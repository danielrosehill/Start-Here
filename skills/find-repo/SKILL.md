---
name: find-repo
description: Find one of Daniel Rosehill's GitHub repositories by name, subject, GitHub topic or date, without crawling his profile. Use when asked to locate "Daniel's repo for X", check whether he has a project on a subject, list his recent repos, or resolve a half-remembered repo name to its URL.
---

# Find a repo

Daniel has 1,000+ public repositories. Don't page through
`github.com/danielrosehill?tab=repositories` and don't guess URLs — the whole
public set is already indexed as JSON in
[danielrosehill/Start-Here](https://github.com/danielrosehill/Start-Here).

## Fast path: the search script

`scripts/search.py` (next to this file) is standard-library Python. It fetches
`repositories.json` from GitHub and ranks repos against a query, weighting name
over topics over description. Output is JSON.

```bash
python3 scripts/search.py "hebrew speech"            # ranked matches
python3 scripts/search.py "mcp" --topic mcp          # must carry the GitHub topic
python3 scripts/search.py --since 2026-09-01 --limit 30   # newest first, no query
python3 scripts/search.py "label printer" --local ~/repos/indexing-repos/Index
```

Each result: `name`, `url`, `description`, `topics`, `created`, `updated`,
`stars`, `score`. `total_indexed` tells you how big the set was.

## Without the script

```bash
curl -s https://raw.githubusercontent.com/danielrosehill/Start-Here/main/repositories.json \
  | jq -r '.[] | select((.name + " " + (.description // "")) | test("whisper|asr"; "i"))
                | "\(.name)\t\(.url)\t\(.description)"'
```

`repositories.json` is an array of objects shaped like:

```json
{"name": "Subindices", "url": "https://github.com/danielrosehill/Subindices",
 "description": "...", "repositoryTopics": [{"name": "repository-index"}],
 "createdAt": "2025-11-26T09:46:37Z", "updatedAt": "2026-08-10T19:04:46Z",
 "stargazerCount": 3, "forkCount": 0, "isPrivate": false}
```

## Search well

- **Try synonyms.** Names are inconsistent: speech work may say `ASR`, `STT`,
  `Whisper`, `transcription` or `dictation`. Run two or three phrasings before
  concluding there is nothing.
- **Check for a topic index first** when the question is about a subject rather
  than a single repo — a curated index is better than a keyword hit list. See
  the `find-index` skill.
- **Fall back to live GitHub** when the snapshot misses: the JSON is regenerated
  periodically, not live, so a repo created in the last few weeks may be absent.
  `gh search repos --owner danielrosehill <terms>` or
  `gh repo view danielrosehill/<Name>` settles it.

## Traps

- **Public repos only.** Private repos are never in the index. "Not found" means
  "not public", not "doesn't exist" — say so rather than asserting absence.
- **Forks are included.** Check `forkCount`/the repo page if it matters whether
  Daniel wrote it.
- **Renamed repos answer on the old name.** GitHub redirects old slugs
  indefinitely, so an old URL returns 200. Compare `full_name` from
  `gh api repos/danielrosehill/<Name> --jq .full_name` with what you asked for
  before citing a name.
