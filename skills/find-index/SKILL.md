---
name: find-index
description: Find the curated index repository Daniel Rosehill keeps for a subject (AI agents, Hebrew language, Israel, speech tech, Claude Code projects, procurement and more) and read it. Use when the question is "what has Daniel built about X", "show me his projects on Y", or when a keyword search over his repos returns too much noise.
---

# Find a topic index

Alongside his individual repos, Daniel keeps ~65 **index repositories** — each a
hand-curated README listing his projects (and sometimes other people's) on one
subject. When the question is about a subject, an index beats a keyword search:
it is curated, grouped and annotated.

The list of indexes is
[`indexing-repos.json`](https://raw.githubusercontent.com/danielrosehill/Start-Here/main/indexing-repos.json)
in Start-Here, synced from
[danielrosehill/Subindices](https://github.com/danielrosehill/Subindices) (the
index of indexes).

```json
{"source": "https://github.com/danielrosehill/Subindices",
 "synced_at": "2026-10-15T07:47:35Z",
 "indices": [{"title": "Speech-Tech-Index", "description": "...",
              "url": "https://github.com/danielrosehill/Speech-Tech-Index"}]}
```

## Steps

1. **List or search the indexes.**

   ```bash
   # search (script lives in the find-repo skill)
   python3 ../find-repo/scripts/search.py "speech" --indexes
   # or everything
   curl -s https://raw.githubusercontent.com/danielrosehill/Start-Here/main/indexing-repos.json \
     | jq -r '.indices[] | "\(.title)\t\(.description)"'
   ```

   Index titles are short; read the descriptions, and scan the full list when the
   subject is broad — there are only ~65, so this is cheap.

2. **Read the index's README** — that is where the content is.

   ```bash
   gh api repos/danielrosehill/Speech-Tech-Index/readme --jq .content | base64 -d
   # or
   curl -sL https://raw.githubusercontent.com/danielrosehill/Speech-Tech-Index/main/README.md
   ```

   Some indexes also ship a machine-readable file (`index.json`, `repos.json`,
   `data/*.json`). Check the file listing before parsing markdown:
   `gh api repos/danielrosehill/<Index>/contents --jq '.[].name'`.

3. **Answer from the index, then follow links** into the individual repos if the
   user needs detail.

## Traps

- **No index ≠ no projects.** Many subjects have repos but no index. If nothing
  fits, fall back to the `find-repo` skill.
- **Indexes overlap.** A Hebrew speech repo may appear in both the Hebrew and the
  speech indexes. Check both before saying a list is complete.
- **Some index names are old.** Several were renamed and their old slugs redirect
  (e.g. `Index-Of-Indices` → `Subindices`, `Github-Master-Index` and `Index` →
  `Start-Here`). Use the URL from `indexing-repos.json` and resolve with
  `gh api repos/danielrosehill/<Name> --jq .full_name` before citing a name.
