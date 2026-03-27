# Reddit Reviews / Extractor

This project fetches Reddit posts matching keywords for brand comparisons (Apple vs Samsung).

Setup
1. Create a Reddit developer app and get `client_id` and `client_secret`.
2. Copy `.env.example` to `.env` and fill in values, or set environment variables in your shell.
3. Install dependencies:

```powershell
pip install -r requirements.txt
```

Optional: if you want the repo to auto-load `.env` files, `python-dotenv` is already included in `requirements.txt`.

Extractor usage

Examples (PowerShell):

Set environment variables for the current session:

```powershell
$env:REDDIT_CLIENT_ID='your_client_id'
$env:REDDIT_CLIENT_SECRET='your_client_secret'
$env:REDDIT_USER_AGENT='app:apple_vs_samsung:v1 (by /u/yourname)'
```

Fetch posts to JSON:

```powershell
python reddit_extractor.py --subreddit Android --keywords "Samsung,Galaxy" --limit 100 --out samsung_posts.json
```

Fetch posts and top 5 comments per post to CSV:

```powershell
python reddit_extractor.py --subreddit iPhone --keywords "iPhone,Apple" --limit 50 --comments 5 --out iphone_posts.csv
```

You can also pass credentials on the CLI (overrides env):

```powershell
python reddit_extractor.py --subreddit Android --keywords "Samsung" --client-id YOUR_ID --client-secret YOUR_SECRET --out out.json
```

Files in this repo

- `reddit_extractor.py` — main extractor (CLI)
- `reddit_reviews.py` — small example script
- `.env.example` — example env file
- `requirements.txt` — dependencies
- `smoke_test.py` — basic smoke test
