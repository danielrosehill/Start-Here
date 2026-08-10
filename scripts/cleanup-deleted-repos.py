#!/usr/bin/env python3
"""
Cleanup script to remove stale repositories from the index.

This index documents public repositories, forks included. By default an entry
is stale if the repo is no longer a public repo — deleted, renamed, or turned
private. Pass --deleted-only to prune just the ones that no longer resolve.

Two things this script used to get wrong, both silent:

  * Its link regex only matched plain `[text](url)` links, so it saw 73 of the
    1304 entries actually present. The leaf section files use a badge form,
    `## Name [![View Repo](badge-url)](repo-url)`, whose inner `]` defeats the
    old pattern. Match on the GitHub URL itself instead.
  * It removed the single matched line. In the badge form the description sits
    on the following line, so that orphaned the description under the previous
    entry. Remove the whole entry block.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import re

def get_current_repos(deleted_only=False):
    """Fetch current list of repos from GitHub using gh CLI.

    Default is public repos, forks included, which is what this index
    contains — hierarchy-schema.json has a deliberate forks.md category.
    --deleted-only widens it to every repo that still exists, public or
    private, so only genuinely deleted repos count as stale.
    """
    cmd = ['gh', 'repo', 'list', 'danielrosehill', '--limit', '4000', '--json',
           'name,nameWithOwner,description,createdAt,updatedAt,url,stargazerCount,forkCount,repositoryTopics']
    if not deleted_only:
        cmd += ['--visibility', 'public']
        print("📡 Fetching current public repositories from GitHub...")
    else:
        print("📡 Fetching all existing repositories from GitHub...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        repos = json.loads(result.stdout)
        print(f"✓ Found {len(repos)} repositories on GitHub")
        return {repo['nameWithOwner']: repo for repo in repos}
    except subprocess.CalledProcessError as e:
        print(f"❌ Error fetching repos from GitHub: {e}")
        print(f"❌ Error output: {e.stderr if hasattr(e, 'stderr') else 'No stderr'}")
        sys.exit(1)

# Match the repo URL itself, so this works for both the plain link form
# `[Name](https://github.com/owner/repo)` and the badge form
# `## Name [![View Repo](badge)](https://github.com/owner/repo)`.
# Badge URLs live on img.shields.io, so they never match this pattern.
REPO_URL_RE = re.compile(r'https://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9._-]+)')

def extract_repo_name(line):
    """Extract repository nameWithOwner from a markdown line."""
    match = REPO_URL_RE.search(line)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return None

def scan_section_files(sections_dir):
    """Scan all section files and extract indexed repos."""
    print("\n🔍 Scanning section files for indexed repositories...")
    indexed_repos = {}  # {nameWithOwner: [list of file paths where it appears]}

    for md_file in sections_dir.rglob('*.md'):
        if md_file.name == 'README.md' or md_file.name == 'index.md':
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        for line in content.split('\n'):
            repo_name = extract_repo_name(line)
            if repo_name:
                if repo_name not in indexed_repos:
                    indexed_repos[repo_name] = []
                indexed_repos[repo_name].append(md_file)

    print(f"✓ Found {len(indexed_repos)} unique repositories indexed across section files")
    return indexed_repos

def find_deleted_repos(current_repos, indexed_repos):
    """Compare indexed repos against current repos to find deleted ones."""
    print("\n🗑️  Identifying deleted repositories...")
    deleted = {}

    for repo_name, file_paths in indexed_repos.items():
        if repo_name not in current_repos:
            deleted[repo_name] = file_paths

    if deleted:
        print(f"❌ Found {len(deleted)} deleted repositories:")
        for repo_name in sorted(deleted.keys()):
            print(f"   - {repo_name}")
    else:
        print("✓ No deleted repositories found - index is up to date!")

    return deleted

def remove_repo_from_file(file_path, repo_name):
    """Remove every entry for a repo from a file.

    An entry in a leaf section file is a `## Heading` line carrying the repo
    link, followed by its description and a blank separator. Dropping only the
    heading would strand the description under the entry above, so consume the
    whole block. Plain one-line list entries are removed as a single line.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    removed_count = 0
    index = 0

    while index < len(lines):
        line = lines[index]
        if extract_repo_name(line) != repo_name:
            new_lines.append(line)
            index += 1
            continue

        removed_count += 1
        if not line.lstrip().startswith('#'):
            index += 1
            continue

        # Heading entry: skip it, its description, and one trailing blank line.
        index += 1
        while index < len(lines) and not lines[index].lstrip().startswith('#') \
                and lines[index].strip():
            index += 1
        if index < len(lines) and not lines[index].strip():
            index += 1

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    return removed_count

def cleanup_deleted_repos(deleted_repos, dry_run=True):
    """Remove deleted repos from all section files."""
    if not deleted_repos:
        return

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"\n🧹 Cleanup mode: {mode}")

    total_removed = 0

    for repo_name, file_paths in deleted_repos.items():
        print(f"\n📝 Processing: {repo_name}")
        for file_path in file_paths:
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                rel_path = file_path

            if dry_run:
                print(f"   Would remove from: {rel_path}")
            else:
                count = remove_repo_from_file(file_path, repo_name)
                total_removed += count
                print(f"   ✓ Removed {count} line(s) from: {rel_path}")

    if not dry_run:
        print(f"\n✅ Cleanup complete! Removed {total_removed} entries total.")
    else:
        print(f"\n💡 This was a dry run. Use --execute to perform actual cleanup.")

def save_report(deleted_repos, current_repos, indexed_repos):
    """Save a cleanup report."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    report_file = Path('scripts') / f'cleanup-report-{timestamp}.json'

    report = {
        'timestamp': timestamp,
        'current_repos_count': len(current_repos),
        'indexed_repos_count': len(indexed_repos),
        'deleted_repos_count': len(deleted_repos),
        'deleted_repos': {
            repo: [str(p) for p in paths]
            for repo, paths in deleted_repos.items()
        }
    }

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to: {report_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Clean up deleted repositories from index')
    parser.add_argument('--execute', action='store_true',
                       help='Actually perform cleanup (default is dry run)')
    parser.add_argument('--deleted-only', action='store_true',
                       help='Only prune repos that no longer exist, keeping '
                            'entries for repos that went private')
    args = parser.parse_args()

    print("🧹 GitHub Repository Cleanup Tool")
    print("=" * 50)

    # Get current repos from GitHub
    current_repos = get_current_repos(deleted_only=args.deleted_only)

    # Scan section files for indexed repos
    sections_dir = Path('sections')
    indexed_repos = scan_section_files(sections_dir)

    # Find deleted repos
    deleted_repos = find_deleted_repos(current_repos, indexed_repos)

    # Save report
    save_report(deleted_repos, current_repos, indexed_repos)

    # Cleanup
    if deleted_repos:
        cleanup_deleted_repos(deleted_repos, dry_run=not args.execute)

        if args.execute:
            print("\n🔄 Regenerating indexes...")
            print("Run: ./scripts/sync-all.sh")
    else:
        print("\n✨ Index is clean - no action needed!")

if __name__ == '__main__':
    main()
