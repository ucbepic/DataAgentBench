# DEPS_DEV_V1 冻结口径（预注册）

- 冻结时间：2026-11-09T06:30:00Z（作者：dab-agent-01；cross-checker：dab-agent-02 待复算）
- 知识来源：附录 A3（DEPS 条目）与 strict 基线描述（sanctioned stores 表）；方案乙 benchmark-informed。
- Sanctioned stores：`package_query.db`(SQLite: packageinfo)、`project_query.db`(DuckDB: project_info, project_packageversion)。

## q1（top 5 by stars, latest release per package）
- 过滤：packageinfo 全表 System='NPM'（实际全表即 NPM）。
- "latest release"：对每个 distinct Name，取 IsRelease=true 的行中 VersionInfo.Ordinal 最大者（Ordinal 无 null）。
- join：packageinfo(System,Name,Version) → project_packageversion 同键 → ProjectName → project_info（ProjectName 从 Project_Information 文本解析 "The project <X> is hosted on GitHub"）。
- 聚合：按 GitHub stars 降序取前 5 个 package-version（不去重 project；同一 project 可多次入榜）。
- tie-break：stars 相同按 Ordinal 降序，再按 Name 字母序。
- 输出格式（继承 strict 帧式）：
  `N. <package Name> (<version>) - <stars> GitHub stars [<ProjectName>]`，5 行。

## q2（top 5 projects by forks；VI 读法〔附录 A3：项目级 MIT + 任一 release 即计〕）
- 项目级 license：project_info.Licenses JSON 数组恰为 ["MIT"]（"project license 'MIT'"指被链接 project 的 license）。
- "marked as release"：包级判定——该 NPM 包在 packageinfo 中存在任一 IsRelease=true 的版本行即计。
- join：满足上述的包，经 project_packageversion 任意版本行链接到 ProjectName（链接行本身不要求是 release），再到 project_info。
- 聚合：distinct project，按 forks 降序取前 5。
- tie-break：forks 相同按 ProjectName 字母序。
- 输出格式（继承 strict 帧式）：
  `N. <ProjectName> - <forks> GitHub forks`，5 行。

## 解析细节（两题共用）
- stars/forks 解析：Project_Information 正则 `(\d+) open issues, (\d+) stars, and (\d+) forks`；无 stars 的 31 行不参与排名（视为无指标，跳过并计数记录）。
- VersionInfo 为 JSON 字符串：IsRelease、Ordinal 用 json 解析，不子串匹配。
- packageinfo.Name 含 `>` 的依赖链记法原样保留，不做拆分。
