# Phoenix-CLI tuned v3: every note in the prompt

Each run's system prompt is the base prompt of our untuned entry #114, then `common.md`, then its dataset's note (`<dataset>.md`) if one exists, then its query's note (`<dataset>/queryN.md`) if one exists, each separated by a blank line. A query gets no note written for any other query. Every run's `isolation.json` lists the files it received with their sha256 (checked: all 270 runs received exactly the files below for their query, with these hashes).

These are the v3 notes, used for all 270 runs. Earlier versions, and the withdrawn v3 agnews q2 candidate, are in `runner_tools.tar.gz` in the release.

## `common.md` (every query), sha256 `146597048ce0e805690a5759f4705095177723cfd569f7441eed6aad427dad3d`

```text
ANSWER DISCIPLINE
- Run every command in the foreground and wait for its result. Write the FINAL ANSWER
  only after all computation has finished.
- The FINAL ANSWER line carries the complete answer: every item of a requested list,
  each with every field the question asks for. Do not shorten a list to examples.
- Before concluding that an entity has no data, confirm it: a table or collection
  listing can be long, so count it or look the entity up by name directly.
- dab_db prints at most 200 rows, then "... N more rows truncated (M total)". Exactly 200
  rows, or that line, means the result is INCOMPLETE: filter, join or aggregate in SQL
  instead, or page with ORDER BY on every selected column (LIMIT/OFFSET without ORDER BY
  can drop and repeat rows).
- Never split a delimited dump on a character the data can contain (some titles hold
  "|"); use char(30)/char(31) as separators or fetch the columns separately.
```

## `stockmarket.md` (dataset stockmarket), sha256 `ad07770f1e2771d02650e3ec103aaf2143115b8089f431c8686225692be7375b`

```text
PRICE DATA
- Each security's daily prices are a table named by its symbol in the trading
  database. Get the complete table list, or query a candidate symbol's table directly;
  never treat a partial listing as the set of securities that have prices.
```

## `agnews/query2.md` (agnews q2), sha256 `593ced4afae0e318d58dfe8ea28ac7ebbe77e21e49f4e7074640b35ae8206e1d`

```text
CATEGORY LABELS (this dataset stores no category; you assign one per article)
- Label articles one at a time by reading each title and description yourself. Do not
  use keyword rules or a trained classifier for the articles the answer depends on.
- Every article gets exactly one of World, Sports, Business, Science/Technology, chosen
  by the story's main subject:
  - Business: companies as businesses (earnings, deals, mergers, layoffs, executives,
    lawsuits, share prices, IPOs), markets, the economy, trade, oil and prices. This
    holds when the company is a technology company: a story about a tech firm's
    results, deal or stock is Business.
  - Science/Technology: the technology or science itself: computing, software, the
    internet, products and how they work, security flaws and viruses, space, research
    and discoveries, health and medical science.
  - World: international affairs, politics, government, elections, conflict, crime and
    disasters, outside sport.
  - Sports: athletes, teams, games, leagues and sporting events.
- Label each of the qualifying articles in three independent passes (do not consult an
  earlier pass while labeling) and count each article under its majority label; if all
  three passes differ, re-read the article and decide.
```

## `agnews/query3.md` (agnews q3), sha256 `31876e5b209161183e3cb144a8dd2e06aec2d0f3fd4f2cbd6679616c530256c3`

```text
This question covers thousands of articles. Choose a method that finishes inside the
time budget; an answer computed on all qualifying articles is required.
```

## `crmarenapro/query2.md` (crmarenapro q2), sha256 `4ce53fe077ed0ccab21df5a85bec06d843ea144d6f19f8b9bf5642635ca36d2d`

```text
- "Cost and setup" means the quote's pricing (line discounts) and its installation or
  setup terms. Which products a quote bundles is not what this question checks.
- The tiers in the Volume-Based Discounts article are unit quantities per line item,
  not dollar amounts: compare each line's discount with the tier its quantity reaches.
```

## `crmarenapro/query3.md` (crmarenapro q3), sha256 `3cde7b4991c5f6a3289119264a416c5f6dbdc47f059dd17badfdce841cf17d48`

```text
- The stage an opportunity's tasks represent is the stage of its most advanced task
  (stage order: Qualification, Discovery, Quote, Negotiation, Closed), counting every
  task on the opportunity whether or not it has started.
```

## `crmarenapro/query7.md` (crmarenapro q7), sha256 `14107cb7e484f6e7f3a8239305ee026d5b5b66b6770c20d0871ce4af71d8b4c7`

```text
- When the agent recommended a solution that a knowledge article covers, first check the
  conditions that article sets for offering it (eligibility, timing and validity
  windows). Breaking those conditions is the breach this question asks about.
```

## `crmarenapro/query8.md` (crmarenapro q8), sha256 `e2a44d7ca575cbb04ed6c96c991feac3a70e386cbadacec7ff175340ef40c0e1`

```text
- "Fewest transfer counts among agents who handled cases" ranks the agents that
  transferred at least one case in the window. An agent with zero transfers made no
  transfers to count and is not a candidate.
```

## `crmarenapro/query12.md` (crmarenapro q12), sha256 `5ae4a5a48233616af0670afc3b0e46b546d4881c3d19aa7a4341efae3a52cc51`

```text
- An opportunity "closes" on its contract's company signed date (the end point the
  sales cycle policy defines). "In April 2023" selects opportunities whose company
  signed date falls in April 2023. Turnaround = days from the opportunity's created
  date to that signed date; average per owner (agent).
```

## `crmarenapro/query13.md` (crmarenapro q13), sha256 `3f3da63f2efd744dba1d5397befdb91c290238a66ce51aaf0b81376f9a5af9c7`

```text
- "Top sales for orders" is an ORDER question: sales per agent = SUM(OrderItem.Quantity *
  OrderItem.UnitPrice) over orders whose Order.EffectiveDate falls in the window, grouped
  by Order.OwnerId. The contract-signed-date sentence in the policy governs opportunities;
  do not credit Opportunity owners here.
- Clean ids on both sides of every join (trim '#' and blanks) and return the cleaned id.
```

## `DEPS_DEV_V1/query1.md` (DEPS_DEV_V1 q1), sha256 `6212eb6ce8813c956fdbb96008a3f9e5e7f3846aa9c386cbd1b2b79b04417715`

```text
- A package name can contain ">" (a nested dependency path). Each distinct stored name
  is its own package; keep such names whole and in the ranking.
- When several packages tie at a rank, still name one concrete package (with its
  version) for that rank, and say that it is tied.
- packageinfo stores rows more than once: select DISTINCT. A package's latest release is
  its IsRelease row with the highest VersionInfo Ordinal.
- Fetch every candidate row: when paging, ORDER BY every selected column. Rank on the
  complete set; a package missing from a partial fetch is not evidence it is unmapped.
```

## `GITHUB_REPOS/query1.md` (GITHUB_REPOS q1), sha256 `face8387edbb12552c58c1cddbee3f6d84f2b1a5511b4a3afb39ad9d0a952a6f`

```text
- The repository's README.md files are the rows of the files table whose path is
  README.md (at any folder depth). A file's text is the contents row with the same id:
  join files.id = contents.id. Do not identify README files from contents.sample_path.
- Give the proportion as a decimal fraction (for example 0.25), followed by the
  numerator and denominator.
```

## `GITHUB_REPOS/query2.md` (GITHUB_REPOS q2), sha256 `66263b8e82a97dbed102d314bc28fcb06d5355df70a20ab0ac7bbec6ce4ff8d3`

```text
- Only files whose id appears in the files table qualify, as the question says; a
  Swift file found only in contents is not a candidate.
- The answer names the repository AND the file: its path, its id and its copy count.
```

## `GITHUB_REPOS/query4.md` (GITHUB_REPOS q4), sha256 `389df46316de1487780a71480b793854c53bbae3369b06cf297daba507a1ff11`

```text
- A repository's main language is the language with the most bytes in its own languages
  row. A repository with no languages row of its own has no main language, so "not
  Python" cannot be established for it and it is not a candidate (a fork's row is not
  the original's).
- Match repo names case-insensitively between tables.
```

## `googlelocal/query2.md` (googlelocal q2), sha256 `1b6e20acb779ebbbe6e2ee206321efa380e0a1963963a31f27fb1f148bc66f11`

```text
- A massage therapy business is any business whose name, category, description or
  reviews show that it provides massage or bodywork, whether or not its name contains
  the word "massage".
```

## `music_brainz_20k/query3.md` (music_brainz_20k q3), sha256 `1760054fdf55f4082b616ff6b6c11563f33298511c2514bd48a61d22a427ae05`

```text
- Resolve duplicate track rows into songs before summing revenue: variants include a
  numeric prefix ("NNN-Title"), "Artist - Title" with the artist field blank, an album
  name appended to the title ("Title - Album", "Title (Album)"), album typos and
  truncated artist names. A remix or version tag is part of the song: different mixes
  are different songs.
- Print the top clusters with their member tracks and check each before answering.
```

## `PANCANCER_ATLAS/query1.md` (PANCANCER_ATLAS q1), sha256 `6f1a3823d81663a91541abc7f842f618876d5b973fe13891effc9cd41dacc73c`

```text
- Report one average per histology type, keyed by the histology code as stored in the
  clinical data (the ICD-O-3 morphology code of the form NNNN/N), not by a type name.
```

## `PATENTS/query2.md` (PATENTS q2), sha256 `fa0d81612b44fbc8f4b1f4a8686883b3a71ea710d55c179be3808af9c3ffe406`

```text
- Exponential moving average per CPC group over consecutive filing years (years with
  no filings count as zero): the first year's value is that year's count, then
  EMA = 0.1 x count + 0.9 x previous EMA. If several years share the highest EMA,
  report the earliest.
```

## `PATENTS/query3.md` (PATENTS q3), sha256 `be15171d549c6cffb1625a1f56598c8a36b3451b22d1f14998e0c00c8ce0049f`

```text
- "UNIV CALIFORNIA" is the assignee whose name is exactly that; assignees whose names only
  start with it (campuses or units named after it) are different assignees.
- Compute the answer in ONE SQL query that joins the UNIV CALIFORNIA publications to the
  rows citing them; do not dump the publication list and filter it by hand (the list is
  longer than one dab_db page). Primary CPC = the cpc entry with first = true; subclass =
  its first 4 characters; title = cpc_definition titleFull for that symbol. List every
  citing assignee once per distinct subclass and leave UNIV CALIFORNIA itself out.
```

## `stockmarket/query4.md` (stockmarket q4), sha256 `209931ff85f0aac18d3628f268773fa4d56d2e96fb544b49858642200c92564b`

```text
- Qualify stocks on up days > down days in 2017 (up: Close > Open, down: Close < Open),
  then rank the qualifiers by the margin (up days minus down days), largest first.
- Answer with company names from stockinfo, in rank order.
```
