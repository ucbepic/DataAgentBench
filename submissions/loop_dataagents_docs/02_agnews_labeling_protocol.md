# agnews 离线标签协议（预注册冻结）— dab-agent-02, 2026-11-09

## 覆盖谓词（标签覆盖范围的选择依据：四个 query 的谓词）

L = 满足以下任一谓词的文章集合（article_id 去重）：
- A: 作者为 Amy Jones（authors.name = 'Amy Jones'，经 article_metadata join）
- B: region='Europe' 且 publication_date ∈ [2010-01-01, 2020-12-31]（含端点）
- C: publication_date ∈ [2015-01-01, 2015-12-31]（含端点）
- D: description 字符长度排名前 60 的文章（按 len(description) 降序，取前 60 作缓冲；q1 只需要从最长往下找第一个 Sports）

只对 L 内文章打四类标签；L 外文章不打标签、不参与任何统计。

## 类别定义（给标注者的指南，逐字用于所有 pass）

四个类别（官方 withhint 给定）：World / Sports / Business / Science/Technology。

- World: 国际关系、战争与冲突、外交、各国政治与选举、法律与犯罪、恐怖主义、王室、公众人物讣告、社会抗议、自然灾害事故（无科技/商业主线时）。
- Sports: 任何体育运动、运动员、球队、赛事、联赛、奥运、赛车（体育竞技视角）。
- Business: 公司经营与财报、股市/汇率/大宗商品行情、并购、经济数据与宏观政策、就业、房地产、行业市场分析、能源油市（商业视角）。
- Science/Technology: 科学研究与新发现、太空、医学研究（研究视角）、计算机/互联网/软件/硬件/消费电子、网络安全漏洞、游戏与数码产品、技术标准。

边界规则（统一适用）：
1. 科技公司的财报/股价/并购 → Business；科技公司的产品与技术发布 → Science/Technology。
2. 生物医药的临床研究/药物机理 → Science/Technology；药企的经营与股价 → Business。
3. 体育赛事与运动员 → Sports；体育产业的商业交易（转播权出售等以商业为主线）→ Business。
4. 疾病的医学研究 → Science/Technology；疫情的政治/社会应对 → World。
5. 汽车行业产销与公司动态 → Business；新车型的具体技术介绍 → Science/Technology。
6. 无法判断主线的多主题文章：以标题主题为准；标题也不明确时按 Science/Technology < Business < World < Sports 的顺序取最先可排除者（即尽量排除而非默认）。

## 标注流程

- pass1、pass2：两个独立的标注者实例（不同 subagent 会话），同一输入文件，逐条输出 {article_id, label}。标注者只见 (article_id, title, description) 三列，不接触其他任何数据。
- 分歧处理：pass1 与 pass2 不一致的条目交 pass3（第三个独立实例，附边界规则全文重读原文）；最终标签 = 3 pass 多数；pass3 后仍三分歧（不可能出现，2 类分歧下 3 pass 必有多数）——若 pass3 产生第三类则形成三方分裂，由 dab-agent-02 人工裁决并逐条留痕。
- 标签文件与分歧裁决记录全部落盘 /root/dabteam/runs/agnews_labels/。

## 下游确定性统计（trial 内，不使用任何 LLM）

- q1: 在 L∩D 中从最长 description 依次向下，第一个 label=Sports 的文章，答案 = 其 title（原样字符串）。
- q2: count(A ∩ Science/Technology) / count(A)，输出小数（≥4 位精度）。
- q3: count(B ∩ Business) / 11（2010..2020 共 11 年，含端点），输出该平均数。
- q4: C 中 label=World 的文章按 region 分组计数，取计数最大的 region；并列 tie-break：字母序取先（预注册，不因结果调整）。

## 红线确认

本协议及标注指南不含任何期望答案值、类别基数、行集；标签仅由 LLM 阅读 sanctioned (title, description) 文本产生；trial 内统计为纯确定性代码。
