"""Reddit extractor for 'Apple vs Samsung' project.

Usage examples:
  # set env vars (PowerShell)
  $env:REDDIT_CLIENT_ID='..'; $env:REDDIT_CLIENT_SECRET='..'; $env:REDDIT_USER_AGENT='app:apple_vs_samsung:v1 (by /u/you)'

  # fetch and save to JSON
  python reddit_extractor.py --subreddit Android --keywords "Samsung,Galaxy" --limit 50 --out results.json

  # fetch and save to CSV
  python reddit_extractor.py --subreddit iPhone --keywords "iPhone,Apple" --limit 50 --out results.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
from typing import Any, Dict, List, Iterable, Optional

import praw

try:
    # optional: load .env automatically when present
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv is optional; requirements.txt already lists it
    pass


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def make_reddit_client(client_id: Optional[str], client_secret: Optional[str], user_agent: Optional[str]) -> praw.Reddit:
    """Create a PRAW client using either provided values or environment variables.

    CLI arguments take precedence over environment variables.
    """
    cid = client_id or os.environ.get("REDDIT_CLIENT_ID")
    csec = client_secret or os.environ.get("REDDIT_CLIENT_SECRET")
    uag = user_agent or os.environ.get("REDDIT_USER_AGENT", "apple_vs_samsung_extractor/0.1")

    if not cid or not csec:
        raise RuntimeError("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be provided via CLI or environment variables")

    return praw.Reddit(client_id=cid, client_secret=csec, user_agent=uag)


def fetch_submissions(reddit: praw.Reddit, subreddit_name: str, keywords: List[str], limit: int = 50) -> Iterable[Dict[str, Any]]:
    query = " OR ".join(keywords)
    logger.info("Searching r/%s for: %s (limit=%s)", subreddit_name, query, limit)
    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.search(query, limit=limit):
        yield {
            "id": submission.id,
            "title": submission.title,
            "author": str(submission.author),
            "score": submission.score,
            "num_comments": submission.num_comments,
            "url": submission.url,
            "selftext": submission.selftext,
        }


def fetch_top_comments(reddit: praw.Reddit, submission_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    submission = reddit.submission(id=submission_id)
    submission.comments.replace_more(limit=0)
    comments = []
    for c in submission.comments[:limit]:
        comments.append({"id": c.id, "author": str(c.author), "score": c.score, "body": c.body})
    return comments


def write_json(out_path: str, items: Iterable[Dict[str, Any]]) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(list(items), f, ensure_ascii=False, indent=2)


def write_csv(out_path: str, items: Iterable[Dict[str, Any]]) -> None:
    items = list(items)
    if not items:
        logger.warning("No items to write to CSV")
        return

    fieldnames = list(items[0].keys())
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for it in items:
            writer.writerow(it)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract Reddit posts and optional comments to JSON/CSV")
    p.add_argument("--subreddit", required=True)
    p.add_argument("--keywords", required=True, help="Comma-separated keywords to OR together")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--out", required=True, help="Output file path (.json or .csv)")
    p.add_argument("--comments", type=int, default=0, help="Number of top-level comments to fetch per submission (0 to skip)")
    p.add_argument("--client-id", help="Reddit client_id (overrides env)")
    p.add_argument("--client-secret", help="Reddit client_secret (overrides env)")
    p.add_argument("--user-agent", help="Reddit user_agent (overrides env)")
    p.add_argument("--dry-run", action="store_true", help="Do everything except write the output file")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    reddit = make_reddit_client(client_id=args.client_id, client_secret=args.client_secret, user_agent=args.user_agent)

    items: List[Dict[str, Any]] = []
    for sub in fetch_submissions(reddit, args.subreddit, keywords, limit=args.limit):
        if args.comments and int(sub.get("num_comments", 0)) > 0:
            try:
                sub_comments = fetch_top_comments(reddit, submission_id=sub["id"], limit=args.comments)
                sub["top_comments"] = sub_comments
            except Exception:
                logger.exception("Failed to fetch comments for %s", sub["id"])
                sub["top_comments"] = []
        items.append(sub)

    out = args.out
    if out.lower().endswith(".json"):
        if not args.dry_run:
            write_json(out, items)
    elif out.lower().endswith(".csv"):
        # flatten top_comments if present
        flat_items = []
        for it in items:
            copy = dict(it)
            if "top_comments" in copy:
                copy["top_comments"] = json.dumps(copy["top_comments"], ensure_ascii=False)
            flat_items.append(copy)
        if not args.dry_run:
            write_csv(out, flat_items)
    else:
        raise RuntimeError("Output file must end with .json or .csv")

    logger.info("Fetched %d items; output path=%s; dry_run=%s", len(items), out, args.dry_run)


if __name__ == "__main__":
    main()
