#!/usr/bin/env python3
"""Shared trial harness for the DAB deterministic pipeline (dab-agent-02 side).

A solver module defines:
  DATASET, QUERY_TEXTS (dict qid->question), STEPS (dict qid->list of (label, code)),
  DERIVATION (dict qid->short derivation string), ANSWER (dict qid->answer string).

run_trials() executes every query's step list in a fresh namespace (capturing
stdout per step), formats trace files compatible with the strict-baseline layout,
and writes traces/<dataset>/queryN/tR/{final_agent.json,tool_calls.jsonl}.
Answers are recomputed by the executed code itself (namespace['ANSWER']).
"""
import contextlib, io, json, os, sys

def run_query_steps(steps):
    ns = {}
    per_step = []
    for i, (label, code) in enumerate(steps):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(code, f"<step{i}:{label}>", "exec"), ns)
            rc = 0
        except Exception:
            import traceback
            buf.write(traceback.format_exc())
            rc = 1
        per_step.append({"label": label, "code": code, "stdout": buf.getvalue(), "returncode": rc})
        if rc:
            raise RuntimeError(f"step {i} ({label}) failed:\n{buf.getvalue()}")
    ans = ns.get("ANSWER")
    if not isinstance(ans, str):
        raise RuntimeError("solver did not set ANSWER (str)")
    return per_step, ans

def write_trace(outdir, question, steps_out, answer, derivation, agent):
    calls = []
    messages = [{"role": "user", "content": question}]
    for i, st in enumerate(steps_out):
        cid = f"call_{i:02d}"
        messages.append({"role": "assistant", "content": [
            {"type": "tool_use", "id": cid, "name": "run_python", "input": {"code": st["code"]}}]})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": cid, "content": st["stdout"]}]})
        calls.append({"iteration": i, "tool_use_id": cid, "name": "run_python",
                      "input": {"code": st["code"]},
                      "result": {"stdout": st["stdout"], "returncode": st["returncode"]}})
    rid = f"call_{len(steps_out):02d}"
    messages.append({"role": "assistant", "content": [
        {"type": "tool_use", "id": rid, "name": "return_answer", "input": {"answer": answer}}]})
    calls.append({"iteration": len(steps_out), "tool_use_id": rid, "name": "return_answer",
                  "input": {"answer": answer}, "result": {"submitted": True}})
    final = {"final_result": answer, "terminate_reason": "return_answer", "messages": messages,
             "llm_call_count": 0, "tool_call_count": len(steps_out) + 1, "duration": 0.0,
             "model": None, "agent": agent, "derivation": derivation}
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "tool_calls.jsonl"), "w") as f:
        for c in calls:
            f.write(json.dumps(c) + "\n")
    with open(os.path.join(outdir, "final_agent.json"), "w") as f:
        json.dump(final, f, indent=1)
    return len(calls)

def run_trials(mod, traces_root, n_runs=5, only=None):
    """Execute every query n_runs times; return {qid: answer} (assert identical across runs)."""
    answers = {}
    for qid, qtext in sorted(mod.QUERY_TEXTS.items(), key=lambda kv: int(kv[0])):
        if only and qid not in only:
            continue
        runs = []
        for r in range(n_runs):
            steps_out, ans = run_query_steps(mod.STEPS[qid])
            runs.append(ans)
            write_trace(os.path.join(traces_root, mod.DATASET, f"query{qid}", f"t{r}"),
                        qtext, steps_out, ans, mod.DERIVATION[qid], mod.AGENT)
        if len(set(runs)) != 1:
            raise RuntimeError(f"{mod.DATASET} q{qid}: non-deterministic across runs: {set(runs)}")
        answers[qid] = runs[0]
        print(f"{mod.DATASET} q{qid}: {len(runs)} trials, answer deterministic")
    return answers
