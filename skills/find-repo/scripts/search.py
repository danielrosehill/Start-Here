#!/usr/bin/env python3
"""Search Daniel Rosehill's public GitHub repositories.

Reads repositories.json (and optionally indexing-repos.json) from the
danielrosehill/Start-Here repo and ranks repos against a free-text query.
Standard library only, so any agent with Python 3 can run it.

    search.py "hebrew asr"                 # ranked matches, JSON out
    search.py "mcp" --topic mcp --limit 50
    search.py --since 2026-01-01 --limit 20 # newest, no query
    search.py "first aid" --indexes        # search the topic indexes instead
"""

import argparse
import json
import re
import sys
import urllib.request

RAW = "https://raw.githubusercontent.com/danielrosehill/Start-Here/main/"


def load(name, local_dir=None):
    if local_dir:
        with open(f"{local_dir.rstrip('/')}/{name}", encoding="utf-8") as f:
            return json.load(f)
    with urllib.request.urlopen(RAW + name, timeout=30) as r:
        return json.load(r)


def tokens(text):
    return [t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if t]


def score(query_terms, name, description, topics):
    """Name hits outweigh topic hits, which outweigh description hits."""
    name_l = name.lower()
    name_t = set(tokens(name))
    desc_t = set(tokens(description))
    topic_t = set(t for topic in topics for t in tokens(topic))
    s = 0.0
    hit = 0
    for term in query_terms:
        t = 0
        if term in name_t:
            t += 3
        elif term in name_l:
            t += 2
        if term in topic_t:
            t += 2
        if term in desc_t:
            t += 1
        s += t
        hit += t > 0
    if not query_terms:
        return s
    # Weight by the share of terms matched, and drop repos that matched fewer
    # than half: "hebrew asr" should not rank a Hebrew calendar dashboard.
    coverage = hit / len(query_terms)
    return 0.0 if coverage < 0.5 else s * coverage * coverage


def search_repos(args):
    repos = load("repositories.json", args.local)
    terms = tokens(args.query)
    out = []
    for r in repos:
        topics = [t["name"] for t in (r.get("repositoryTopics") or [])]
        if args.topic and args.topic.lower() not in topics:
            continue
        if args.since and (r.get("createdAt") or "") < args.since:
            continue
        s = score(terms, r["name"], r.get("description"), topics) if terms else 1
        if s <= 0:
            continue
        out.append({
            "name": r["name"],
            "url": r["url"],
            "description": r.get("description") or "",
            "topics": topics,
            "created": (r.get("createdAt") or "")[:10],
            "updated": (r.get("updatedAt") or "")[:10],
            "stars": r.get("stargazerCount", 0),
            "score": s,
        })
    if terms:
        out.sort(key=lambda x: (x["score"], x["updated"]), reverse=True)
    else:
        out.sort(key=lambda x: x["created"], reverse=True)
    return {"total_indexed": len(repos), "matches": len(out), "results": out[: args.limit]}


def search_indexes(args):
    data = load("indexing-repos.json", args.local)
    terms = tokens(args.query)
    out = []
    for ix in data["indices"]:
        s = score(terms, ix["title"], ix.get("description"), []) if terms else 1
        if s > 0:
            out.append({**ix, "score": s})
    out.sort(key=lambda x: -x["score"])
    return {"synced_at": data.get("synced_at"), "matches": len(out), "results": out[: args.limit]}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("query", nargs="?", default="", help="free-text query; omit to list")
    p.add_argument("--indexes", action="store_true", help="search the topic indexes, not repos")
    p.add_argument("--topic", help="only repos carrying this exact GitHub topic")
    p.add_argument("--since", help="only repos created on/after this date (YYYY-MM-DD)")
    p.add_argument("--limit", type=int, default=15)
    p.add_argument("--local", help="read the JSON from a local Start-Here clone instead of GitHub")
    args = p.parse_args()
    result = search_indexes(args) if args.indexes else search_repos(args)
    json.dump(result, sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
