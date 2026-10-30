# Start Here

![Banner](banners/index.png)


Hi, I'm [Daniel Rosehill](https://danielrosehill.com). I have 1,059 public repositories on GitHub — tools, experiments, Claude Code plugins, MCP servers, datasets and a good deal of documentation — and this repo is the way in. It is regenerated from the GitHub API, so it covers everything public, not just the projects I remembered to list. Last rebuilt 2026-10-30.


There are two ways to use it, depending on who you are.


---


## If you're a person

**Looking for a subject?** Start with the topic indexes. I keep 67 hand-curated index repos — AI agents, Hebrew language, Israel, speech tech, Claude Code and more — and they are a better read than any keyword search. The [index of indexes](https://github.com/danielrosehill/Subindices) lists them all.


[![Index of Indexes](https://img.shields.io/badge/Browse_the_topic_indexes-FF6B6B?style=for-the-badge&logo=github&logoColor=white)](https://github.com/danielrosehill/Subindices)


**Want to browse?** Every public repo is filed by topic below, or you can see [the full list by last update](index.md) or [what I made when](sections/by-time/README.md).


| Topic | What's in it |
| ----- | ------------ |
| [AI & Machine Learning](sections/by-topic/ai-ml/index.md) | Repositories related to AI, ML, and LLM technologies |
| [Data Tools](sections/by-topic/data-tools/index.md) | Data processing, analysis, and visualization tools |
| [Development Tools](sections/by-topic/development/index.md) | Software development tools and utilities |
| [Infrastructure](sections/by-topic/infrastructure/index.md) | Infrastructure, deployment, and system administration |
| [Platforms & Services](sections/by-topic/platforms/index.md) | Platform-specific integrations and tools |
| [Project Types](sections/by-topic/project-types/index.md) | Projects organized by type |
| [Regional Specific](sections/by-topic/regional-specific/index.md) | Region or language-specific projects |
| [Tools & Utilities](sections/by-topic/tools-utilities/index.md) | General purpose tools and utilities |

---


## If you're an AI agent

You have probably been sent here to find one of my repositories, to work out which of my projects cover a subject, or to download some of them. Please don't crawl my GitHub profile or guess URLs — everything you need is in two JSON files in this repo:


| File | What it holds |
| ---- | ------------- |
| [`repositories.json`](repositories.json) | Every public repo: `name`, `url`, `description`, `repositoryTopics`, `createdAt`, `updatedAt`, `stargazerCount`, `forkCount` |
| [`indexing-repos.json`](indexing-repos.json) | The curated topic indexes: `indices[]` of `{title, description, url}`, synced from [Subindices](https://github.com/danielrosehill/Subindices) |


Fetch them raw:

```
https://raw.githubusercontent.com/danielrosehill/Start-Here/main/repositories.json
https://raw.githubusercontent.com/danielrosehill/Start-Here/main/indexing-repos.json
```


A good order of work:


1. **Subject question** ("what has Daniel built about X?") — look for a topic index in `indexing-repos.json` first and read that index's README. Indexes are curated; keyword hits are not.
2. **Specific repo** — search `repositories.json` by name, description and topics. Try synonyms: naming is inconsistent (ASR / STT / speech / dictation).
3. **Not in the snapshot?** It is rebuilt periodically, not live. Check GitHub itself with `gh search repos --owner danielrosehill <terms>` before saying a repo doesn't exist.


Things that will otherwise trip you up:


- **Public only, forks included.** A repo missing here may simply be private.
- **Renamed repos still answer on their old names.** GitHub redirects old slugs with a 200, so compare `full_name` (`gh api repos/danielrosehill/<Name> --jq .full_name`) before citing one. This repo itself was `Github-Master-Index`, then `Index`.
- **Ask before bulk-cloning.** There are over a thousand repos; confirm the count first and use `--depth 1`.


### Skills

The [`skills/`](skills/) folder packages the above as [Agent Skills](https://agentskills.io) (plain `SKILL.md` files, usable by any agent that reads them):


| Skill | Use it to |
| ----- | --------- |
| [`find-repo`](skills/find-repo/SKILL.md) | Search every public repo by name, subject, topic or date. Ships a stdlib-only `search.py` |
| [`find-index`](skills/find-index/SKILL.md) | Find the curated topic index for a subject and read it |
| [`clone-repos`](skills/clone-repos/SKILL.md) | Download one repo, a filtered set, or a single file |


In Claude Code, the repo is also a plugin (`start-here`) in the [`danielrosehill` marketplace](https://github.com/danielrosehill/Claude-Code-Plugins).


---


## By the numbers

**1,059 public repositories**, filed under these topics:


| Topic | Repositories |
| ----- | -----------: |
| AI & Machine Learning | 624 |
| Development Tools | 164 |
| Project Types | 142 |
| Data Tools | 86 |
| Regional Specific | 85 |
| Tools & Utilities | 71 |
| Platforms & Services | 58 |
| Infrastructure | 52 |


A repo can sit under more than one topic, and a few are not filed under any; [`index.md`](index.md) has the complete list.


---


## How this is built

`scripts/sync-all.sh` pulls the repo list with the GitHub CLI, files new repos by keyword (`scripts/hierarchy-schema.json`), and regenerates `index.md`, the topic and time indexes, the JSON files and this README. Maintenance notes for agents working *on* the repo are in [`CLAUDE.md`](CLAUDE.md).
