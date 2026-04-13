from common_scaffold.tools.BaseTool import BaseTool, FatalError
from common_scaffold.tools.exec_utils.parse_result import parse_result_python
import asyncio
from pathlib import Path

from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
import logging
import os
import json


def _unlink_tmp_code_scripts(work_dir: Path, logger: logging.Logger) -> None:
    """Remove DockerCommandLineCodeExecutor temp scripts (tmp_code_<hash>.py) from work_dir."""
    try:
        if not work_dir.is_dir():
            return
        for path in work_dir.glob("tmp_code_*.py"):
            try:
                path.unlink(missing_ok=True)
            except OSError as e:
                logger.debug("Could not remove %s: %s", path, e)
    except OSError as e:
        logger.debug("tmp_code cleanup skipped: %s", e)


class ExecTool(BaseTool):
    """
    A robust, synchronous interface around AutoGen's DockerCommandLineCodeExecutor.
    Each call supports a timeout and automatically restarts the container if a command hangs.
    
    The returned format of DeckExecutorResult is:
    - exit_code = 0, 
    - output = std_out + std_err,
    - code_file = working_dir / file_name)
    """

    def __init__(self, log_path, name, work_dir: Path, timeout=600):
        super().__init__(log_path, name)
        self.logger = logging.getLogger(__name__)
        self.work_dir = work_dir
        self.logger.info(f"\twork_dir: {self.work_dir}")
        self.timeout = timeout
        self.logger.info(f"\ttimeout: {self.timeout} seconds")
        self.artifact_log_path = os.path.join(os.path.dirname(self.log_path), f"{name}_artifacts.jsonl")
        self.logger.info(f"\tartifact_log: {self.artifact_log_path}")

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._executor = None
        self._start_executor()
    
    def to_dict(self):
        return super().to_dict().update({
            "work_dir": str(self.work_dir),
            "timeout": self.timeout,
            "artifact_log_path": self.artifact_log_path,
        })

    def get_spec(self):
        spec = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": (
                    """Execute a Python snippet. All previous tool results are available as variables. You must print the final result following the required PRINT FORMAT."""
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": (
                                "Python code to execute in the context of already loaded previous tool results."
                            )
                        }
                    },
                    "required": ["code"]
                }
            }
        }
        return spec


    # ---------------------------------------------------------
    # Internal executor management
    # ---------------------------------------------------------

    def _start_executor(self):
        """Start a fresh docker executor."""
        self.logger.debug("Starting Docker executor...")
        self._executor = DockerCommandLineCodeExecutor(
            image="python-data:3.12",
            work_dir=self.work_dir,
        )
        self._loop.run_until_complete(self._executor.start())

    def _stop_executor(self):
        """Stop the container if running."""
        self.logger.debug("Stopping Docker executor...")
        try:
            self._loop.run_until_complete(self._executor.stop())
        except Exception as e:
            self.logger.critical(f"Failed to stop executor cleanly: {str(e)}")
            pass

    def _restart_executor(self):
        """Safely restart container after a timeout or crash."""
        self._stop_executor()
        self._start_executor()

    # ---------------------------------------------------------
    # Async helpers
    # ---------------------------------------------------------

    async def _run_inside(self, blocks):
        """Low-level helper to run code blocks asynchronously."""
        return await self._executor.execute_code_blocks(
            blocks,
            cancellation_token=CancellationToken(),
        )

    # ---------------------------------------------------------
    # Public sync API
    # ---------------------------------------------------------

    def run_python(self, code: str):
        """Run Python code in the persistent container, with timeout."""
        return self._run_with_timeout(
            [CodeBlock(language="py", code=code)]
        )

    def run_shell(self, code: str):
        """Run shell commands in the persistent container, with timeout."""
        return self._run_with_timeout(
            [CodeBlock(language="sh", code=code)]
        )

    # ---------------------------------------------------------
    # Timeout + restart wrapper
    # ---------------------------------------------------------

    def _run_with_timeout(self, blocks):
        try:
            return self._loop.run_until_complete(
                asyncio.wait_for(
                    self._run_inside(blocks),
                    timeout=self.timeout,
                )
            )
        except asyncio.TimeoutError:
            # Kill container + restart
            # This will never happen, due to DockerCommandLineCodeExecutor's inner implementation
            self._restart_executor()
            raise TimeoutError(f"Execution timed out after {self.timeout} seconds")
        except Exception as e:
            raise FatalError(f"Execution failed: {str(e)}")

    # ---------------------------------------------------------
    # Manual clean shutdown
    # ---------------------------------------------------------

    def close(self):
        """Explicit shutdown method."""
        self._stop_executor()
        _unlink_tmp_code_scripts(self.work_dir, self.logger)
        self._loop.stop()
        self._loop.close()

    
    def clean_up(self):
        super().clean_up()
        self.close()


    def _check_args(self, args):
        super()._check_args(args)
        # Require either `code` (from agent) + `env` (from engineer) or `command`
        if "code" in args:
            if not isinstance(args["code"], str):
                raise ValueError(f"`code` must be a string, got {type(args['code']).__name__}")
            if "env" not in args:
                raise FatalError("Missing required argument: env")
            if not isinstance(args["env"], dict):
                raise FatalError(f"`env` must be a dict, got {type(args['env']).__name__}")
            return {
                "code": args["code"].strip(),
                "env": args["env"],
            }
        elif "command" in args:
            if not isinstance(args["command"], str):
                raise ValueError(f"`command` must be a string, got {type(args['command']).__name__}")
            return {
                "command": args["command"].strip()
            }
        else:
            raise ValueError("Invalid argument")
    
    def _exec(self, args):
        super()._exec(args)
        try:
            if "code" in args:
                env_args = args["env"]
                exec_str = f'''code = """{args["code"]}"""\n\nenv_args = {env_args}\n\nexec(code, env_args)\n'''
                result = self.run_python(exec_str)
            elif "command" in args:
                result = self.run_shell(args["command"])
            else:
                raise FatalError("Invalid argument")

            self.logger.debug(f"ExecTool execution result: {result}")
            # Log artifact
            artifact_entry = {"val_args": args}
            try:
                artifact_entry['exit_code'] = result.exit_code
            except Exception:
                raise FatalError("Execution did not return an exit code")
            try:
                artifact_entry['output'] = result.output
            except Exception:
                raise FatalError("Execution did not return output")
            try:
                artifact_entry['code_file'] = str(result.code_file)
            except Exception:
                raise FatalError("Execution did not return code file")
            with open(self.artifact_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(artifact_entry) + "\n")

            if result.exit_code != 0:
                # Handle timeout case separately
                if "code execution was cancelled" in result.output.lower():
                    raise TimeoutError(f"Execution timed out after {self.timeout} seconds")
                try:
                    clean_err = result.output.strip().splitlines()[-1]
                except Exception:
                    clean_err = result.output
                raise ValueError(f"Execution failed with exit code {result.exit_code}\n{clean_err}")
            if "code" in args:
                parsed_output = parse_result_python(result.output)
                self.logger.debug(f"Parsed ExecTool output: {parsed_output}")
                return parsed_output
            return result.output
        finally:
            _unlink_tmp_code_scripts(self.work_dir, self.logger)
