#!/usr/bin/env python3
"""
Build hierarchical README from hierarchy schema with badge links
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Repo links in the leaf section files, e.g.
# ## Some Repo [![View Repo](badge)](https://github.com/danielrosehill/Some-Repo)
REPO_LINK_RE = re.compile(r"https://github\.com/danielrosehill/([A-Za-z0-9._-]+)")

def load_hierarchy_schema(schema_path):
    """Load the hierarchy schema JSON"""
    with open(schema_path, 'r') as f:
        return json.load(f)

def count_total_repositories(base_dir):
    """Total repo count from the freshest GitHub snapshot available.

    sync-all.sh only copies repo-data/latest.json to repositories.json at
    step 6, after this script runs at step 5, so prefer the snapshot and
    fall back to the root copy for standalone runs.
    """
    for candidate in (base_dir / "repo-data" / "latest.json", base_dir / "repositories.json"):
        try:
            with open(candidate, 'r') as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError):
            continue
        if isinstance(data, list):
            return len(data)
    return None

def count_repos_by_category(base_dir, sections, base_path="sections/by-topic"):
    """Count distinct repos filed under each top-level category."""
    counts = {}
    for section_key, section_data in sections.items():
        section_dir = base_dir / base_path / section_key
        if not section_dir.is_dir():
            continue
        repos = set()
        for md_file in section_dir.rglob("*.md"):
            if md_file.name == "index.md":
                continue
            repos.update(REPO_LINK_RE.findall(md_file.read_text(encoding="utf-8")))
        section_name = section_data.get('name', format_section_name(section_key))
        counts[section_name] = len(repos)
    return counts

def format_title_for_badge(title):
    """Format title for badge display (replace spaces with underscores)"""
    return title.replace(' ', '_')

def format_section_name(name):
    """Format section name for display"""
    return name.replace('-', ' ').title()

def build_hierarchy_section(sections, base_path="sections/by-topic"):
    """Build the hierarchical README content with badges and category index links"""
    content = []

    for section_key, section_data in sorted(sections.items()):
        section_name = section_data.get('name', format_section_name(section_key))

        # Main section header (##)
        content.append(f"\n## {section_name}\n")

        if 'description' in section_data:
            content.append(f"*{section_data['description']}*\n")

        # Add link to category index
        category_index_path = f"{base_path}/{section_key}/index.md"
        content.append(f"\n**[View Complete {section_name} Index]({category_index_path})**\n")

        # Check if section has subsections
        if 'subsections' in section_data:
            for subsection_key, subsection_data in sorted(section_data['subsections'].items()):
                subsection_name = subsection_data.get('name', format_section_name(subsection_key))

                # Subsection header (####)
                content.append(f"\n#### {subsection_name}\n")

                if 'description' in subsection_data:
                    content.append(f"*{subsection_data['description']}*\n")

                # Add badges for files in subsection
                if 'files' in subsection_data:
                    content.append("\n")
                    for file_name in sorted(subsection_data['files'].keys()):
                        file_title = file_name.replace('.md', '').replace('-', ' ').title()
                        badge_title = format_title_for_badge(file_title)
                        file_path = f"{base_path}/{section_key}/{subsection_key}/{file_name}"

                        badge = f"[![{file_title}](https://img.shields.io/badge/{badge_title}-2ea44f?style=for-the-badge&logo=github)]({file_path})"
                        content.append(f"{badge}<br>")
                    content.append("\n")

        # If section has direct files (no subsections)
        elif 'files' in section_data:
            content.append("\n")
            for file_name in sorted(section_data['files'].keys()):
                file_title = file_name.replace('.md', '').replace('-', ' ').title()
                badge_title = format_title_for_badge(file_title)
                file_path = f"{base_path}/{section_key}/{file_name}"

                badge = f"[![{file_title}](https://img.shields.io/badge/{badge_title}-2ea44f?style=for-the-badge&logo=github)]({file_path})"
                content.append(f"{badge}<br>")
            content.append("\n")

    return '\n'.join(content)

def build_category_summary(sections, base_path="sections/by-topic"):
    """Build a concise category summary with just main category links"""
    content = []

    for section_key, section_data in sorted(sections.items()):
        section_name = section_data.get('name', format_section_name(section_key))
        description = section_data.get('description', '')
        category_index_path = f"{base_path}/{section_key}/index.md"

        content.append(f"| [{section_name}]({category_index_path}) | {description} |")

    return '\n'.join(content)

def load_indexing_repos(base_dir):
    """The specialised indexes, as synced from Subindices by step 0."""
    try:
        with open(base_dir / "indexing-repos.json", 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None

def build_readme(schema_path, output_path, base_dir=None):
    """Build complete README from schema"""
    schema = load_hierarchy_schema(schema_path)
    base_dir = Path(base_dir) if base_dir else Path(output_path).parent
    total = count_total_repositories(base_dir)
    total_text = f"{total:,}" if total is not None else "a lot of"
    indexing = load_indexing_repos(base_dir)
    index_count = len(indexing["indices"]) if indexing else None
    index_text = f"{index_count}" if index_count else "several dozen"
    updated = datetime.now().strftime('%Y-%m-%d')

    readme_content = [
        "# Start Here\n",
        "![Banner](banners/index.png)\n",
        f"\nHi, I'm [Daniel Rosehill](https://danielrosehill.com). I have {total_text} public "
        "repositories on GitHub — tools, experiments, Claude Code plugins, MCP servers, "
        "datasets and a good deal of documentation — and this repo is the way in. "
        "It is regenerated from the GitHub API, so it covers everything public, "
        f"not just the projects I remembered to list. Last rebuilt {updated}.\n",
        "\nThere are two ways to use it, depending on who you are.\n",
        "\n---\n",
        "\n## If you're a person\n",
        "**Looking for a subject?** Start with the topic indexes. I keep "
        f"{index_text} hand-curated index repos — AI agents, Hebrew language, Israel, "
        "speech tech, Claude Code and more — and they are a better read than any keyword search. "
        "The [index of indexes](https://github.com/danielrosehill/Subindices) lists them all.\n",
        "\n[![Index of Indexes](https://img.shields.io/badge/Browse_the_topic_indexes-FF6B6B?style=for-the-badge&logo=github&logoColor=white)](https://github.com/danielrosehill/Subindices)\n",
        "\n**Want to browse?** Every public repo is filed by topic below, or you can see "
        "[the full list by last update](index.md) or [what I made when](sections/by-time/README.md).\n",
        "\n**Want to see what's new?** [Firehose](https://github.com/danielrosehill/Firehose) is a daily "
        "digest of what I published across GitHub, Hugging Face and my blog.\n",
        "\n| Topic | What's in it |",
        "| ----- | ------------ |",
    ]

    if 'sections' in schema:
        readme_content.append(build_category_summary(schema['sections']))

    readme_content.extend([
        "\n---\n",
        "\n## If you're an AI agent\n",
        "You have probably been sent here to find one of my repositories, to work out which of "
        "my projects cover a subject, or to download some of them. Please don't crawl my GitHub "
        "profile or guess URLs — everything you need is in two JSON files in this repo:\n",
        "\n| File | What it holds |",
        "| ---- | ------------- |",
        "| [`repositories.json`](repositories.json) | Every public repo: `name`, `url`, `description`, `repositoryTopics`, `createdAt`, `updatedAt`, `stargazerCount`, `forkCount` |",
        "| [`indexing-repos.json`](indexing-repos.json) | The curated topic indexes: `indices[]` of `{title, description, url}`, synced from [Subindices](https://github.com/danielrosehill/Subindices) |\n",
        "\nFetch them raw:\n",
        "```",
        "https://raw.githubusercontent.com/danielrosehill/Start-Here/main/repositories.json",
        "https://raw.githubusercontent.com/danielrosehill/Start-Here/main/indexing-repos.json",
        "```\n",
        "\nA good order of work:\n",
        "\n1. **Subject question** (\"what has Daniel built about X?\") — look for a topic index in "
        "`indexing-repos.json` first and read that index's README. Indexes are curated; keyword hits are not.",
        "2. **Specific repo** — search `repositories.json` by name, description and topics. "
        "Try synonyms: naming is inconsistent (ASR / STT / speech / dictation).",
        "3. **Not in the snapshot?** It is rebuilt periodically, not live. Check GitHub itself with "
        "`gh search repos --owner danielrosehill <terms>` before saying a repo doesn't exist.\n",
        "\nThings that will otherwise trip you up:\n",
        "\n- **Public only, forks included.** A repo missing here may simply be private.",
        "- **Renamed repos still answer on their old names.** GitHub redirects old slugs with a 200, "
        "so compare `full_name` (`gh api repos/danielrosehill/<Name> --jq .full_name`) before citing one. "
        "This repo itself was `Github-Master-Index`, then `Index`.",
        "- **Ask before bulk-cloning.** There are over a thousand repos; confirm the count first and use `--depth 1`.\n",
        "\n### Skills\n",
        "The [`skills/`](skills/) folder packages the above as [Agent Skills](https://agentskills.io) "
        "(plain `SKILL.md` files, usable by any agent that reads them):\n",
        "\n| Skill | Use it to |",
        "| ----- | --------- |",
        "| [`find-repo`](skills/find-repo/SKILL.md) | Search every public repo by name, subject, topic or date. Ships a stdlib-only `search.py` |",
        "| [`find-index`](skills/find-index/SKILL.md) | Find the curated topic index for a subject and read it |",
        "| [`clone-repos`](skills/clone-repos/SKILL.md) | Download one repo, a filtered set, or a single file |\n",
        "\nIn Claude Code, the repo is also a plugin (`start-here`) in the "
        "[`danielrosehill` marketplace](https://github.com/danielrosehill/Claude-Code-Plugins).\n",
        "\n---\n",
        "\n## By the numbers\n",
        f"**{total_text} public repositories**, filed under these topics:\n",
    ])

    if 'sections' in schema:
        category_counts = count_repos_by_category(base_dir, schema['sections'])
        ranked = sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))
        if ranked:
            readme_content.append("\n| Topic | Repositories |")
            readme_content.append("| ----- | -----------: |")
            readme_content.extend(f"| {name} | {count} |" for name, count in ranked)
            readme_content.append("")

    readme_content.extend([
        "\nA repo can sit under more than one topic, and a few are not filed under any; "
        "[`index.md`](index.md) has the complete list.\n",
        "\n---\n",
        "\n## How this is built\n",
        "`scripts/sync-all.sh` pulls the repo list with the GitHub CLI, files new repos by keyword "
        "(`scripts/hierarchy-schema.json`), and regenerates `index.md`, the topic and time indexes, "
        "the JSON files and this README. Maintenance notes for agents working *on* the repo are in "
        "[`CLAUDE.md`](CLAUDE.md).\n",
    ])

    # Write README
    with open(output_path, 'w') as f:
        f.write('\n'.join(readme_content))

    print(f"✓ README built successfully: {output_path}")

if __name__ == "__main__":
    # Paths
    base_dir = Path(__file__).parent.parent
    schema_path = base_dir / "scripts" / "hierarchy-schema.json"
    output_path = base_dir / "README.md"

    print("Building hierarchical README...")
    print(f"Schema: {schema_path}")
    print(f"Output: {output_path}")

    build_readme(schema_path, output_path, base_dir)
