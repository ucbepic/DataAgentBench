# PromptQL: agent description

- Agent: PromptQL
- Backbone models: Claude Fable 5.2 and GPT-6.2 Astra (reasoning effort max). These are two separate entries.
- Hints used: Yes
- Tuned prompt: No
- Coverage: 53 of 54 questions, 5 runs each, 265 trials per model. GITHUB_REPOS query 2 is missing for both models.

## How it works

PromptQL is a general-purpose data agent. Each dataset was connected to a PromptQL project as a data source. Every trial started a new, empty bot under a non-admin trial account and sent it one message: the prompt. The bot plans, writes and runs its own SQL and Python against the connected data, and posts one final message. That message is the answer in the answers file.

We didn't build tools, write wiki pages or add instructions for this benchmark.

## Data

The benchmark's SQLite, DuckDB and PostgreSQL sources were loaded into PostgreSQL and connected to the projects. AG News and Yelp ran in one shared project through its connectors, including two MongoDB connectors, with read access set per table for each dataset's trial account.

## Prompt

One wrapper for every question and both models. It has no dataset names, no query names and no rules written for this benchmark. The full text is in the PR description and in `promptql_prompts_and_reports.tar.gz`.

The wrapper carries the dataset's `db_description.txt`, its `db_description_withhint.txt` and the question from `query.json`.

## Notes

- AG News has no stored category, so the agent had to classify articles itself. Some Claude Fable 5.2 answers say it used an LLM for that. The traces don't include the classification step for either model. See the PR description.
- Internet access was on. The prompt told the agent not to use it. See the PR description for what we checked.
- The traces are partial. See the PR description for what they hold.
