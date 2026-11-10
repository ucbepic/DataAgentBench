# dab-agent-02 逐题口径冻结 v1（预注册）— 2026-11-09T06:43:46Z

> 冻结时间见 02_freeze_timestamp.txt。本文件在计算任何答案之前写盘。
> 知识来源：方案乙（benchmark-informed）。通过读法继承自附录（其中 PANCANCER q1、PATENTS q2、bookreview q1 为 validator-informed 的 v2/VI 读法）；googlelocal q3、yelp q6 为本轮按题面自行预注册的新读法（strict 读法已知失败，未继承）。
> 实现约束：严格基线包（loop_team_dab_full_strict 五件套）中的既有答案串仅用作实现正确性交叉核对（同读法同数据应复现同值），不作为答案来源。

## PANCANCER_ATLAS

- q1〔v2/VI〕：LGG 队列 = clinical_info.Patient_description 含 "Lower Grade Glioma"；表达行 = RNASeq_Expression.Symbol='IGF2' 且 normalized_count 非空；按 clinical_info.icd_o_3_histology 分组（替代 strict 的 histological_type 名称分组），排除方括号注记（如 "[Not Applicable]"）；值 = mean(log10(normalized_count+1))（+1 偏移，替代 strict 的无偏移）。输出行 "ICD-O-3码: %.4f"，按组标签字母序。join 键 RNASeq.ParticipantBarcode ↔ clinical patient_id（Patient_description 内 TCGA barcode）。
- q2（strict 通过读法）：BRCA 队列 = Patient_description 含 "Breast...Carcinoma"（BRCA=Breast Invasive Carcinoma）；alive = Patient_description 含 "vital status: Alive"；按 histological_type 分组，组内 CDH1 突变患者占比 = 有任一 Hugo_Symbol='CDH1' Mutation_Data 行的患者数 / 组内患者总数（分母为该 histology 非 null 的 alive BRCA 患者）；取前 3，行格式 "Name - PP.PP% (m/n)"，按占比降序。
- q3（strict 通过读法）：女性 BRCA（Patient_description 含 "FEMALE"）；行 = histological_type（非空、非方括号），列 = 是否有 CDH1 突变（Mutation_Data，join 同上）；剔除行合计 ≤10 的 histology（若列合计也 ≤10 一并剔除）；χ² = Σ(O-E)²/E，E=行合计×列合计/总计；输出 χ² 值 4 位小数。

## PATENTS

- q1（strict 通过读法）：专利计数按 publicationinfo 全体（277,813 行），年份 = filing_date 解析年；每专利在每组只计一次，组 = cpc 字段中 first=true 的条目映射到 cpc_definition.level=5 的组（code 本身或其 level=5 祖先——以 cpc_definition.parents/level 判定，实现时用 symbol 前缀树判定所属 level-5 组）；EMA α=0.2、首值初始化、首年至末年零填充；best year = EMA 最高年（并列取最早）；输出所有 best year=2022 的 level-5 组码，按 2022 年 EMA 值降序（并列按码字母序），换行分隔。
- q2〔v2/VI〕：选择集 = assignee 国别为德国（Patents_info 的 country_code='DE'）且 grant_date ∈ 2019-07-01..2019-12-31 的 grant 专利；level-4 组 = 该选择集涉及的 cpc_definition.level=4 组；每组年度序列 = **选择集内**专利按 filing_date 年计数（区别于 strict 的全体专利序列）；EMA α=0.1、首值初始化、零填充、最早峰值；输出 best year ≠ 末年（即峰值出现在序列中间/早期、非单调递增至末年）之外——**输出规则（预注册）**：按峰值 EMA 值降序取前 4 组，行格式 "CODE | TITLEFULL | best year YYYY"。〔注：取前 4 依据 strict 答案行数；若数据自然分界（如第 4/5 名明显断档）以分界为准并在 trace 中说明〕
- q3（strict 通过读法）：UC 专利 = Patents_info.assignee_harmonized 含 "UNIV CALIFORNIA"（子串，覆盖 campus 变体）；引用判定 = citation 字段引用了 UC 专利的公开号；输出 (citing assignee, 被引 UC 专利的主 CPC subclass 的 titleFull)，(assignee, title) 去重；行格式 "ASSIGNEE | TITLEFULL"，按 assignee 字母序。主 subclass = 被引 UC 专利 cpc 中 first=true 条目的 code（映射 cpc_definition.titleFull）。

## bookreview

- q1〔v2/VI〕：review-weighted：年代平均 = 该年代出版书籍所获全部评分的均值（每条 review 一票；区别于 strict 的先书均分再年代平均）；年代 = 出版年（features/details 中 "Month D, YYYY" 解析）10 年段（1980s=1980-1989）；仅计入 ≥10 本有评分数书籍的年代；答案 = 均值最高的年代标签（如 "2020s"）。
- q2（strict 通过）：English 判定 = details 含 `\bin English\b`；类别 = categories 解析后含 'Literature & Fiction'；均分 = 全部 review 均值 = 5.0；输出书名列表，按 book_id 升序（strict 顺序核对依据）。
- q3（strict 通过）：类别含 "Children's Books"；仅 review_time ≥ 2020-01-01 的评分；均分 ≥ 4.5；输出书名列表，按 book_id 升序。

## googlelocal

- q1（strict 通过）：Los Angeles, CA（description 含 "Los Angeles"）；均分 = review 表按 gmap_id 均值；排序 均分降序 → 评论数降序 → gmap_id 升序；前 5；行 "N. Name - R.RR (M reviews)"。
- q2（strict 通过，R001/R002 修订）：按摩业 = name/description 含 massage 或 ≥3 条不同 review 文本含 massage；均分 ≥ 4.0；排序 均分降序 → 评论数降序 → gmap_id 升序；行 "Name - R.RR"。
- q3【本轮新预注册，strict 读法已知失败】：营业时段解析 hours（JSON list of [day, span]）；"remain open after 6:00 PM on at least one weekday" = 存在 Mon–Fri 的时段满足 start ≤ 18:00 且 end > 18:00（18:00 时刻仍在营业且随后才打烊；跨午夜时段 end<start 视为 end=24:00 判定），或 "Open 24 hours"；排序 均分降序 → 评论数降序 → gmap_id 升序，前 5；行 "N. Name - hours: SPAN - average rating: R.RR"，SPAN = 星期一到五顺序中第一个满足条件的原文字符串。
- q4（strict 通过）：2019 年内（review.time 解析年=2019）rating ≥ 4.5 的评论数；前 3；行 "Name - M reviews"（R001 修订），计数降序 → gmap_id 升序。

## yelp

- 公共解析：review/tip 的 business_ref ↔ business.business_id（前缀替换 businessref_→businessid_）；日期多格式解析（含 "January 01, 2016"、"01 Aug 2016"、ISO、"June 14, 2021 at 11:39 AM"）；类别 = description 中 "in <CAT1, CAT2, ...>" 闭词表最长短语匹配（保留 "American (New)" 括号）；州 = description "in CITY, ST" 的 ST。
- q1（strict 通过）：Indianapolis, Indiana 的全部 business；均分 = review 表这些 business 的评分均值；输出 "%.2f"。
- q2（strict 通过）：州按 review 行数（join business）计数最多者；输出 "ST, R.RR"，R.RR = 该州 business 的 review 均分。
- q3（strict 通过）：2018 年有 review 的 business ∩ (attributes.BusinessParking 任一子键 True 或 BikeParking='True')；输出计数（整数）。
- q4（strict 通过）：BusinessAcceptsCreditCards='True' 的 business 按类别计数（一 business 多类别时计入其每个类别）；计数最大类别 + 该类别 business 均分；输出 "Category, R.RR"。
- q5（strict 通过）：WiFi 属性 ≠ no（free/paid 均 offer）的 business 按州计数最多的州 + 这些（该州 offer WiFi 的）business 的均分；输出 "ST, R.RR"。
- q6【本轮预注册（R003 修订）：strict 读法已知失败】：窗口 2016-01-01..2016-06-30（含端点）内有 review 的 business，全部评论数（review 表全量）≥ 5；排序 = 窗口内均分降序 → business_id 升序；答案 = "店名, 字母序第一类别" 单行。
- q7（strict 通过）：yelping_since 年=2016 的用户；其 date ≥ 2016-01-01 的 review 按 business 类别累计（review 计入 business 的每个类别）；前 5 类别，计数降序 → 类别名字母序；输出逗号+空格连接。

## agnews

见 frozen/02_agnews_labeling_protocol.md（已冻结）。q1 缓冲集 D=top60 已按数据核实；L=A(111)∪B(14,860)∪C(6,696)∪D(60)=20,342，输入批次已导出。

## 红线确认

本文件不含期望答案字面值/类别基数/精确行集；strict 包答案串仅用于实现核对。冻结后如经 validator 反馈修订，逐条登记 query/旧读法/新读法/触发原因，最终披露 validator-informed。
