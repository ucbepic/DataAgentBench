import utils.net
import utils.clients
import utils.http_session
import utils.transport
import utils.session
import asyncio
from pathlib import Path

from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

async def main():
    work_dir = Path("coding")
    work_dir.mkdir(exist_ok=True)

    async with DockerCommandLineCodeExecutor(
        image="python-data:3.12",    # optional; matches your earlier code
        work_dir=work_dir,
        
    ) as executor:
        code_blocks = [
                CodeBlock(
                    language="py",
                    code="""
import pandas as pd
data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]}
df = pd.DataFrame(data)
df.to_parquet('output.parquet', engine='pyarrow', index=False)"""
                ),
                CodeBlock(
                    language="sh",
                    code="ls"
                ),
                CodeBlock(
                    language="py",
                    code="""
import pandas as pd
df = pd.read_parquet('output.parquet', engine='pyarrow')
print(df)"""
                ),

            ]
        for code_block in code_blocks:
            print(f"--- Executing code ---")
            result = await executor.execute_code_blocks(
                code_blocks=[code_block],
                cancellation_token=CancellationToken()
            )

            print(result)

if __name__ == "__main__":
    asyncio.run(main())