import praw
import csv
from datetime import datetime, timedelta

# Reddit credentials
client_id = "PzKE5js_EwgTQ1iJmX_16w"
client_secret = "6yNPkwxRsnfnz16H1BBsIsEfQk5Efg"
user_agent = "timeboundGMATopinionresearch_by_sireeshy"

# Create Reddit instance
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# Subreddits and search query
subreddits = ['GMAT', 'MBA', 'gradadmissions', 'testprep']
search_query = "GMAT preparation resources"
csv_filename = "gmat_reddit_posts_last3yrs.csv"

# Calculate cutoff (3 years ago from today)
cutoff_date = datetime.utcnow() - timedelta(days=3 * 365)
cutoff_timestamp = cutoff_date.timestamp()

def scrape_recent_gmat_posts():
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Subreddit', 'Title', 'Author', 'Score', 'URL', 'Date', 'Text Snippet'])

        for sub in subreddits:
            print(f"Searching r/{sub}...")
            subreddit = reddit.subreddit(sub)
            for submission in subreddit.search(search_query, sort='new', time_filter='all'):
                if submission.created_utc >= cutoff_timestamp:
                    writer.writerow([
                        sub,
                        submission.title,
                        str(submission.author),
                        submission.score,
                        submission.url,
                        datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
                        submission.selftext[:300]
                    ])
                    print(f"Saved: {submission.title[:60]}...")

if __name__ == "__main__":
    scrape_recent_gmat_posts()
    print(f"\n✅ Done. Posts from the last 3 years saved to '{csv_filename}'")