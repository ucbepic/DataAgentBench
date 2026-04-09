import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from pathlib import Path
from datetime import datetime
import time
import logging
from openai import AzureOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from dotenv import load_dotenv
from common_scaffold.prompts import prompt_builder
from common_scaffold.tools.BaseTool import BaseTool
from common_scaffold.tools.ExecTool import ExecTool
from common_scaffold.tools.ListDBTool import ListDBTool
from common_scaffold.tools.QueryDBTool import QueryDBTool
from common_scaffold.tools.ReturnAnswerTool import ReturnAnswerTool
from common_scaffold.validate.validate import validate


SUCCESS_TOOL_RESULT_TMPL = """
The tool {tool_name} was executed successfully.

The result is stored under key:
{result_key}

The result is:
{tool_result}
"""

SUCCESS_TOOL_PREVIEW_TMPL = """
The tool {tool_name} was executed successfully.

The result is too large, so it is stored in a file. The file path is stored under key: 
{result_key}

The preview (first {preview_length} characters) of the result is:
{tool_result_preview}
"""

FAIL_TOOL_RESULT_TMPL = """
The tool {tool_name} execution failed. The error message is:
{tool_result}
"""

FAIL_TOOL_PREVIEW_TMPL = """
The tool {tool_name} execution failed. The error message is:
{tool_result_preview}
... (too long, truncated)
"""


class DataAgent:
    def __init__(
            self, 
            query_dir: Path, 
            db_description: str, 
            db_config_path: str, 
            deployment_name: str,
            exec_python_timeout: int = 600,
            max_iterations: int = 100,
            root_name: str = datetime.now().strftime("%Y%m%d_%H%M%S"),
        ):
        self.logger = logging.getLogger(__name__)

        # Load query
        self.query_dir = query_dir
        self.logger.info(f"Loading query from {self.query_dir}...")

        # Initialize OpenAI client
        self.logger.info("🤖 Initializing Agent...")
        self.max_iterations = max_iterations
        self.logger.info(f"\tmax_iterations: {self.max_iterations}")
        self.llm_call_count = 0
        load_dotenv()
        
        if "/" in deployment_name:
            self.client = OpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            )
        elif "gpt" in deployment_name.lower():
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_API_KEY"),
                api_version=os.getenv("AZURE_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_API_BASE")
            )
        elif "gemini" in deployment_name.lower():
            self.client = OpenAI(
                api_key=os.getenv("GEMINI_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
        elif "kimi" in deployment_name.lower() or "qwen" in deployment_name.lower():
            self.client = OpenAI(
                api_key=os.getenv("TOGETHER_API_KEY"),
                base_url="https://api.together.xyz/v1",
            )
        elif "claude" in deployment_name.lower():
            self.client = OpenAI(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                base_url="https://api.anthropic.com/v1",
            )
        else:
            raise ValueError(f"Unsupported deployment name: {deployment_name}")
        self.deployment_name = deployment_name
        self.logger.info(f"\tdeployment: {self.deployment_name}")

        # Initialize agent storage
        self.root_dir = query_dir / "logs" / "data_agent" / root_name
        assert not self.root_dir.exists(), f"Run directory already exists: {self.root_dir}"
        os.makedirs(self.root_dir, exist_ok=True)
        self.exec_tool_work_dir = self.root_dir / "exec_tool_work_dir"
        os.makedirs(self.exec_tool_work_dir, exist_ok=True)
        self.file_storage_dir = self.exec_tool_work_dir / "file_storage" # store large intermediate results
        os.makedirs(self.file_storage_dir, exist_ok=True)
        self.logger.info(f"\tfile_storage: {self.file_storage_dir}")


        # Initialize agent logs
        self.llm_log_path = self.root_dir / "llm_calls.jsonl"
        self.logger.info(f"\tlog: {self.llm_log_path}")
        self.validation_log_path = self.root_dir / "validation.jsonl"
        self.tool_log_path = self.root_dir / "tool_calls.jsonl"


        # Initialize messages
        with open(query_dir / "query.json", 'r', encoding="utf-8") as f:
            query_info = json.load(f)
        if isinstance(query_info, str):
            user_query = query_info
        elif isinstance(query_info, dict) and "query" in query_info:
            user_query = query_info["query"]
        else:
            raise ValueError(f"Unrecognized query.json format: {query_info}")
        self.messages = prompt_builder.init_messages(
            user_query=user_query,
            db_description=db_description,
            deployment_name=deployment_name,
        )
        self.final_result = None
        self.terminate_reason = None

        # Register tools
        self.tools: dict[str, BaseTool] = {
            "query_db": QueryDBTool(
                log_path=self.tool_log_path,
                name="query_db", # the name must equal the key in tools_spec, and this is used for tool spec provided to LLMs
                db_config_path=db_config_path,
                check_load=True,
            ),
            "list_db": ListDBTool(
                log_path=self.tool_log_path,
                name="list_db",
                db_config_path=db_config_path,
                check_load=False,
            ),
            "execute_python": ExecTool(
                log_path=self.tool_log_path,
                name="execute_python",
                work_dir=self.exec_tool_work_dir,
                timeout=exec_python_timeout,
            ),
            "return_answer": ReturnAnswerTool(
                log_path=self.tool_log_path,
                name="return_answer",
            )
        }

        # Initialize storage for intermediate results
        self.result_storage = dict()

    def to_dict(self):
        return {
            # result
            "final_result": self.final_result,
            "terminate_reason": self.terminate_reason,
            # trace
            "messages": self.messages,
            "result_storage": self.result_storage,
            # costs
            "llm_call_count": self.llm_call_count,
            # tools
            "tools": {name: tool.to_dict() for name, tool in self.tools.items()},
            # params
            "query_dir": str(self.query_dir),
            "max_iterations": self.max_iterations,
            "deployment_name": self.deployment_name,
            "file_storage_dir": str(self.file_storage_dir),
            # logs
            "llm_log_path": str(self.llm_log_path),
            "validation_log_path": str(self.validation_log_path),
            "tool_log_path": str(self.tool_log_path),
        }
        
    def call_llm(self):
        # vllm tool calling: https://docs.vllm.ai/en/v0.6.0/getting_started/examples/openai_chat_completion_client_with_tools.html
        start = time.time()
        response = None
        for attempt in range(3):
            try: 
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=self.messages,
                    tools=[tool.get_spec() for tool in self.tools.values()],
                    timeout=600,
                )
                break
            except Exception as e:
                response = None
                self.terminate_reason = f"llm_response_failed ({type(e).__name__}): {str(e)}"
                time.sleep(80)
        end = time.time()

        if response == None:
            self.final_result = ""
            if self.terminate_reason == None:
                self.terminate_reason = "llm_response_failed"
            self.logger.info(f"🛑 Terminating ({self.terminate_reason})...")
            assert self.final_result != None


        self.llm_call_count += 1

        # Log LLM call
        log_entry = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": start,
            "end_time": end,
            "duration": end - start,
            "model": self.deployment_name,
            "response": response.to_dict() if response is not None else None,
            "messages": self.messages,
        }
        with open(self.llm_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        response_msg = response.choices[0].message if response is not None else None
        if response_msg != None:
            self.logger.debug(f"\n{'-' * 10}\nLLM response message:\n{response_msg.to_dict()}\n{'-' * 10}\n")
        
        return response_msg

    def _handle_tool_call(self, tool_call: ChatCompletionMessageToolCall):
        """Agent error-safe tool call handler."""
        self.logger.debug(f"🤖 tool_call: {tool_call.model_dump()}")

        
        tool_name = tool_call.function.name
        try:
            tool_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            self.logger.info(f"🔧 Tool {tool_name} arguments JSON decode error: {e}")
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": FAIL_TOOL_RESULT_TMPL.replace("{tool_name}", tool_name).replace("{tool_result}", f"Arguments JSON decode error ({type(e).__name__}): {str(e)}")
            })
            return


        if tool_name not in self.tools:
            self.logger.info(f"🔧 Unknown tool: {tool_name}")
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": FAIL_TOOL_RESULT_TMPL.replace("{tool_name}", tool_name).replace("{tool_result}", "Unknown tool")
            })
            return

        if tool_name == "execute_python":
            # inject env args
            tool_args['env'] = self.result_storage.copy()
        

        exec_result = self.tools[tool_name].exec(tool_args) # {"success": bool, "result": json-serializable}
        if exec_result["success"] == True:
            if tool_name == "return_answer":
                assert self.final_result == None
                self.final_result = tool_args["answer"] if tool_args["answer"] != None else ""
                self.logger.info(f"🛑 Terminating (return_answer)...")
                assert self.final_result != None
                self.terminate_reason = "return_answer"

            result_key = f"var_{tool_call.id}"
            assert result_key not in self.result_storage, f"Result storage key collision: {result_key}"
            serialized_result = json.dumps(exec_result["result"])
            if len(serialized_result) > prompt_builder.PREVIEW_LENGTH:
                # store in file
                file_path = self.file_storage_dir / f"{tool_call.id}.json"
                assert not file_path.exists(), f"File storage path collision: {file_path}"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(exec_result["result"], f, indent=2)
                self.result_storage[result_key] = os.path.join("file_storage", os.path.basename(file_path)) # store relative path
                content = SUCCESS_TOOL_PREVIEW_TMPL.replace("{tool_name}", tool_name).replace("{result_key}", result_key).replace("{preview_length}", str(prompt_builder.PREVIEW_LENGTH)).replace("{tool_result_preview}", serialized_result[:prompt_builder.PREVIEW_LENGTH])
            else:
                # store directly
                self.result_storage[result_key] = exec_result["result"]
                content = SUCCESS_TOOL_RESULT_TMPL.replace("{tool_name}", tool_name).replace("{result_key}", result_key).replace("{tool_result}", serialized_result)
        else:
            serialized_result = json.dumps(exec_result["result"])
            if len(serialized_result) > prompt_builder.PREVIEW_LENGTH:
                content = FAIL_TOOL_PREVIEW_TMPL.replace("{tool_name}", tool_name).replace("{tool_result_preview}", serialized_result[:prompt_builder.PREVIEW_LENGTH])
            else:
                content = FAIL_TOOL_RESULT_TMPL.replace("{tool_name}", tool_name).replace("{tool_result}", serialized_result)
            

        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_name,
            "content": content
        })
    
    def _handle_content(self, content: str):
        self.logger.debug(f"🤖 content: {content}")
        assert self.final_result == None
        self.final_result = content if content != None else ""
        self.logger.info(f"🛑 Terminating (no tool call)...")
        assert self.final_result != None
        self.terminate_reason = "no_tool_call"


    def handle_reponse(self, response_msg: ChatCompletionMessage):
        if response_msg is None:
            return
        
        tool_calls = response_msg.tool_calls

        if tool_calls is None: # fallback to content
            self.messages.append({
                "role": "assistant",
                "content": response_msg.content
            })
            self._handle_content(response_msg.content)
            return
        
        self.messages.append({
            "role": "assistant",
            "tool_calls": [call.model_dump() for call in tool_calls]
        })
        
        for call in tool_calls:
            self._handle_tool_call(call)

        if (self.final_result == None) and (self.llm_call_count >= self.max_iterations):
            self.final_result = ""
            self.logger.info(f"🛑 Terminating (max iterations reached: {self.llm_call_count}/{self.max_iterations})...")
            assert self.final_result != None
            self.terminate_reason = "max_iterations"
    
    # def validate(self):
    #     val_result = validate(
    #         query_dir=self.query_dir,
    #         llm_answer=self.final_result,
    #         reason=self.terminate_reason,
    #     )
    #     with open(self.validation_log_path, "a", encoding="utf-8") as f:
    #         f.write(json.dumps(val_result) + "\n")
    #     return val_result
        
    
    def run(self):
        self.logger.info("🚀 Starting...")
        run_start = time.time()
        try:
            while self.final_result == None:
                response_msg = self.call_llm()
                self.handle_reponse(response_msg)
            run_end = time.time()
            
            assert self.final_result != None
            assert self.llm_call_count <= self.max_iterations
            self.logger.info(f"\tllm_calls:\t{self.llm_call_count}")
            self.logger.info(f"\tfinal_result:\t{self.final_result}")
        except Exception as e:
            run_end = time.time()
            self.final_result = ""
            self.terminate_reason = f"agent_run_failed ({type(e).__name__}): {str(e)}"
            self.logger.info(f"🛑 Terminating ({self.terminate_reason})...")
            assert self.final_result != None

        ## validate final result
        # self.logger.info("🔍 Validating final result...")
        # val_result = self.validate()
        # self.logger.info("✅" if val_result["is_valid"] else "❌")
        # print(f"\tllm:\t{val_result['llm_answer']}")
        # print(f"\ttrue:\t{val_result['ground_truth']}")

        ## log final result
        final_log_entry = {
            # time
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": run_start,
            "end_time": run_end,
            "duration": run_end - run_start,
        }
        final_log_entry.update(self.to_dict())

        with open(self.root_dir / "final_agent.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(final_log_entry, indent=2))

        # clean up tools
        for tool in self.tools.values():
            tool.clean_up()

        # clean file storage
        if os.path.exists(self.file_storage_dir):
            for file_name in os.listdir(self.file_storage_dir):
                file_path = os.path.join(self.file_storage_dir, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        return self.final_result
