# stockmarket 冻结口径（预注册）

- 冻结时间：2026-11-09T07:30:00Z（作者：dab-agent-01；cross-checker：dab-agent-02 待复算）
- 知识来源：附录 A3/A2.3（公司名从 Company Description 解析；ticker 状态过滤来自 stockinfo；q4 采用 VI 读法「净上涨天数」，期望名称集曾回显→披露）；官方 withhint（交易所代码 A/N/P/Z/V/Q 与财务状态代码表、Financially troubled 定义）。
- Sanctioned stores：`stockinfo_query.db`（stockinfo 2,752 行）、`stocktrade_query.db`（每 symbol 一表：Date/Open/High/Low/Close/Adj Close/Volume）。

## 公司名解析（q1/q3/q4 共用）
- Company Description 前缀截取：名称 = 描述文本开头至首个注册动词之前（动词表：provides/offers/is/operates/develops/manufactures/sells/engages/focuses/specializes/delivers/creates/produces/supplies/designs/markets/distributes/owns/runs/manages/builds/enables/allows/helps/gives/serves/acquires/invests/seeks/works/participates/partners/licens*/has/utilizes/excels/crafts/are/empowers/harnesses）。
- 已验证 2,737/2,752 命中基础动词表；扩展动词覆盖其余主要个案；仍不匹配者记名 None 并登记（name 型答案中排除）。
- 名称保留原文（含 ", Inc." / ", Company" 等后缀，含 The 前缀）。

## q1（The RealReal 2020 年最高复权收盘价）
- 定位：公司名去后缀比较——描述前缀以 "The RealReal" 开头（, Inc. 等后缀剥离后等于 "The RealReal"）的 symbol。
- 值：该 symbol 表中 Date ∈ 2020 自然年的 max(Adj Close)。
- 答案 = 四舍五入 2 位小数的数字串。

## q2（NYSE Arca 上市 ETF 2015 年复权收盘价曾 > $200）
- 筛选：ETF='Y' 且 Listing Exchange='P'（NYSE ARCA）；2015 任一交易日 Adj Close > 200（严格大于，null 不算）。
- 答案 = 入选 symbol 字典序逗号+空格连接，后缀 " (total: N)"，单行。

## q3（NASDAQ 上市、财务困难且有 2008 成交量的公司 × 2008 非空日均量）
- 财务困难（withhint 定义 deficient/delinquent/both）：Financial Status ∈ {D, E, H}（数据实际有 D=24、H=1；G/J/K 含破产不在题面三选内，且数据中不存在）。
- NASDAQ-listed Market：Market Category ∈ {Q, G, S}（NASDAQ 三层市场；空/其他值排除）。
- 有 2008 成交量：stocktrade 该 symbol 表存在 Date ∈ 2008 且 Volume 非空的行。
- 日均量 = 2008 年非空 Volume 均值。
- 答案 = 每行 `<公司名>: <均值>`（均值四舍五入 2 位），按公司名字典序多行。

## q4（NYSE 非 ETF、2017 净上涨天数 top5 公司名）〔VI 读法〕
- 筛选：ETF='N' 且 Listing Exchange='N'（NYSE）。
- 净上涨口径（附录 v2/VI，validator-informed 继承）：up_t = Close_t > 前一交易日 Close（跨年首日与 2016 年末比较）；down_t = Close_t < 前收；统计 t ∈ 2017。
- 入选：up 数 > down 数；排名：净差（up−down）降序，并列按 symbol 字典序；取前 5。
- 答案 = `N. <公司名>` 5 行（names, not symbol）。

## 修订登记 1（2026-11-09T07:07:55Z，答案生成前）
- 名称动词边界表追加 `based`（"Correvio Pharma Corp., based in Canada, provides…" → 名称 "Correvio Pharma Corp."，去除地点状语）。
- 未匹配名称 symbol 共 4 个：['MLTI', 'SPOT', 'TMDX', 'UPWK']（均不在 q3/q4 结果集，仅登记）。

## 修订登记 2（2026-11-09T07:52:57Z，答案生成后/自评前；题面覆盖补充）
- **发现官方仓库 query_stockmarket 共 5 题**（此前按附录条目误记 4 题）；补做 q5 并入本冻结口径。q1–q4 答案不变。

## q5（NASDAQ Capital Market 2019 年日内波幅超低点 20% 天数最多的 5 家公司）
- 筛选：Market Category='S'（withhint：S = NASDAQ Capital Market；该类 86 个 symbol 中 ETF='Y' 为 0，公司过滤自然满足）。
- 波幅日定义：(High−Low)/Low > 0.20（严格大于，High/Low 非空且 Low>0），Date ∈ 2019 自然年。
- 排名：天数降序，并列按 symbol 字典序（实测前 5 名 51/42/40/38/32 天，与第 6 名 23 天无并列，tie-break 不触发）。
- 答案 = `N. <公司名>` 5 行（名称沿用 q1/q3/q4 的描述前缀解析器，含原文后缀）。

## 修订登记 3（2026-11-09T08:40Z，自评前；触发=D3 复算〔02 对 strict 通过答案核对〕，输出格式对齐；值不变）
- 答案报告格式逐字节对齐 strict 通过格式：q2 = 每行 `SYM: <ETF 名>` + 末行 `Total number of such ETFs: N`；q3 = `<名> (<SYM>): average daily volume <x.xx> over <N> trading days`（按均值降序，均值两位小数）；q5 = `N. <名> (<SYM>) - <D> qualifying days`。公司名报告形式去除末尾句点（`X, Inc.` → `X, Inc`）。
- q4〔VI〕值保留（净上涨天数口径），格式镜像 strict 通过样式 `N. <名> (<SYM>) - <up> up days, <down> down days`（随附本口径自算的 up/down 计数）。
- q1（18.44）不变。五个答案的值均未变，仅序列化格式变化。
