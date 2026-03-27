"""Small Reddit review fetcher.

Improvements made:
- Read Reddit credentials from environment variables.
- Add basic error handling and logging.
- Provide a small smoke test and supporting files in the repo.
"""

import os
import logging
from typing import List, Dict

import praw


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def make_reddit_client() -> praw.Reddit:
    """Create a PRAW Reddit client using environment variables.

    Expects the following env vars to be set:
    - REDDIT_CLIENT_ID
    - REDDIT_CLIENT_SECRET
    - REDDIT_USER_AGENT
    """
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "mobileBrandProject by /u/yourusername")

    if not client_id or not client_secret:
        raise RuntimeError("Reddit credentials not found. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.")

    return praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)


def get_reddit_reviews(reddit: praw.Reddit, subreddit_name: str, keywords: List[str], limit: int = 50) -> List[Dict]:
    """Search a subreddit for posts matching keywords and return a list of dicts.

    Args:
        reddit: an authenticated praw.Reddit instance
        subreddit_name: name of subreddit to search (without r/)
        keywords: list of keywords to OR together in the query
        limit: maximum number of submissions to return

    Returns:
        A list of dictionaries containing basic submission metadata.
    """
    query = " OR ".join(keywords)
    reviews_list: List[Dict] = []

    try:
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.search(query, limit=limit):
            reviews_list.append({
                "title": submission.title,
                "author": str(submission.author),
                "score": submission.score,
                "comments": submission.num_comments,
                "url": submission.url,
                "text": submission.selftext,
            })
    except Exception as e:
        logger.exception("Error while fetching reviews from Reddit: %s", e)
        raise

    return reviews_list


def main():
    # Example keywords
    keywords_samsung = ["Samsung", "Galaxy S23", "Galaxy S24"]
    keywords_apple = ["iPhone", "iPhone 15", "iPhone 14"]

    reddit = make_reddit_client()

    # Fetch Samsung reviews
    samsung_reviews = get_reddit_reviews(reddit, "Android", keywords_samsung, limit=30)
    for rev in samsung_reviews[:5]:
        print(rev["title"], "-", rev["author"])

    # Fetch Apple reviews
    apple_reviews = get_reddit_reviews(reddit, "iPhone", keywords_apple, limit=30)
    for rev in apple_reviews[:5]:
        print(rev["title"], "-", rev["author"])


if __name__ == "__main__":
    main()
