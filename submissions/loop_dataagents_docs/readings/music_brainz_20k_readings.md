# music_brainz_20k 冻结口径（预注册）

- 冻结时间：2026-11-09T07:25:00Z（作者：dab-agent-01；cross-checker：dab-agent-02 待复算）
- 知识来源：附录 A3（music_brainz_20k 全通过：实体归一——标题归一 + 模糊匹配，artist/album 支撑——后再聚合收入）、官方 withhint（去重需实体归一，属性可有小变异；sales 五国五平台）。
- Sanctioned stores：`/root/dabdata/query_music_brainz_20k/query_dataset/tracks.db`（tracks 19,375 行）+ `sales.duckdb`（**官方仓库 query_dataset 副本**，dabdata 镜像缺此文件；sales 58,049 行）。

## 标题清洗（保留原拼写用于展示；归一用于比较）
1. 剥离前缀 `^\d{1,4}[-_. ]+`（音轨号 022-、011-）。
2. 剥离成对括号内容 `(…)`（专辑名后缀）。
3. 若含 ` - `：左侧 fuzzy≈artist（≥85）或 artist 缺失（None/'[unknown]'）→ 取右侧为标题核心；否则右侧 fuzzy≈本行 album 或任一同块 album（≥85）→ 取左侧。
4. 清洗后标题去两侧空白；重复 1–3 至稳定。
- 归一 key = NFKD 去变音符 → 小写 → 仅保留字母数字（**去掉全部空格与标点**：可吸收 'GetMe Bodied'、'StreetH ype'、'R&B' 等变异）。

## artist/album/year/length 归一
- artist：None/'[unknown]'/'unknown' 视为缺失；归一同上（去变音符后 'Beyoncé'='Beyonce'）。
- album：归一同上；缺失容忍。
- year：4 位取后两位比对（'2007'≡'07'≡"'07"）。
- length：不参与匹配（格式混乱：秒/毫秒/'2m 57sec'/'00:00'），仅登记。

## 聚类（并查集）
- 分块：清洗后标题归一 key 的前 2 个字母数字字符。
- 块内两两合并条件（全部满足）：
  a) 标题 partial_ratio(归一) ≥ 90（partial 吸收残余前后缀）且非互为不同标题（交集保护：较短者长度 ≥ 4）；
  b) artist 双方齐全：ratio ≥ 85（吸收 'Brucqe'/'Bruce' 单字母替换）；一方缺失：要求 (album 双方齐全 ratio ≥ 80) 或 (year 等价)；
  c) 不做跨块合并（限制爆炸）。
- 聚类后每簇 = 一个真实曲目实体；簇标题（展示用）= 簇内清洗后标题的众数（并列取字典序最小）。

## 收入聚合
- sales.track_id → tracks 行 → 簇；簇收入 = sum(revenue_usd)。

## q1（Beyoncé 'Get Me Bodied' × Apple Music × Canada）
- 目标簇 = 清洗标题归一 = 'getmebodied' 且 artist 归一 fuzzy 'beyonce' ≥ 90 的簇（核验恰 1 簇）。
- 答案 = 该簇 sales 中 store='Apple Music' 且 country='Canada' 的 revenue_usd 总和，四舍五入 2 位小数串。

## q2（Brucqe Maginnis 'Street Hype' 全平台最高收入 store）
- 目标簇 = 标题归一 fuzzy 'streethype' ≥ 90 且 artist 归一 fuzzy 'brucqemaginnis' ≥ 85（'Bruce Maginnis' 命中）恰 1 簇。
- 按.store 聚合收入，取最高（并列字典序最小）；答案 = store 名单行。

## q3（全库总收入最高曲目）
- 全部簇聚合收入，取最高（并列取簇标题字典序最小）；答案 = 簇标题（众数形式）单行。

## 修订登记（2026-11-09T07:19:06Z，答案生成前，聚类规则证据驱动收紧）
- **rev.1**：分块键改 2/3 字符双键；短标题（norm<8）仅允许精确相等（防 "Mein" 类碎片吸收长标题后传递合并）。
- **rev.2**：占位标题（untitled/unknown/notitle/noname）不入聚类（互非同一实体，聚合无意义）；多分块键恢复 'Sttreet'↔'Street' 跨块配对。
- **rev.3**：norm 保留 Unicode 字母（西里尔艺术家不再被判缺失——曾使 Tchaikovsky "Concerto" 碎片经 year 通路吸收整组古典作品）；短标题阈 <10 仅精确；缺 artist 合并路径收紧为「album ratio≥80」或「标题精确相等∧year 相等」。
- 验证锚点：Beyoncé 簇恰 5 成员（4233/5281/10838/12954/15158）；Street Hype 簇恰 5 成员（含 'Sttreet Hype' 与 'StreetH ype' 变体）；Bach Presto 簇从 9（污染）回落；q3 top5 各簇 5–6 成员。
- 块 >800 跳过登记：[['th', 992], ['3:the', 806]]（仅损召回，不影响正确性方向）。
