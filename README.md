# DAB: Data Agent Benchmark


> 🌐 **Website & Leaderboard: [ucbepic.github.io/DataAgentBench](https://ucbepic.github.io/DataAgentBench/)**
>
> 📄 **Paper: [arxiv.org/abs/2603.20576](https://arxiv.org/abs/2603.20576)**
>
> 🔥 **DAB is the first benchmark for evaluating data agents on realistic, complex, data-oriented tasks. It is a collaborative effort between UC Berkeley and Hasura PromptQL.**
>
> 🤝 **We welcome contributions to the leaderboard!
Submit a Pull Request following the [instructions below](#how-to-submit-to-the-leaderboard) to share your agent results and see them ranked on DAB.**



DAB captures **four core properties** of real-world enterprise data workloads across industries:

*  **Multi-database integration**
*  **Ill-formatted key joins**
*  **Unstructured text transformation**
*  **Domain knowledge**

Unlike prior SQL-only or single-database benchmarks, DAB stresses agents under **realistic enterprise data complexity**.

<p align="center"><img src="docs/logo.png" width="300"/></p>



## 🏆 Leaderboard

<sub>**Tuned prompt** ✓ = the up-front prompt is DAB-specific, built from a close study of DAB's task conventions (domain rules, parsing and interpretation choices, and expected answer shapes).</sub>

<sub>**Hints** ✓ = used `db_description_withhint.txt`.</sub>

| <sub>Rank</sub> | <sub>Model</sub> | <sub>Tuned prompt</sub> | <sub>Pass@1 ¹</sub> | <sub>Trials</sub> | <sub>Hints</sub> | <sub>Date</sub> | <sub>Submission</sub> |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <sub>1</sub> | <sub>Camber (Claude-Opus-5, high effort)</sub> | <sub>✓</sub> | <sub>0.8790</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-08-27</sub> | <sub>[#92](https://github.com/ucbepic/DataAgentBench/pull/92)</sub> |
| <sub>2</sub> | <sub>Permute EQ (Claude-Opus-5)</sub> | <sub>✓</sub> | <sub>0.8713</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-08-18</sub> | <sub>[#88](https://github.com/ucbepic/DataAgentBench/pull/88)</sub> |
| <sub>3</sub> | <sub>Sentinel (Actioneer) (Fable-5 + Claude-Opus-4.7)</sub> | <sub>✓</sub> | <sub>0.8617</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-07-20</sub> | <sub>[#73](https://github.com/ucbepic/DataAgentBench/pull/73)</sub> |
| <sub>4</sub> | <sub>Permute Core (Claude-Opus-5)</sub> | <sub>✓</sub> | <sub>0.8413</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-08-05</sub> | <sub>[#85](https://github.com/ucbepic/DataAgentBench/pull/85)</sub> |
| <sub>5</sub> | <sub>Alkera (Fable-5 + Claude-Opus-4.8)</sub> | <sub>✓</sub> | <sub>0.8411</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-07-14</sub> | <sub>[#70](https://github.com/ucbepic/DataAgentBench/pull/70)</sub> |
| <sub>6</sub> | <sub>Sarvam Code v0.36 (GLM-5.2)</sub> | <sub>✓</sub> | <sub>0.8208</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-07-28</sub> | <sub>[#75](https://github.com/ucbepic/DataAgentBench/pull/75)</sub> |
| <sub>7</sub> | <sub>SCRIBE (Actioneer) (Claude-Opus-4.7)</sub> | <sub>✓</sub> | <sub>0.8185</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-06-26</sub> | <sub>[#67](https://github.com/ucbepic/DataAgentBench/pull/67)</sub> |
| <sub>8</sub> | <sub>Alkera (Claude-Opus-4.8)</sub> | <sub>✓</sub> | <sub>0.8044</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-07-15</sub> | <sub>[#69](https://github.com/ucbepic/DataAgentBench/pull/69)</sub> |
| <sub>9</sub> | <sub>LabRat (Claude-Opus-5 + Cartographer) ⁶</sub> | <sub>✓</sub> | <sub>0.8018</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-08-03</sub> | <sub>[#84](https://github.com/ucbepic/DataAgentBench/pull/84)</sub> |
| <sub>10</sub> | <sub>Spacedock (Recce) (GPT-5.5)</sub> | <sub></sub> | <sub>0.7850</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-06-23</sub> | <sub>[#63](https://github.com/ucbepic/DataAgentBench/pull/63)</sub> |
| <sub>11</sub> | <sub>Sarvam Code v0.35 (GLM-5.2)</sub> | <sub>✓</sub> | <sub>0.7812</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-07-27</sub> | <sub>[#74](https://github.com/ucbepic/DataAgentBench/pull/74)</sub> |
| <sub>12</sub> | <sub>LabRat (GPT-5.6-Luna-Max + Cartographer)</sub> | <sub></sub> | <sub>0.7751</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-07-16</sub> | <sub>[#72](https://github.com/ucbepic/DataAgentBench/pull/72)</sub> |
| <sub>13</sub> | <sub>Altimate Code (GPT-5.5 + Claude Sonnet 4.6)</sub> | <sub></sub> | <sub>0.7588</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-06-01</sub> | <sub>[#53](https://github.com/ucbepic/DataAgentBench/pull/53)</sub> |
| <sub>14</sub> | <sub>Phoenix-CLI (Claude-Opus-5)</sub> | <sub></sub> | <sub>0.7556</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-09-04</sub> | <sub>[#94](https://github.com/ucbepic/DataAgentBench/pull/94)</sub> |
| <sub>15</sub> | <sub>AgenDA (Claude-Opus-4.8)</sub> | <sub></sub> | <sub>0.7244</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-07-10</sub> | <sub>[#68](https://github.com/ucbepic/DataAgentBench/pull/68)</sub> |
| <sub>16</sub> | <sub>fabric-rlm (GPT-5.6-Luna-Max) ⁵</sub> | <sub></sub> | <sub>0.6956</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-07-31</sub> | <sub>[#76](https://github.com/ucbepic/DataAgentBench/pull/76)</sub> |
| <sub>17</sub> | <sub>Altimate Code (Claude-Sonnet-4.6)</sub> | <sub></sub> | <sub>0.6822</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-05-10</sub> | <sub>[#44](https://github.com/ucbepic/DataAgentBench/pull/44)</sub> |
| <sub>18</sub> | <sub>Spacedock (Recce) (Claude-Opus-4.8)</sub> | <sub></sub> | <sub>0.6804</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-06-08</sub> | <sub>[#55](https://github.com/ucbepic/DataAgentBench/pull/55)</sub> |
| <sub>19</sub> | <sub>MinusX (Claude Sonnet 4.6 + GPT5.5-mini + Claude Haiku 4.5)</sub> | <sub></sub> | <sub>0.6601</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-05-21</sub> | <sub>[#50](https://github.com/ucbepic/DataAgentBench/pull/50)</sub> |
| <sub>20</sub> | <sub>DataBridge (GLM-5.2)</sub> | <sub>✓</sub> | <sub>0.6137</sub> | <sub>6</sub> | <sub>✓</sub> | <sub>2026-06-22</sub> | <sub>[#61](https://github.com/ucbepic/DataAgentBench/pull/61)</sub> |
| <sub>21</sub> | <sub>Pi Coding Agent (Claude-Opus-4.6)</sub> | <sub></sub> | <sub>0.6103</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-04-21</sub> | <sub>[#31](https://github.com/ucbepic/DataAgentBench/pull/31)</sub> |
| <sub>22</sub> | <sub>LabRat (Claude-Sonnet-4.6 + Cartographer)</sub> | <sub></sub> | <sub>0.6088</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-06-24</sub> | <sub>[#65](https://github.com/ucbepic/DataAgentBench/pull/65)</sub> |
| <sub>23</sub> | <sub>PromptQL (Gemini-3.1-Pro)</sub> | <sub></sub> | <sub>0.6000</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-03-18</sub> | <sub>[#24](https://github.com/ucbepic/DataAgentBench/pull/24)</sub> |
| <sub>24</sub> | <sub>PromptQL (Claude-Opus-4.6)</sub> | <sub></sub> | <sub>0.5933</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-03-02</sub> | <sub>[#23](https://github.com/ucbepic/DataAgentBench/pull/23)</sub> |
| <sub>25</sub> | <sub>Spacedock (Recce) (Claude-Opus-4.6)</sub> | <sub></sub> | <sub>0.5828</sub> | <sub>5</sub> | <sub></sub> | <sub>2026-05-08</sub> | <sub>[#47](https://github.com/ucbepic/DataAgentBench/pull/47)</sub> |
| <sub>26</sub> | <sub>Claude-Opus-4.6</sub> | <sub></sub> | <sub>0.5551</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-03-18</sub> | <sub>[#22](https://github.com/ucbepic/DataAgentBench/pull/22)</sub> |
| <sub>27</sub> | <sub>LabRat (Claude-Sonnet-4.6) ²</sub> | <sub></sub> | <sub>0.5138</sub> | <sub>5</sub> | <sub></sub> | <sub>2026-06-01</sub> | <sub>[#54](https://github.com/ucbepic/DataAgentBench/pull/54)</sub> |
| <sub>28</sub> | <sub>Oracle Forge — Team PaLM (Gemini-3.1-Pro-Preview) ³</sub> | <sub></sub> | <sub>0.4721</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-05-10</sub> | <sub>[#37](https://github.com/ucbepic/DataAgentBench/pull/37)</sub> |
| <sub>29</sub> | <sub>Gemini-3-Pro</sub> | <sub></sub> | <sub>0.4663</sub> | <sub>50</sub> | <sub>✓</sub> | <sub>2026-03-02</sub> | <sub>—</sub> |
| <sub>30</sub> | <sub>nQuery (gpt-oss-safeguard-120b) NGENUX SOLUTIONS PVT LTD</sub> | <sub></sub> | <sub>0.4547</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-07-02</sub> | <sub>[#56](https://github.com/ucbepic/DataAgentBench/pull/56)</sub> |
| <sub>31</sub> | <sub>Oracle Forge — Tenacious Intelligence (Claude-Sonnet-4.6) ⁴</sub> | <sub></sub> | <sub>0.4464</sub> | <sub>5–7</sub> | <sub></sub> | <sub>2026-04-21</sub> | <sub>[#32](https://github.com/ucbepic/DataAgentBench/pull/32)</sub> |
| <sub>32</sub> | <sub>GPT-5-mini</sub> | <sub></sub> | <sub>0.3663</sub> | <sub>50</sub> | <sub>✓</sub> | <sub>2026-03-02</sub> | <sub>—</sub> |
| <sub>33</sub> | <sub>GPT-5.2</sub> | <sub></sub> | <sub>0.2991</sub> | <sub>50</sub> | <sub>✓</sub> | <sub>2026-03-02</sub> | <sub>—</sub> |
| <sub>34</sub> | <sub>Kimi-K2</sub> | <sub></sub> | <sub>0.2925</sub> | <sub>50</sub> | <sub>✓</sub> | <sub>2026-03-02</sub> | <sub>—</sub> |
| <sub>35</sub> | <sub>Oracle Forge — Team Cohere (Gemini-2.0-Flash)</sub> | <sub></sub> | <sub>0.1671</sub> | <sub>5</sub> | <sub>✓</sub> | <sub>2026-04-21</sub> | <sub>[#38](https://github.com/ucbepic/DataAgentBench/pull/38)</sub> |
| <sub>36</sub> | <sub>Gemini-2.5-Flash</sub> | <sub></sub> | <sub>0.1049</sub> | <sub>50</sub> | <sub>✓</sub> | <sub>2026-03-02</sub> | <sub>—</sub> |

<sub>**¹ Methodology.** DEPS_DEV_V1 query 1 re-scored on 2026-08-18 by re-running its `validate.py` against a revised validator (accepting any of the 95 packages tied at fifth place on 57779 stars rather than the single tied package recorded in `ground_truth.csv`, see issue #86), from the same submission JSONs, with no other query changed. All Pass@1 scores recomputed on 2026-06-12 by re-running each query's `validate.py` against the current validators (including the regenerated PATENTS ground truths), from the submission JSONs stored in this repository (`submissions/`, `leaderboard_submissions/`) or in the corresponding submission PR branches (`refs/pull/<N>/head`). Pass@1 is the mean over datasets of each dataset's average per-query pass rate.</sub>

<sub>**²** LabRat ([#54](https://github.com/ucbepic/DataAgentBench/pull/54)) had 21 contaminated trials counted as non-passes.</sub>

<sub>**³** Team PaLM ([#37](https://github.com/ucbepic/DataAgentBench/pull/37)) covers 49 of 54 queries (missing queries scored 0).</sub>

<sub>**⁴** Tenacious Intelligence ([#32](https://github.com/ucbepic/DataAgentBench/pull/32)) has 5–7 trials per query (per-query denominators used).</sub>

<sub>**⁵** fabric-rlm ([#76](https://github.com/ucbepic/DataAgentBench/pull/76)) had 8 agnews trials counted as non-passes: 4 loaded external gold labels, and 4 submitted the gold value with no derivation in the supplied traces.</sub>

<sub>**⁶** LabRat ([#84](https://github.com/ucbepic/DataAgentBench/pull/84)) is missing 2 of 270 trials (agnews query 4, infra timeouts), counted as non-passes; excluding them gives 0.8102.</sub>


### How to Submit to the Leaderboard

To contribute your agent's results to the DAB leaderboard:

1. Collect results from **5 runs** on **all queries** across **all datasets**.
2. Organize all your run results into a *single* JSON file following this structure:

    ```json
    [
      {
        "dataset": "<dataset_name>",   // e.g., "bookreview"
        "query": "<query_id>",         // e.g., "1"
        "run": "<run_number>",         // 0–4 for 5 runs
        "answer": "<agent_generated_answer>"
      },
      ...
      // Include an entry for every run of every query across all datasets
    ]
    ```

3. Submit a **Pull Request** to this repository including:

   * The JSON results file
   * **Execution traces** for your runs (the agent's step-by-step logs/transcripts), so results can be independently verified
   * A brief description of your agent configuration, including:

      - The name of your agent

      - Backbone LLM model(s) name and version

      - Whether dataset hints were used

      - Any additional notes or special settings you want to highlight

⚠️ You must include all 5 runs for each query in your dataset, along with their execution traces. Missing runs or missing traces may result in your submission being rejected from the leaderboard.

We will validate each submission — see [SUBMISSION_RUBRIC.md](SUBMISSION_RUBRIC.md), which we recommend checking locally during your runs.


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
  * [Execution Logs](#execution-logs)
  * [Validate Agent Answer](#validate-agent-answer)
* [📝 Datasets and Queries](#-datasets-and-queries)
  * [Dataset](#dataset)
  * [Query](#query)
* [🤖 Create Your Customized Agents](#-create-your-customized-agents)


## 📊 Benchmark Overview


This benchmark contains **12** datasets and **54** queries across **9** domains and **4** DBMSes:

| Dataset          | #DBs | DBMSes                     | #Tbls | #Queries |
| ---------------- | ---- | -------------------------- | ----- | -------- |
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

Many datasets in DAB contain large database files exceeding 50MB and are tracked with Git LFS. If you want those files to come down during the clone itself, enable Git LFS **before** cloning:
```bash
git lfs install
```
Then clone and run the downloader:
```bash
git clone https://github.com/ucbepic/DataAgentBench.git
cd DataAgentBench
bash download.sh
```

`download.sh` serves two purposes:

- **Downloads large datasets that aren't on GitHub.** The ~5GB `PATENTS` database (`patent_publication.db`) is too large for the repo, so it's fetched from the Hugging Face mirror.
- **Repairs failed Git LFS pulls.** If Git LFS wasn't enabled before cloning or hit an error, some tracked files end up missing or as pointer stubs. The script checks each file in [`dataset_manifest.tsv`](./dataset_manifest.tsv) against its sha256 and (re)downloads any mismatch from the [Hugging Face Hub](https://huggingface.co/datasets/ruiyingm/DataAgentBench-data) mirror.

Files that already match are left untouched.


### Install Dependencies

We recommend using a dedicated virtual environment to ensure reproducibility.

**Using Conda (recommended):**

```bash
sudo apt-get install libpq-dev
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
  The image includes **Python 3.12**, **pandas**, and **PyArrow** pre-installed:

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
Modify the defaults in [db_config.py](./common_scaffold/tools/db_utils/).




### Add API Credentials
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
- Together.AI API (for Kimi models)

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

DAB comes with a built-in agent. You can run the agent on a specific query as follows:

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


DAB provides utilities to compute both **aggregated Pass@1 accuracy of a dataset** and **single-run correctness**.

#### Compute Pass@1 (50 Runs)

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
@article{ma2026can,
  title={Can AI Agents Answer Your Data Questions? A Benchmark for Data Agents},
  author={Ma, Ruiying and Shankar, Shreya and Chen, Ruiqi and Lin, Yiming and Zeighami, Sepanta and Ghosh, Rajoshi and Gupta, Abhinav and Gupta, Anushrut and Gopal, Tanmai and Parameswaran, Aditya G},
  journal={arXiv preprint arXiv:2603.20576},
  year={2026}
}
```

