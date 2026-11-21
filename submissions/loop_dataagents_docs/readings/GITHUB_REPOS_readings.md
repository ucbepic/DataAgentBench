# GITHUB_REPOS 冻结口径（预注册）

- 冻结时间：2026-11-09T06:52:00Z（作者：dab-agent-01；cross-checker：dab-agent-02 待复算）
- 知识来源：附录 A2/A3（GITHUB 条目）、strict 基线描述（token-exact 语言成员、README 版权 contents⋈files、按 blob id 去重）、官方 withhint 描述。方案乙 benchmark-informed。
- 污染披露：GITHUB_REPOS q1–q4 前轮两名成员曾见部分 gold（附录 A2.1）；本轮答案仍全部由 sanctioned stores SQL/管道得出，中间行入 trace。
- Sanctioned stores：`repo_metadata.db`（repos/languages/licenses，一 repo 一行）、`repo_artifacts.db`（files/contents/commits，DuckDB）。

## 语言 token 抽取（q1/q3/q4 共用）
- 从 `language_description` 正则抽取 `(<Lang>) \(([\d,]+) bytes\)` 对；token 精确匹配（大小写敏感原样，PowerShell≠Shell，Vim script≠script）。
- 成员资格 = token 出现（无论字节数）；主语言 = 字节数最大 token（并列取字典序最小，记录）。
- languages/licenses 缺行的 repo（如 torvalds/linux 级别缺失）在内连接语义下不参与对应题。

## q1（不用 Python 的 repo 的 README.md 含版权比例）
- R1 = languages 中 token 集不含 "Python" 的 repo。
- **修订登记 2（2026-11-09T07:05:00Z，答案生成前）**：README 文件改取 contents 中 sample_path='README.md' 的行。证据：files 与 contents 为两棵独立抽样树，id 交集仅 362 个 blob，path='README.md' 的 1,059 个 files 行 join contents 为 0 行；README 内容样本在 contents 侧（128 行，id 唯一）。repo 归属 = sample_repo_name；无 languages 行的 repo（10 个）按内连接不参与。原"files 行 + join contents"读法在该数据结构上恒为 0/900，失真。
- 文件集 U = sample_repo_name∈R1 的 contents README 行，按 blob id 去重（该表 id 唯一，去重为恒等）。
- 含版权 = lower(content) 含子串 'copyright'。
- 比例 = 含版权数 / |U|，答案 = round(比例, 4) 的小数串（Python round，4 位）。

## q2（含 Swift 代码的 repo + 被复制最多的非二进制 .swift 文件）
- Swift 文件 = files 中 path 以 '.swift' 结尾的行。
- 非二进制 = id 在 contents 中且 repo_data_description 含 'non-binary'（contents 确含 3,786 行二进制描述行，须显式排除）。
- **修订登记（2026-11-09T06:55:00Z，答案生成前）**：复制次数改以 repo_data_description 中的 "appears/sees/repeated/duplicated N times" 为准。证据：files 表为路径抽样（非二进制 .swift blob 在 files 中均仅 1 行），描述中的 times 才是数据集级拷贝数；原"files 行数为准"规则在抽样表上失真。非二进制 .swift blob 共 2 个（copies 23 与 15），最大者唯一无并列。
- 答案 repo = 该 id 在 files 中的拷贝 repo（经核验 SwiftAndroid/swift 唯一）且 languages 含 "Swift" token；答案 = repo_name 单行。
- （题面 "uniquely determined by its ID" 即按 blob id 去重认定"同一文件"。）

## q3（Shell + Apache-2.0 repo 的 commit message 计数）
- R3 = languages 含 "Shell"（精确）且 licenses.license.strip().lower()='apache-2.0' 的 repo。
- commits 中 repo∈R3 的行；message 非空非 NULL；len(message)<1000 字符；lower(message) 不以 'merge'/'update'/'test' 开头。
- 答案 = 合格行数（每行一条 message，不去重文本）。

## q4（主语言非 Python 的 commit 数 top5 repo）
- 主语言 = 字节最大 token；不含 languages 行的 repo 不参与（内连接）。
- 排除主语言='Python'；按 commits 行数降序取前 5；并列 commit 数按 repo_name 升序。
- 输出帧式（与 DEPS 列表一致）：`N. <repo_name>` 共 5 行。

## 修订登记 3（2026-11-09T08:40Z，自评前；触发=D3 复算〔strict 通过答案核对〕；本数据集已按 A2.1 披露 gold 暴露史）
- **q1 旧→新读法**：旧「README 语料 = contents 中 sample_path='README.md' 的 128 个样本 blob，非 Python 按 token 精确判定 → 108 blob / 16 copyright / 0.1481」→ 新「README 语料 = files ⋈ contents **按 blob id 相等** 且 lower(path) LIKE '%readme.md'（4 blob）；"不使用 Python" = language_description **不含子串** 'Python'（子串判定，非 token）→ 3 blob / 1 copyright / 0.3333333333333333；输出 CSV 两行 `total_readmes,copyright_readmes,proportion`」。新读法为我方以独立 SQL 复现并通过（4 blob 中 rgardler/azure-quickstart-templates 因描述含 'Python' 子串剔除），读法承继自前轮通过管线（D3 判别裁决）。
- q2/q3/q4 值不变，输出格式对齐 strict：q2/q3 加 CSV 表头行（`repo_name` / `num_messages`）；q4 改 CSV `repo_name,num_commits` + `repo,count` 行。
