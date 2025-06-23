import praw
import os
import csv # Import the csv module

# --- Configuration ---
# You need to create a Reddit application to get these credentials.
# Go to https://www.reddit.com/prefs/apps/
# Create a 'script' type app.
# Fill in the 'name', 'client_id', 'client_secret', and 'user_agent' below.
# 'redirect_uri' can be http://localhost:8080 if you don't have a specific one.

# It's recommended to store these in environment variables or a separate config file
# for security, rather than hardcoding them. For demonstration, we'll use placeholders.
# Replace with your actual credentials:
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', 'PzKE5js_EwgTQ1iJmX_16w')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '6yNPkwxRsnfnz16H1BBsIsEfQk5Efg')
REDDIT_USER_AGENT = 'GMATopinionresearch_by_sireeshy' # Be descriptive!
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME', 'sireeshy') # Optional, for user-based authentication. Changed 'None' to None.
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD', 'Sireesh!2025') # Optional, for user-based authentication. Changed 'None' to None.

SUBREDDIT_NAME = ['GMAT', 'MBA', 'GMATpreparation'] # Added more subreddits
SEARCH_KEYWORDS = ['GMAT preparation resources', 'GMAT study materials', 'GMAT prep books', 'GMAT quant resources', 'GMAT verbal resources', 'GMAT official guide', 'GMAT practice test', 'GMAT prep', 'GMAT preparation', 'improve GMAT score', 'gmat quant syllabus', 'gmat sections', 'target test prep gmat','best gmat coaching in india', 'egmat', 'GMAT', 'gmat', 'eGMAT', 'GMAT focus', 'GMAT mock test', 'GMAT drills', 'GMAT practice', 'GMAT questions', 'GMAT materials' ] # Updated keywords
LIMIT_POSTS = 20 # Number of top posts to retrieve for each keyword
LIMIT_COMMENTS_PER_POST = 5 # Number of top comments to retrieve per post
CSV_FILENAME = 'gmat_reddit_conversations.csv' # Define the output CSV filename

def initialize_reddit():
    """Initializes and returns a PRAW Reddit instance."""
    try:
        # If you're only reading public content and don't need user-specific actions,
        # you can omit username and password. PRAW will use an "unauthenticated"
        # script instance. If you need to access private data or act as a user,
        # provide username and password.
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            username=REDDIT_USERNAME if REDDIT_USERNAME and REDDIT_PASSWORD else None,
            password=REDDIT_PASSWORD if REDDIT_USERNAME and REDDIT_PASSWORD else None
        )
        print("Successfully connected to Reddit API.")
        return reddit
    except Exception as e:
        print(f"Error initializing Reddit API: {e}")
        print("Please ensure your REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT are correct.")
        print("If using username/password, ensure they are also correct.")
        return None

import datetime  # Make sure this is already imported

def get_gre_conversations(reddit_instance, subreddit_names, search_keywords, limit_posts=None, limit_comments=None):
    """Fetch posts and full comments from a subreddit, filtered by date."""
    if not reddit_instance:
        print("Reddit instance not initialized. Cannot fetch conversations.")
        return []
    for subreddit_name in subreddit_names:
        subreddit = reddit_instance.subreddit(subreddit_name)
    all_conversations = []
    processed_submission_ids = set()

    print(f"\n🔍 Searching r/{subreddit_name} for posts related to GMAT preparation...")

    for keyword in search_keywords:
        print(f"\n--- Searching for keyword: '{keyword}' ---")
        try:
            for submission in subreddit.search(keyword, sort='relevance', time_filter='all', limit=None):
                # Convert post time and apply filter
                post_time = datetime.datetime.utcfromtimestamp(submission.created_utc)
                if post_time < datetime.datetime(2021, 1, 1):
                    continue  # Skip posts before 2021

                if submission.id in processed_submission_ids:
                    continue

                print(f"\n📌 Title: {submission.title}")
                print(f"🕒 Posted on: {post_time.isoformat()}")
                print(f"💬 Comments: {submission.num_comments}")

                # Fetch all top-level comments
                submission.comments.replace_more(limit=0)
                comments_data = []
                for comment in submission.comments.list():
                    if isinstance(comment, praw.models.Comment):
                        comment_data = {
                            'author': comment.author.name if comment.author else '[deleted]',
                            'score': comment.score,
                            'body': comment.body,
                            'created_time': datetime.datetime.utcfromtimestamp(comment.created_utc).isoformat()
                        }
                        comments_data.append(comment_data)

                all_conversations.append({
                    'id': submission.id,
                    'title': submission.title,
                    'url': submission.url,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'selftext': submission.selftext,
                    'post_time': post_time.isoformat(),
                    'subreddit': subreddit_name,
                    'comments': comments_data
                })

                processed_submission_ids.add(submission.id)
        except Exception as e:
            print(f"❌ Error fetching for keyword '{keyword}': {e}")

    print(f"\n✅ Done searching r/{subreddit_name}. Found {len(processed_submission_ids)} unique posts.")
    return all_conversations
def save_conversations_to_csv(conversations_data, post_filename, comment_filename):
    if not conversations_data:
        print("No data to save to CSV.")
        return

    # Columns for each file
    post_fields = ['post_id', 'title', 'url', 'score', 'num_comments', 'selftext', 'post_time']
    comment_fields = ['post_id', 'author', 'score', 'created_time', 'body']

    try:
        with open(post_filename, mode='w', newline='', encoding='utf-8') as post_file, \
             open(comment_filename, mode='w', newline='', encoding='utf-8') as comment_file:

            post_writer = csv.DictWriter(post_file, fieldnames=post_fields)
            comment_writer = csv.DictWriter(comment_file, fieldnames=comment_fields)

            post_writer.writeheader()
            comment_writer.writeheader()

            for post in conversations_data:
                post_id = post.get('id', '')
                post_writer.writerow({
                    'post_id': post_id,
                    'title': post.get('title', ''),
                    'url': post.get('url', ''),
                    'score': post.get('score', 0),
                    'num_comments': post.get('num_comments', 0),
                    'selftext': post.get('selftext', ''),
                    'post_time': post.get('post_time', '')
                })

                for comment in post.get('comments', []):
                    comment_writer.writerow({
                        'post_id': post_id,
                        'author': comment.get('author', ''),
                        'score': comment.get('score', 0),
                        'created_time': comment.get('created_time', ''),
                        'body': comment.get('body', '')
                    })

        print(f"✅ Saved posts to '{post_filename}'")
        print(f"✅ Saved comments to '{comment_filename}'")

    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")


# --- Main execution ---
if __name__ == "__main__":
    reddit = initialize_reddit()
    if reddit:
        conversations = get_gre_conversations(
            reddit,
            SUBREDDIT_NAME,
            SEARCH_KEYWORDS,
            #LIMIT_POSTS,
            #LIMIT_COMMENTS_PER_POST
        )
        # Call the new function to save data to CSV
        save_conversations_to_csv(
            conversations,
            post_filename='gmat_posts.csv',
            comment_filename='gmat_comments.csv'
        )

