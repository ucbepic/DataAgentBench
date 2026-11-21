# stockindex 冻结口径（预注册）

- 冻结时间：2026-11-09T07:15:00Z（作者：dab-agent-01；cross-checker：dab-agent-02 待复算）
- 知识来源：附录 A3（stockindex 全通过条目：混合日期格式归一、日内波动 (High-Low)/Open、up day Close>Open、每月首个交易日定投）、官方 withhint（Exchange↔主要指数符号映射 + 区域推断 + 波动率定义）。
- Sanctioned stores：`indexInfo_query.db`（index_info: 14 交易所×货币）、`indextrade_query.db`（index_trade: 13 指数符号×混合日期格式 OHLC/Adj Close/CloseUSD）。

## Exchange → Index 符号映射（地理知识，withhint 例证）
NYSE→NYA、NASDAQ→IXIC、港交所→HSI、上交所→000001.SS、东证→N225、Euronext→N100、深交所→399001.SZ、多伦多→GSPTSE、印度 NSE→NSEI、法兰克福→GDAXI、韩国交易所→（无对应符号，内连接不参与）、约翰内斯堡→J203.JO、SIX→SSMI、台湾→TWII。
区域：Asia = HSI/000001.SS/399001.SZ/N225/NSEI/TWII；North America = NYA/IXIC/GSPTSE；Europe = N100/GDAXI/SSMI；Africa = J203.JO。
国家（q3 用）：NYA/IXIC→United States、N225→Japan、GDAXI→Germany、GSPTSE→Canada、HSI→Hong Kong、SSMI→Switzerland。

## 日期归一
混合格式（`31 Dec 1986, 00:00` / `January 02, 1987 at 12:00 AM` / `1987-01-05 00:00:00` / `06 Jan 1987, 00:00`）统一解析为 date（dateutil 逐行尝试多格式；失败行计数登记、不丢弃）。

## q1（2020 以来亚洲平均日内波动最高）
- 亚洲指数集内、Date ≥ 2020-01-01 的交易日，vol = (High-Low)/Open 逐日，按指数求平均；取最高。
- ~~数据截止使候选实际为 N225 与 TWII~~（**修订登记 1，2026-11-09T07:20Z，规则不变仅更正描述**：早前"数据截止"判断来自 Date 字符串 min/max，混合格式下字符串比较无意义；归一化后 6 个亚洲指数均有 2020 数据，全部参与：HSI 348 天/000001.SS 340/N225 344/399001.SZ 342/NSEI 349/TWII 339。）
- 答案 = 该指数在 Index 字段中的符号（如 `TWII`），单行。

## q2（2018 年北美 up days > down days 的指数）
- 北美指数集（NYA/IXIC/GSPTSE），2018 自然年：up = Close>Open，down = Close<Open（相等不计入任一侧）；up>down 者入榜。
- ~~GSPTSE 数据止于 2016-09-30 不参与~~（**修订登记 1 同上：字符串 max 伪象；归一化后 GSPTSE 2018 年有 250 个交易日，参与判定**。）
- 答案 = 入榜指数符号，字典序，逗号+空格连接单行。

## q3（2000 起每月定投收益 top5 及国家）
- 起点：2000-01-01 起有交易数据的指数（**修订登记 1 同上：实际候选 11 个**——HSI/NYA/IXIC/000001.SS/N225/N100/399001.SZ/GSPTSE/GDAXI/SSMI/TWII，均自 2000-01 可定投；J203.JO（2016 起）与 NSEI（2014 起）不参与）。
- 定投：自 2000-01 起每个自然月的**首个交易日**投 1 USD，按当日 CloseUSD 计入份额（跨币种可比，用数据集自带的 USD 折算列；Adj Close 为本币复权，不用于跨市场比较）。
- 期末：该指数数据中最后一个交易日的 CloseUSD；总投入 = 月数；总收益 = 期末市值/总投入 − 1。
- 按 收益 降序取前 5；并列按符号字典序。
- 答案帧式：`N. <SYMBOL> (<Country>)` 共 5 行。

## 修订登记 1（2026-11-09T08:40Z，自评前；触发=D3 复算〔strict 通过答案核对〕）
- q3 候选集修正：去掉「数据须始于 2000-01-31 前」的误加过滤——题面 "regular monthly investments in all indices since 2000" 即所有指数参与，月度投资自 2000-01 或该指数首个可得月起算（NSEI 自 2007-09 起 165 个月入选第 2）。修正后 top5 = IXIC/NSEI/399001.SZ/GDAXI/TWII，与 strict 通过集合一致（旧读法漏 NSEI、多 N225）。
- q1/q2/q3 输出格式逐字节对齐 strict：q1 = `SYM (交易所全名, 国家) - highest average intraday volatility since 2020 (0.0183)`；q2 = `SYM (交易所, 国家) - <up> up days vs <down> down days`；q3 = `N. SYM (国家) - overall return <P>% over <K> monthly investments`。
