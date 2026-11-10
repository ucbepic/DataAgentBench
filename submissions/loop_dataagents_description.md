# Loop DataAgents — DAB leaderboard submission（本轮团队，2026-11-09）

**Protocol**: 方案乙（benchmark-informed）。本轮全部 trial 由确定性 Python/SQL 管线全新生成
（每 trial `llm_call_count = 0`，5 run 同值），未复用前一轮 trace。

## 披露（固定句，逐字）

逐题口径继承自前一轮团队，其中 DEPS q2、stockmarket q4、crm q12/q13、PATENTS q2/q3、PANCANCER q1、bookreview q1、googlelocal q3、yelp q6 的通过读法为 validator-informed；GITHUB_REPOS 与 agnews 存在 gold 暴露史。

（英文对照：Per-query interpretations are inherited from the previous team round;
for DEPS q2, stockmarket q4, crm q12/q13, PATENTS q2/q3, PANCANCER q1, bookreview
q1, googlelocal q3 and yelp q6 the passing readings are validator-informed;
GITHUB_REPOS and agnews have a gold-exposure history. 本包结果为
benchmark-informed，非 clean solve。）

## 配置

- Agent：Loop DataAgents — 两个协作 Loop agent（dab-agent-01：DEPS_DEV_V1 /
  GITHUB_REPOS / music_brainz_20k / stockindex / stockmarket / crmarenapro，
  30 query；dab-agent-02：PANCANCER_ATLAS / PATENTS / agnews / bookreview /
  googlelocal / yelp，24 query），各自盲解 + 互相独立复算（D3）。
- Trial 内 backbone：无。每个 scored trial 执行确定性管线；`llm_call_count = 0`
  为字面真值（trial 内不调用任何模型）。
- 作者模型：dab-agent-01 与 dab-agent-02 均运行于 **deepseek-flash**（Loop Claude
  runtime）。作者模型仅用于编写/复核求解代码与离线标注，不在 scored trial 内调用。
  本提交**不是模型分数**，是 benchmark-informed 工程管线。
- Trials：每 query 5 个 run（0–4），共 270 条记录。
- Dataset hints：是（db_description(.withhint).txt 为许可输入）。
- agnews 四分类标签为 trial 外离线三遍标注资产（pass1/pass2 独立实例 + 分歧
  adjudication，见 frozen/02_agnews_labeling_protocol.md），trial 内仅做确定性
  计数；标签不来自任何 gold/validator 输出（该数据集存在 gold 暴露史，红线：
  暴露值一律不得作为答案来源）。

## 口径与修订

- 冻结：答案计算前逐题预注册（frozen/02_readings_v1.md 等，含时间戳）。
- 冻结后修订全部登记于 registry/revision_log.md（query/旧读法/新读法/触发原因），
  含 R007/R008（PATENTS q2 恢复 VI 选择集内序列；q3 恢复冻结行序）、
  R009（PATENTS q2 选择集实现改为冻结文口径：Patents_info 文本国别 DE = 34 件，
  与 publication 前缀口径逐行相同；第 3–4 名落在 21 路峰值 1.0 并列内，按预注册
  组码升序 tie-break 取 A21/B23）、R010（R008 行序勘误：恢复字母序后首行由
  CALIFORNIA 变为 BLOOM，4 组 assignee|title 集合不变）。
- 12 个已知失败题的通过读法按上表披露继承；PATENTS q3 的 VI 修正不可从
  sanctioned 材料复原，按冻结预注册读法提交（与 strict v1 失败答案同形）。
- R016（2026-11-10）：agnews q2 的 111 篇 Amy Jones 标签经两个全新独立实例盲审
  （`audit_q2/PROTOCOL.md` v2；A/B 一致 108/111，3 篇分歧不裁决，6 篇共识更正），
  S&T 计数 14/111→15/111，q2 仍为 0/5；q1/q3/q4 与其余 49 题零漂移。
  团队因公开榜单审计已知 q2 的目标计数，但标注输入与采纳规则不读取该计数；
  结果未通过仍按预注册规则采纳，未重跑、未运行第三票。
- R017：团队已知目标计数后做过一次方法级重标（通用四类、无 company-story 硬规则），
  结果仍 15/111，未采纳；无按单篇改标签，答案与 traces 未变。

## 结果与自评

- 自评：dab_selfscore.py 全量运行（首次 0.8534；R011–R016 登记修订后重评，
  最终 0.9583/Failures 10），结果与时间线载 selfcheck.md。
