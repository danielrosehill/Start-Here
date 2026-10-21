---
name: clone-repos
description: Download Daniel Rosehill's GitHub repositories — one repo, a filtered set (by topic, keyword or date), or a single file — by clone, shallow clone, tarball or raw fetch. Use when asked to "grab", "pull down", "clone" or "get the code for" his projects, or to read one file from a repo without cloning it.
---

# Download repos

Pick the lightest method that does the job. Most of the time you need to *read*
a repo, not to work in it, and that does not need a full clone.

| Need | Method |
| --- | --- |
| Read one file | Raw fetch — no clone |
| Read or search a repo's code | Shallow clone (`--depth 1`) |
| Work in it, commit, see history | Full clone |
| No git available | Tarball from codeload |
| Several repos | Build the list from the index, then loop |

## One file

```bash
curl -sL https://raw.githubusercontent.com/danielrosehill/<Repo>/main/README.md
# default branch isn't always main:
gh api repos/danielrosehill/<Repo> --jq .default_branch
# via the API instead (works for any branch name):
gh api repos/danielrosehill/<Repo>/contents/<path> --jq .content | base64 -d
```

## One repo

```bash
git clone --depth 1 https://github.com/danielrosehill/<Repo>.git     # read-only look
gh repo clone danielrosehill/<Repo>                                  # full, uses gh auth
curl -sL https://codeload.github.com/danielrosehill/<Repo>/tar.gz/HEAD | tar xz   # no git
```

## A filtered set

Build the list from Start-Here's `repositories.json` rather than
`gh repo list` — it is already filtered to public repos and needs no auth. Use
the `find-repo` skill's `search.py`, or jq:

```bash
mkdir -p danielrosehill-repos && cd danielrosehill-repos
curl -s https://raw.githubusercontent.com/danielrosehill/Start-Here/main/repositories.json \
  | jq -r '.[] | select(any(.repositoryTopics[]?; .name == "mcp")) | .name' \
  | while read -r name; do
      [ -d "$name" ] || git clone --depth 1 -q "https://github.com/danielrosehill/$name.git"
    done
```

To take everything from a topic index instead, pull the repo links out of that
index's README (see the `find-index` skill):

```bash
gh api repos/danielrosehill/<Index>/readme --jq .content | base64 -d \
  | grep -oE 'github\.com/danielrosehill/[A-Za-z0-9._-]+' | sort -u | cut -d/ -f3
```

## Before cloning many

- **Say how many first.** There are 1,000+ public repos; confirm the count with
  the user before cloning more than a few dozen, and default to `--depth 1`.
- **Clone into a dedicated folder** and skip names that already exist, so a
  re-run resumes instead of failing.
- **Expect a few failures.** The snapshot is periodic, so a repo may since have
  been deleted, renamed or made private. Log and continue; do not stop the loop.
- **Unauthenticated limits.** Raw and codeload fetches are not API calls, but
  `gh api` without auth is capped at 60 requests/hour. Use `gh auth status` and
  `git clone` for bulk work.
