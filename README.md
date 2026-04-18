# DAB: Data Agent Benchmark

> 🌐 **Website & Leaderboard: [ucbepic.github.io/DataAgentBench](https://ucbepic.github.io/DataAgentBench/)**

> 📄 **Paper: [arxiv.org/abs/2603.20576](https://arxiv.org/abs/2603.20576)**

> 🔥 **DAB is the first benchmark for evaluating data agents on realistic, complex, data-oriented tasks. It is a collaborative effort between UC Berkeley and Hasura PromptQL.**

> 🤝 **We welcome contributions to the leaderboard!
Submit a Pull Request following the instruction below  to share your agent results and see them ranked on DAB.**

DAB captures **four core properties** of real-world enterprise data workloads across industries:

*  **Multi-database integration**
*  **Ill-formatted key joins**
*  **Unstructured text transformation**
*  **Domain knowledge**

Unlike prior SQL-only or single-database benchmarks, DAB stresses agents under **realistic enterprise data complexity**.


## 🏆 Leaderboard

| Rank | Model          | Pass@1 | Date    |
| ---- | -------------- | ------------------- | ------- |
| 1    | PromptQL (Gemini-3.1-Pro) (5 trials/query) | 0.543                | 2026-03-018 |
| 2    | PromptQL (Claude-Opus-4.6) (5 trials/query) | 0.508                | 2026-03-02 |
| 3    | Claude-Opus-4.6 (5 trials/query) | 0.4376                | 2026-03-18 |
| 4    | Gemini-3-Pro | 0.38           | 2026-03-02 |
| 5    | GPT-5-mini     |     0.30           | 2026-03-02 |
| 6    | GPT-5.2     |     0.25           | 2026-03-02 |
| 7    | Kimi-K2     |     0.23           | 2026-03-02 |
| 8    | Gemini-2.5-Flash     |     0.09          | 2026-03-02 |


### How to Submit to the Leaderboard

To contribute your agent's results to the DAB leaderboard:

1. Collect results from **50 runs** on **all queries** across **all datasets**.
2. Organize all your run results into a *single* JSON file following this structure:

    ```json
    [
      {
        "dataset": "<dataset_name>",   // e.g., "bookreview"
        "query": "<query_id>",         // e.g., "1"
        "run": "<run_number>",         // 0–49 for 50 runs
        "answer": "<agent_generated_answer>"
      },
      ...
      // Include an entry for every run of every query across all datasets
    ]
    ```

3. Submit a **Pull Request** to this repository including:

   * The JSON results file
   * A brief description of your agent configuration, including:

      - The name of your agent

      - Backbone LLM model(s) name and version

      - Whether dataset hints were used

      - Any additional notes or special settings you want to highlight

⚠️ You must include all 50 runs for each query in your dataset. Missing runs may result in your submission being rejected from the leaderboard.


## 📚 Table of Contents

* [📊 Benchmark Overview](#-benchmark-overview)
* [⚙️ Prerequisites](#️-prerequisites)
  * [Clone the Repository](#clone-the-repository)
  * [Install Dependencies](#install-dependencies)
  * [Setup Docker](#setup-docker)
  * [Setup Databases](#setup-databases)
  * [Set Database Configurations](#set-database-configurations)
  * [Add API Credentials](#add-api-credentials)
* [▶️ Run the Benchmark](#️-run-the-benchmark)
  * [Run the Built-in Agent](#run-the-built-in-agent-on-a-single-query)
  * [Run with Knowledge Base (--use_kb)](#run-with-knowledge-base---use_kb)
  * [Execution Logs](#execution-logs)
  * [Validate Agent Answer](#validate-agent-answer)
* [📈 Scoring & Analysis](#-scoring--analysis)
  * [Pass@k Explained](#passk-explained)
  * [Score Local Runs (accuracy.py)](#score-local-runs-accuracypy)
  * [Score benchmark results (avg_accuracy.py)](#score-benchmark-results-avg_accuracypy)
* [📝 Datasets and Queries](#-datasets-and-queries)
  * [Dataset](#dataset)
  * [Query](#query)
* [🤖 Create Your Customized Agents](#-create-your-customized-agents)


## 📊 Benchmark Overview


This benchmark contains **12** datasets and **54** queries across **9** domains and **4** DBMSes:

| Dataset          | #DBs | DBMSes                     | #Tbl | #Queries |
| ---------------- | ---- | -------------------------- | ---- | -------- |
| agnews           | 2    | MongoDB, SQLite            | 3    | 4        |
| bookreview       | 2    | PostgreSQL, SQLite         | 2    | 3        |
| crmarenapro      | 6    | DuckDB, PostgreSQL, SQLite | 27   | 13       |
| deps_dev_v1      | 2    | DuckDB, SQLite             | 3    | 2        |
| github_repos     | 2    | DuckDB, SQLite             | 6    | 4        |
| googlelocal      | 2    | PostgreSQL, SQLite         | 2    | 4        |
| music_brainz_20k | 2    | DuckDB, SQLite             | 2    | 3        |
| pancancer_atlas  | 2    | DuckDB, PostgreSQL         | 3    | 3        |
| patents          | 2    | PostgreSQL, SQLite         | 2    | 3        |
| stockindex       | 2    | DuckDB, SQLite             | 2    | 3        |
| stockmarket      | 2    | DuckDB, SQLite             | 2754 | 5        |
| yelp             | 2    | DuckDB, MongoDB            | 5    | 7        |





## ⚙️ Prerequisites

Before running DAB, please complete the following setup steps.

### Clone the Repository

Some datasets in DAB contain large database files exceeding 50MB and are thus stored in Git LFS. To automatically get the full datasets, you need to ensure you have Git LFS enabled:
```bash
git lfs install
```
Then you can run:
```bash
git clone https://github.com/ucbepic/DataAgentBench.git
cd DataAgentBench
```
One database file of `PATENTS` dataset, `patent_publication.db`, exceeds Git LFS file-size limits (5GB). It is on [google drive](https://drive.google.com/file/d/1pALQ1UH-OwaEUeGYAx47uCyzClfK94XC/view?usp=sharing).

**Option 1:**
Manually download the database to `query_PATENTS/query_dataset/patent_publication.db`

**Option 2:**
Run the following script to automatically download the database:
```bash
bash download.sh
```


### Install Dependencies

We recommend using a dedicated virtual environment to ensure reproducibility.

**Using Conda (recommended):**

```bash
conda env create -f environment.yaml
conda activate dabench
```

This will install all required dependencies specified in [environment.yaml](./environment.yaml).


<!-- ## 🐳  -->
### Setup Docker

- **Install Docker**
   Follow the [official guide](https://www.docker.com/get-started/).

    Version used in our experiments: **28.4.0**

- **Build the Docker image**:
  The image includes **Python 3.12**, **Pandas**, and **PyArrow** pre-installed:

    ```bash
    docker build -t python-data:3.12 .
    ```

### Setup Databases

DAB evaluates agents across multiple database systems, so you must install and configure the following databases locally.
- **PostgreSQL**: 
  Install PostgreSQL from the [official website](https://www.postgresql.org/) and start the server.
  - **Minimum required version**: 17.5
  - Version used in our experiments: 17.7 (Ubuntu 17.7-3.pgdg24.04+1)
- **MongoDB**:
  Install MongoDB Community Edition from the [official website](https://www.mongodb.com/) and start the server.
  - Version used in our experiments: v8.2.1
- **SQLite & DuckDB**: 
  They operate directly on database files and do not require running a server.

### Set Database Configurations

After installing all databases, you need to configure connection parameters to match your local setup.

Default configuration values (defined in [db_config.py](./common_scaffold/tools/db_utils/)):

|**Parameter**|**Default value**|
|:-:|:-:|
|PG_CLIENT | "psql" |
| PG_HOST | "127.0.0.1" |
| PG_PORT | 5432 |
| PG_USER | "postgres" |
| PG_PASSWORD | "" |
| PG_DB | "test" |
| MONGO_URI | "mongodb://localhost:27017/" |
| SQLITE_PATH | "data/mydb.sqlite" |
| DUCKDB_PATH | "data/mydb.duckdb" |

**Option 1**:
Create a `.env` file in the project root. E.g.,

```
# PostgreSQL
PG_PASSWORD=your_password
PG_DB=mydb
# MongoDB (if authentication is required)
MONGO_URI=mongodb://username:password@localhost:27017/?authSource=admin
```

**Option 2**: 
Modifying the defaults in [db_config.py](./common_scaffold/tools/db_utils/).




### Add API credentials
Create a `.env` file in the project root and add your API keys:

```
AZURE_API_BASE=
AZURE_API_KEY=
AZURE_API_VERSION=
GEMINI_API_KEY=
TOGETHER_API_KEY=
```

Currently, we support 
- Microsoft Azure API (for GPT models)
- Google Gemini API (for Gemini models)
- Together.AI API (for Kimi and Qwen models)

If you want to use a model not yet supported by default, you may register it in [DataAgent.py](./common_scaffold/DataAgent.py):
```python
# DataAgent.py (from line 76)
if "gpt" in deployment_name.lower():
      self.client = AzureOpenAI(
          api_key=os.getenv("AZURE_API_KEY"),
          api_version=os.getenv("AZURE_API_VERSION"),
          azure_endpoint=os.getenv("AZURE_API_BASE")
      )
  # add a new model here as an `elif` branch
  else:
      raise ValueError(f"Unsupported deployment name: {deployment_name}")
```
and a customized prompt to adapt to the format of your model's tool call ID in [prompt_builder.py](./common_scaffold/prompts/prompt_builder.py).

## ▶️ Run the Benchmark

### Run the Built-in Agent on a Single Query

DAB comes with a built-in agent. You can run the agent on a specific query as follow:

**Example:** Run a single trial of GPT-5-mini on `query1` of the `bookreview` dataset, with up to 100 agent iterations and dataset hints enabled:

```bash
python run_agent.py \
    --dataset bookreview \
    --query_id 1 \
    --llm gpt-5-mini \
    --iterations 100 \
    --use_hints \
    --root_name run_0
```


### Run with Knowledge Base (`--use_kb`)

The agent can load context from the [oracle-forge KB](../oracle-forge-data-agent/kb/) at session start — corrections from past failures, join key rules, and column semantics — to avoid repeating known mistakes.

**Prerequisites:** set `ORACLE_FORGE_KB_DIR` in `.env` or pass `--kb_dir` explicitly:

```bash
# .env
ORACLE_FORGE_KB_DIR=../oracle-forge-data-agent/kb
```

**Single run with KB context:**

```bash
python run_agent.py \
    --dataset yelp \
    --query_id 3 \
    --llm claude-sonnet-4-6 \
    --use_kb
```

**Multi-pass self-correction** — on failure the agent writes a correction entry to the KB and retries with it loaded:

```bash
python run_agent.py \
    --dataset yelp \
    --query_id 3 \
    --llm claude-sonnet-4-6 \
    --use_kb \
    --max_passes 3
```

Each pass is saved as a separate run directory (`run_0`, `run_0_pass2`, `run_0_pass3`). Corrections are appended to `kb/corrections/log.md` between passes and reloaded before each retry.

> Only content relevant to the target dataset is injected — corrections, join keys, and schemas are filtered by dataset tag to keep the context window lean.

### Execution Logs

Logs for this run will be saved under:

```
query_bookreview/query1/logs/data_agent/run_0
```

The log directory has the following structure:

```
run_0/
├─ exec_tool_work_dir/     <- Working directory for the `execute_python` tool (Docker)
├─ final_agent.json        <- Full agent trajectory and execution statistics
├─ llm_calls.jsonl         <- All LLM API calls made by the agent
└─ tool_calls.jsonl        <- All tool calls made by the agent
```

### Validate Agent Answer


DAB provides utilities to compute both **aggregated Pass@1 accuracy of a dataset** and  **single-run correctness**.

####  Compute Pass@1 (50 Runs)

We provide a script [`avg_accuracy.py`](./python_script/) to compute **Pass@1 accuracy** across **50 runs per query** of a dataset.

Before running the script, make sure your run logs are organized under the following directory structure (you may need to first move them from the dataset folder to the `results-<model_name>/` directory):

```
results-gpt-5-mini/
└─ query_bookreview/
   └─ query1/
      └─ data_agent/
         ├─ run_0/
         ├─ run_1/
         ├─ ...
         └─ run_49/
```

Then compute Pass@1 as follows:

```python
from python_script.avg_accuracy import avg_acc

print(avg_acc("bookreview", "gpt-5-mini"))
```

This will aggregate validation results across runs and queries and report the final Pass@1 accuracy for the dataset.


#### Validate a Single Run

After an agent run completes, you can validate its final answer against the ground truth:

```python
from pathlib import Path
import json

run_dir = Path("query_bookreview/query1/logs/data_agent/run_0")

with open(run_dir / "final_agent.json", encoding="utf-8") as f:
    llm_json = json.load(f)

llm_answer = llm_json["final_result"]
term_reason = llm_json["terminate_reason"]

if term_reason == "no_tool_call":
    validation_result = {"is_valid": False}
else:
    validation_result = validate(query_dir, llm_answer, term_reason)
```

The validation result follows this structure:

```python
{
  "timestamp": "YYYYMMDD_HHMMSS",
  "query_name": "query1",
  "is_valid": True/False,   # Whether the agent’s answer matches the ground truth
  "reason": "...",          # Explanation for success or failure
  "ground_truth": "...",    # The ground-truth answer
  "llm_answer": "...",      # The agent's final answer
}
```


## 📈 Scoring & Analysis

### Pass@k Explained

Pass@k measures the probability that at least one of k independent runs returns the correct answer:

| Metric | Meaning |
|--------|---------|
| **pass@1** | Single-run accuracy — the fraction of runs that are correct |
| **pass@5** | Probability of getting the right answer in 5 tries |
| **pass@50** | Upper bound — are any of 50 runs correct? |

DAB uses **pass@1** as the primary leaderboard metric computed over 50 trials per query. During development, 5 trials is sufficient for quick iteration.

### Score Local Runs (`accuracy.py`)

[`stats_scripts/accuracy.py`](stats_scripts/accuracy.py) scans your local `query_*/query{N}/logs/data_agent/` directories, discovers all completed runs, validates each against ground truth, and prints per-query pass@k scores.

**Run from the repo root — no arguments needed:**

```bash
python stats_scripts/accuracy.py
```

**Example output:**

```
yelp/query1  model=claude-sonnet-4-6  runs=5  correct=3/5  pass@1=0.6000  reasons={'return_answer': 5}
yelp/query2  model=claude-sonnet-4-6  runs=5  correct=2/5  pass@1=0.4000  reasons={'return_answer': 4, 'max_iterations': 1}
bookreview/query1  model=claude-sonnet-4-6  runs=5  correct=5/5  pass@1=1.0000  reasons={'return_answer': 5}
```

Each line reports: dataset/query, model, run count, correct count, pass@1, and how runs terminated. `max_iterations` in `reasons` means the agent hit the iteration cap without returning an answer — a signal to investigate.

**Check a single query:**

```python
from pathlib import Path
from stats_scripts.accuracy import pass_k_per_query, discover_runs

query_dir = Path("query_yelp/query3")
result_dir = query_dir / "logs" / "data_agent"

runs = discover_runs(result_dir)
correct, passk, reasons = pass_k_per_query(query_dir, result_dir, runs)

print(f"Correct: {correct}/{len(runs)}")
print(f"pass@1:  {passk['pass@1']:.4f}")
print(f"pass@5:  {passk.get('pass@5', 'n/a')}")
```

**Validate a single completed run:**

```bash
python failure_analysis/check_run.py --dataset yelp --query_id 3 --run_name run_0
```

This prints PASS/FAIL with the agent answer and ground truth side by side. On failure, add `--use_kb` to save a draft correction for IO review:

```bash
python failure_analysis/check_run.py --dataset yelp --query_id 3 --run_name run_0 --use_kb
```

See [`failure_analysis/README.md`](failure_analysis/README.md) for the full correction workflow.

### Score benchmark results (`avg_accuracy.py`)

[`stats_scripts/avg_accuracy.py`](stats_scripts/avg_accuracy.py) computes dataset-level pass@1 averaged across all queries, designed for the upstream benchmark submission structure (`results-{model}/`).

Organize 50 runs per query under:

```
results-<model>/
└─ query_<dataset>/
   └─ query<N>/
      └─ data_agent/
         ├─ run_0/
         ├─ run_1/
         ├─ ...
         └─ run_49/
```

Then call:

```python
from stats_scripts.avg_accuracy import avg_acc

score = avg_acc("yelp", "claude-sonnet-4-6")
print(f"yelp pass@1: {score:.4f}")
```

Or run the script directly to print a CSV table across all datasets and models defined in the file.

> Use `accuracy.py` during development (reads from local `logs/` dirs). Use `avg_accuracy.py` when preparing a leaderboard submission (reads from `results-{model}/`).

## 📝 Datasets and Queries

<!-- ⚠️ To add a new dataset to DAB, you **must strictly follow the prescribed dataset and query folder structures** described above. This ensures that the benchmark can automatically locate databases, queries, and validation scripts. -->

<!-- After creating your dataset:

1. Verify that it runs correctly with the built-in agent.
2. Ensure all queries include `query.json`, `ground_truth.csv`, and `validate.py`.
3. Confirm database configurations are properly defined in `db_config.yaml`.

Once ready, please submit a **pull request** to our GitHub repository for review.

We welcome high-quality, realistic datasets that reflect complex enterprise data scenarios. -->


### Dataset

A dataset in DAB is organized as a folder under the project root. For example, for dataset `bookreview`:

```
query_bookreview/
├─ query_dataset/                  <- All database files
│  ├─ books_info.sql
│  └─ review_query.db
├─ query1/                         <- Each query stored in a separate folder
├─ db_config.yaml                   <- Database connection configuration
├─ db_description.txt               <- Description of the database schemas
└─ db_description_with_hint.txt     <- Optional hints for queries
```

<!-- Make sure you use the supported database formats: **PostgreSQL**， **MongoDB**, **SQLite**, or **DuckDB**.  -->

### Query

Each query is stored within its corresponding dataset folder:

```
query_1/
├─ query.json           <- The query as a double-quoted string
├─ ground_truth.csv     <- The ground-truth answer in plain text
└─ validate.py          <- Python script to validate an agent's output
```

`validate.py` defines a `validate` function with the following signature:

```python
def validate(llm_output: str):
    """
    Validate if the ground truth is present in the agent's answer.

    Returns:
        (True, "OK")   – if the answer matches the ground-truth
        (False, reason) – if it does not match
    """
```


## 🤖 Create Your Customized Agents

DAB allows you to **implement and run your own agents** while leveraging built-in tools for database querying and Python execution. These utilities, located under [`tools/`](./common_scaffold/tools/), provide:

* **🔗 Automatic Database Connection**

  * Loads database configurations from `db_config.yaml` for each dataset.
  * No need to manually connect to PostgreSQL, MySQL, MongoDB, SQLite, or DuckDB — all connections are handled automatically via [`db_utils`](./common_scaffold/tools/db_utils/).

* **🛡️ Read-only Database Querying**

  * Ensures queries are read-only, preventing accidental writes that could pollute the data.

* **🐳 Safe Python Execution Environment**

  * Executes Python code with a 600-second timeout in a Docker environment with Python 3.12, `pandas`, and `pyarrow` pre-installed.
  * Protects your local machine from unsafe operations by the agent.

* **📄 Agent Reference Implementation**

  * [`DataAgent.py`](./common_scaffold/DataAgent.py) is a fully functional built-in agent.
  * Use it as a template to implement and test your own agent.

## 📖 Citation

If you use DAB in your research, please cite our paper:

```bibtex
@article{ma2025dab,
  title={DAB: Data Agent Benchmark},
  author={Ma, Ruiying and Shankar, Shreya and Chen, Ruiqi and Lin, Yiming and Zeighami, Sepanta and Ghosh, Rajoshi and Gupta, Abhinav and Gupta, Anushrut and Gopal, Tanmai and Parameswaran, Aditya G.},
  journal={arXiv preprint arXiv:2603.20576},
  year={2025}
}
```

