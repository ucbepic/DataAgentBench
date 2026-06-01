# dab

**Run ID:** `dab-1780210698`

## Score

- Overall: 0.58
- Tasks: 54
- Trials: 270
- Passes: 175

## Score by Dimension

### dataset

- agnews: 0.95
- bookreview: 0.93
- crmarenapro: 0.82
- deps_dev_v1: 0.10
- github_repos: 0.50
- googlelocal: 0.50
- music_brainz_20k: 0.07
- pancancer_atlas: 0.67
- patents: 0.00
- stockindex: 1.00
- stockmarket: 0.80
- yelp: 0.63

## Failures

- `deps_dev_v1:1` (trial 0): Missing name: @dmrvos/infrajs>0.0.6>typescript
- `deps_dev_v1:1` (trial 1): Missing name: @dmrvos/infrajs>0.0.6>typescript
- `deps_dev_v1:1` (trial 2): Missing name: @dmrvos/infrajs>0.0.6>typescript
- `deps_dev_v1:1` (trial 3): Missing name: @dmrvos/infrajs>0.0.6>typescript
- `deps_dev_v1:1` (trial 4): Missing name: @dmrvos/infrajs>0.0.6>typescript
- `deps_dev_v1:2` (trial 0): Missing project name: react-native-elements/react-native-elements
- `deps_dev_v1:2` (trial 2): Missing project name: moment/moment
- `deps_dev_v1:2` (trial 3): Missing project name: mui-org/material-ui
- `deps_dev_v1:2` (trial 4): Missing project name: mui-org/material-ui
- `github_repos:1` (trial 0): No value in LLM output rounds to 0.33
- `github_repos:1` (trial 1): No value in LLM output rounds to 0.33
- `github_repos:1` (trial 2): No value in LLM output rounds to 0.33
- `github_repos:1` (trial 3): No value in LLM output rounds to 0.33
- `github_repos:1` (trial 4): No value in LLM output rounds to 0.33
- `github_repos:2` (trial 0): No fuzzy match found for 'swiftandroid/swift' within 3-character distance
- `github_repos:2` (trial 1): No fuzzy match found for 'swiftandroid/swift' within 3-character distance
- `github_repos:2` (trial 2): No fuzzy match found for 'swiftandroid/swift' within 3-character distance
- `github_repos:2` (trial 3): No fuzzy match found for 'swiftandroid/swift' within 3-character distance
- `github_repos:2` (trial 4): No fuzzy match found for 'swiftandroid/swift' within 3-character distance
- `pancancer_atlas:1` (trial 0): Missing histology type: 9382/3
- `pancancer_atlas:1` (trial 1): Missing histology type: 9382/3
- `pancancer_atlas:1` (trial 2): Missing histology type: 9382/3
- `pancancer_atlas:1` (trial 3): Missing histology type: 9382/3
- `pancancer_atlas:1` (trial 4): Missing histology type: 9382/3
- `patents:1` (trial 0): Missing CPC code: A22B
- `patents:1` (trial 1): Missing CPC code: A22B
- `patents:1` (trial 2): Missing CPC code: A23P
- `patents:1` (trial 3): Missing CPC code: A22B
- `patents:1` (trial 4): Missing CPC code: A22B
- `patents:2` (trial 2): Name fuzzy match failed for 'BAKING; EDIBLE DOUGHS' (best match: 'eaingermanywiththe', distance=13)
- `patents:2` (trial 4): Name fuzzy match failed for 'BAKING; EDIBLE DOUGHS' (best match: 'rmaninventorcountr', distance=13)
- `patents:3` (trial 0): No match for: ABBOTT RYAN + DIAGNOSIS; SURGERY; IDENTIFICATION
- `patents:2` (trial 1): Name fuzzy match failed for 'BAKING; EDIBLE DOUGHS' (best match: 'hangewiththehighes', distance=12)
- `patents:2` (trial 3): Name fuzzy match failed for 'BAKING; EDIBLE DOUGHS' (best match: 'easingermanyforpat', distance=12)
- `patents:3` (trial 1): No match for: ABBOTT RYAN + DIAGNOSIS; SURGERY; IDENTIFICATION
- `patents:3` (trial 2): No match for: ABBOTT RYAN + DIAGNOSIS; SURGERY; IDENTIFICATION
- `patents:3` (trial 3): No match for: ABBOTT RYAN + DIAGNOSIS; SURGERY; IDENTIFICATION
- `patents:3` (trial 4): No match for: ABBOTT RYAN + DIAGNOSIS; SURGERY; IDENTIFICATION
- `agnews:4` (trial 2): Ground truth 'Africa' not found in LLM output: The region that published the largest number of articles in the World category in 2015 was **South America**, with **15 articles**.

South America
- `bookreview:3` (trial 2): Missing book title in LLM output: Pokémon: Sun & Moon, Vol. 8 (8)
- `patents:2` (trial 0): Name fuzzy match failed for 'BAKING; EDIBLE DOUGHS' (best match: 'indingsmethodology', distance=13)
- `crmarenapro:12` (trial 0): Found agent IDs ['005Wt000003NEa3IAG', '005Wt000003NEa3IAG'], but expected '005Wt000003NDEBIA4'
- `crmarenapro:12` (trial 1): Found agent IDs ['005Wt000003NEa3IAG', '005Wt000003NEa3IAG'], but expected '005Wt000003NDEBIA4'
- `crmarenapro:12` (trial 2): Found agent IDs ['005Wt000003NEa3IAG', '005Wt000003NEa3IAG'], but expected '005Wt000003NDEBIA4'
- `crmarenapro:12` (trial 3): Found agent IDs ['005Wt000003NEa3IAG'], but expected '005Wt000003NDEBIA4'
- `crmarenapro:12` (trial 4): Found agent IDs ['005Wt000003NEa3IAG', '005Wt000003NEa3IAG'], but expected '005Wt000003NDEBIA4'
- `crmarenapro:2` (trial 0): Found knowledge article IDs ['ka0Wt000000Ens5IAC', 'ka0Wt000000Ens5IAC'], but expected 'ka0Wt000000Eq0MIAS'
- `crmarenapro:2` (trial 1): Found knowledge article IDs ['ka0Wt000000Ens5IAC'], but expected 'ka0Wt000000Eq0MIAS'
- `crmarenapro:2` (trial 3): Found knowledge article IDs ['ka0Wt000000Ens5IAC', 'ka0Wt000000Ens5IAC'], but expected 'ka0Wt000000Eq0MIAS'
- `crmarenapro:2` (trial 4): Found knowledge article IDs ['ka0Wt000000Ens5IAC', 'ka0Wt000000Ens5IAC'], but expected 'ka0Wt000000Eq0MIAS'
- `crmarenapro:6` (trial 3): Found knowledge article IDs ['ka0Wt000000Eq0MIAS', 'ka0Wt000000Eq0MIAS'], but expected 'ka0Wt000000EnwvIAC'
- `crmarenapro:7` (trial 1): Found knowledge article IDs ['ka0Wt000000EpSUIA0', 'ka0Wt000000EpSUIA0'], but expected 'ka0Wt000000EoD3IAK'
- `crmarenapro:7` (trial 3): Found knowledge article IDs ['ka0Wt000000EpSUIA0'], but expected 'ka0Wt000000EoD3IAK'
- `googlelocal:2` (trial 0): Missing name in LLM output: J B Oriental Inc
- `googlelocal:2` (trial 1): Missing name in LLM output: J B Oriental Inc
- `googlelocal:2` (trial 2): Missing name in LLM output: J B Oriental Inc
- `googlelocal:2` (trial 3): Missing name in LLM output: J B Oriental Inc
- `googlelocal:2` (trial 4): Missing name in LLM output: J B Oriental Inc
- `googlelocal:3` (trial 0): Missing business name: Mariscos el poblano
- `googlelocal:3` (trial 1): Missing hours [Thursday, Closed] for business: TACOS LA CABANA
- `googlelocal:3` (trial 2): Missing hours [Thursday, Closed] for business: TACOS LA CABANA
- `googlelocal:3` (trial 3): Missing hours [Thursday, Closed] for business: TACOS LA CABANA
- `googlelocal:3` (trial 4): Missing business name: Mariscos el poblano
- `music_brainz_20k:1` (trial 0): Ground truth '1059.46' not found in LLM output: Apple Music made **$601.44 USD** from Beyoncé's 'Get Me Bodied' in Canada.

**601.44**
- `music_brainz_20k:1` (trial 1): Ground truth '1059.46' not found in LLM output: Apple Music made **$601.44 USD** from Beyoncé's song 'Get Me Bodied' in Canada.

$601.44
- `music_brainz_20k:1` (trial 2): Ground truth '1059.46' not found in LLM output: The query joined the tracks database on `track_id`, filtered for Beyoncé's "Get Me Bodied", Canada, and Apple Music, then summed the revenue.

**$601.44**
- `music_brainz_20k:1` (trial 3): Ground truth '1059.46' not found in LLM output: Apple Music made **$601.44 USD** from Beyoncé's song 'Get Me Bodied' in Canada.

**601.44**
- `music_brainz_20k:1` (trial 4): Ground truth '1059.46' not found in LLM output: Apple Music made **$601.44 USD** from Beyoncé's 'Get Me Bodied' in Canada.

**601.44**
- `music_brainz_20k:2` (trial 0): Ground truth 'iTunes' not found in LLM output: The query returned clear results. Amazon Music earned $304.13 in total revenue from Brucqe Maginnis' song 'Street Hype' across all countries, compared to Apple Music's $47.52.

**Amazon Music**
- `music_brainz_20k:2` (trial 2): Ground truth 'iTunes' not found in LLM output: The query returns clear results. **Amazon Music** earned the most revenue from Brucqe Maginnis' song 'Street Hype' across all countries, with **$304.13 USD** (compared to Apple Music at $47.52).

Amazon Music
- `music_brainz_20k:2` (trial 3): Ground truth 'iTunes' not found in LLM output: The query returned results. Amazon Music earned $304.13, far ahead of Apple Music at $47.52.

**Amazon Music**
- `music_brainz_20k:2` (trial 4): Ground truth 'iTunes' not found in LLM output: The query found the track by Brucqe Maginnis titled 'Street Hype' and aggregated revenue by store across all countries.

**Amazon Music** earned the most revenue in USD from 'Street Hype' by Brucqe Maginnis, with **$304.13** across all countries (compared to Apple Music's $47.52).

Amazon Music
- `music_brainz_20k:3` (trial 0): No fuzzy match (Zo gaat het leven aan je voor) found in The song **"Systemisch bled"** by **Stüngö** generated the highest total revenue at **$2,522.82 USD** across all stores and countries.

Systemisch bled. Best score: 0.28
- `music_brainz_20k:3` (trial 1): No fuzzy match (Zo gaat het leven aan je voor) found in The song **"Systemisch bled"** by **Stüngö** generated the highest total revenue with **$2,522.82 USD** across all stores and countries.

**Systemisch bled**. Best score: 0.27
- `music_brainz_20k:3` (trial 2): No fuzzy match (Zo gaat het leven aan je voor) found in The song **"Systemisch bled"** by **Stüngö** generated the highest total revenue at **$2,522.82 USD** across all stores and countries.

Systemisch bled. Best score: 0.28
- `music_brainz_20k:3` (trial 3): No fuzzy match (Zo gaat het leven aan je voor) found in The song **"Systemisch bled"** by Stüngö generated the highest total revenue with **$2,522.82 USD** across all stores and countries.

Systemisch bled. Best score: 0.27
- `music_brainz_20k:3` (trial 4): No fuzzy match (Zo gaat het leven aan je voor) found in The song **"Systemisch bled"** by **Stüngö** generated the highest total revenue, with **$2,522.82 USD** across all stores and countries.

**Systemisch bled**. Best score: 0.27
- `stockmarket:3` (trial 1): Number near 'BIO-key International, Inc' does not match rounded 10988
- `stockmarket:3` (trial 3): Name not found within 5 edits: 'Synthesis Energy Systems, Inc', closest: 'sunesis pharmaceuticals, inc' (distance=16)
- `stockmarket:3` (trial 4): Name not found within 5 edits: 'Synthesis Energy Systems, Inc', closest: 'sunesis pharmaceuticals, inc' (distance=16)
- `stockmarket:4` (trial 3): Name not found within 5 edits: 'MFA Financial, Inc', closest: 'rnational, inc' (distance=8)
- `stockmarket:5` (trial 4): Name not found within 5 edits: 'Synthesis Energy Systems, Inc', closest: 'spi | spi energy co., l' (distance=17)
- `yelp:2` (trial 0): No occurrence of 3.7 near PA/Pennsylvania.
- `yelp:2` (trial 2): No occurrence of 3.7 near PA/Pennsylvania.
- `yelp:2` (trial 3): No occurrence of 3.7 near PA/Pennsylvania.
- `yelp:2` (trial 4): No occurrence of 3.7 near PA/Pennsylvania.
- `yelp:3` (trial 1): Number 35 not found in LLM output.
- `yelp:3` (trial 4): Number 35 not found in LLM output.
- `yelp:4` (trial 0): Value '3.63' not found in LLM output.
- `yelp:4` (trial 2): Value '3.63' not found in LLM output.
- `yelp:4` (trial 3): Value '3.63' not found in LLM output.
- `yelp:7` (trial 2): Missing category: Restaurants
- `yelp:7` (trial 3): Missing category: Breakfast & Brunch
- `yelp:4` (trial 4): Value '3.63' not found in LLM output.
- `yelp:7` (trial 1): Missing category: Breakfast & Brunch

## Config

```json
{
  "n_trials": 5,
  "task_filter": [
    "deps_dev_v1:1",
    "deps_dev_v1:2",
    "github_repos:1",
    "github_repos:2",
    "github_repos:3",
    "github_repos:4",
    "pancancer_atlas:1",
    "pancancer_atlas:2",
    "pancancer_atlas:3",
    "patents:1",
    "patents:2",
    "patents:3",
    "agnews:1",
    "agnews:2",
    "agnews:3",
    "agnews:4",
    "bookreview:1",
    "bookreview:2",
    "bookreview:3",
    "crmarenapro:1",
    "crmarenapro:10",
    "crmarenapro:11",
    "crmarenapro:12",
    "crmarenapro:13",
    "crmarenapro:2",
    "crmarenapro:3",
    "crmarenapro:4",
    "crmarenapro:5",
    "crmarenapro:6",
    "crmarenapro:7",
    "crmarenapro:8",
    "crmarenapro:9",
    "googlelocal:1",
    "googlelocal:2",
    "googlelocal:3",
    "googlelocal:4",
    "music_brainz_20k:1",
    "music_brainz_20k:2",
    "music_brainz_20k:3",
    "stockindex:1",
    "stockindex:2",
    "stockindex:3",
    "stockmarket:1",
    "stockmarket:2",
    "stockmarket:3",
    "stockmarket:4",
    "stockmarket:5",
    "yelp:1",
    "yelp:2",
    "yelp:3",
    "yelp:4",
    "yelp:5",
    "yelp:6",
    "yelp:7"
  ]
}
```