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

def build_readme(schema_path, output_path, base_dir=None):
    """Build complete README from schema"""
    schema = load_hierarchy_schema(schema_path)
    base_dir = Path(base_dir) if base_dir else Path(output_path).parent

    # Header section - simplified without table of contents
    readme_content = [
        "# Daniel Rosehill Github Repository Index\n",
        "![Banner](banners/index.png)\n",
        f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        "\nThis is an automatically generated index of my public GitHub repositories.\n",
        "\n---\n",
        "\n## Index of Indexes\n",
        "I maintain several specialized indexes for different project categories. View the complete list:\n",
        "\n[![Index of Indexes](https://img.shields.io/badge/View_Index_of_Indexes-FF6B6B?style=for-the-badge&logo=github&logoColor=white)](https://github.com/danielrosehill/Subindices)\n",
        "\n---\n",
        "\n## Repository Views\n",
        "This index provides multiple ways to explore my GitHub repositories:\n",
        "\n| View | Description |",
        "| ---- | ----------- |",
        "| [![Full Index](https://img.shields.io/badge/Full_Index-4285F4?style=flat-square&logo=github&logoColor=white)](index.md) | All repositories sorted by update date |",
        "| [![Browse by Time](https://img.shields.io/badge/By_Time-9C27B0?style=flat-square&logo=github&logoColor=white)](sections/by-time/README.md) | Explore by year and month of creation |\n",
        "\n---\n",
        "\n## Browse by Topic\n",
        "Explore repositories organized by topic:\n",
        "\n| Category | Description |",
        "| -------- | ----------- |",
    ]

    # Build concise category summary table
    if 'sections' in schema:
        category_table = build_category_summary(schema['sections'])
        readme_content.append(category_table)

    # Footer sections
    total = count_total_repositories(base_dir)
    readme_content.extend([
        "\n## Repository Statistics\n",
        f"**Total Repositories:** {total if total is not None else 'unknown'}\n",
    ])

    if 'sections' in schema:
        category_counts = count_repos_by_category(base_dir, schema['sections'])
        ranked = sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))
        if ranked:
            readme_content.append("\n**Repositories per category:**\n")
            readme_content.append("\n| Category | Repositories |")
            readme_content.append("| -------- | -----------: |")
            readme_content.extend(f"| {name} | {count} |" for name, count in ranked)
            readme_content.append("")

    readme_content.extend([
        "\n---\n",
        "\n## Data Access\n",
        "The generated data is committed to this repository and can be fetched directly:\n",
        "\n| File | Contents |",
        "| ---- | -------- |",
        "| [`repositories.json`](repositories.json) | Full GitHub metadata for every indexed repository |",
        "| [`indexing-repos.json`](indexing-repos.json) | The specialised indexes, synced from [Subindices](https://github.com/danielrosehill/Subindices) |",
        "| [`index.md`](index.md) | All repositories as markdown, sorted by update date |\n",
        "\nRaw URLs, for scripts:\n",
        "```",
        "https://raw.githubusercontent.com/danielrosehill/Index/main/repositories.json",
        "https://raw.githubusercontent.com/danielrosehill/Index/main/indexing-repos.json",
        "```\n",
        "\nData is regenerated by `scripts/sync-all.sh`; it is not live.\n"
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
