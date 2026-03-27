"""Simple smoke test for reddit_reviews.py.

This test will try to import the module and call functions with mocked environment variables.
It does not call the real Reddit API (to avoid network calls) — instead it validates the client creation logic.
"""

import os
import importlib


def test_make_client_without_env_raises():
    # Ensure env vars are not set
    os.environ.pop('REDDIT_CLIENT_ID', None)
    os.environ.pop('REDDIT_CLIENT_SECRET', None)

    reddit_reviews = importlib.import_module('reddit_reviews')
    try:
        reddit_reviews.make_reddit_client()
    except RuntimeError:
        print('PASS: make_reddit_client raised RuntimeError when credentials missing')
    else:
        print('FAIL: make_reddit_client did not raise')


if __name__ == '__main__':
    test_make_client_without_env_raises()
