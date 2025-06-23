import praw
import os

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
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME', 'sireeshy') # Optional, for user-based authentication
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD', 'Sireesh!2025') # Optional, for user-based authentication

SUBREDDIT_NAME = 'GMAT' # Changed from 'GRE' to 'GMAT'
SEARCH_KEYWORDS = ['GMAT preparation resources', 'GMAT study materials', 'GMAT prep books', 'GMAT quant resources', 'GMAT verbal resources', 'GMAT official guide', 'GMAT practice test', 'GMAT prep', 'GMAT preparation', 'improve GMAT score', 'gmat quant syllabus', 'gmat sections', 'target test prep gmat','best gmat coaching in india', 'egmat', 'GMAT', 'gmat', 'eGMAT', 'GMAT focus', 'GMAT mock test', 'GMAT drills', 'GMAT practice', 'GMAT questions', 'GMAT materials' ] # Updated keywords
LIMIT_POSTS = 20 # Number of top posts to retrieve for each keyword
LIMIT_COMMENTS_PER_POST = 5 # Number of top comments to retrieve per post

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

def get_gre_conversations(reddit_instance, subreddit_name, search_keywords, limit_posts, limit_comments):
    """
    Fetches conversations (posts and comments) from a specified subreddit
    based on search keywords.
    """
    if not reddit_instance:
        print("Reddit instance not initialized. Cannot fetch conversations.")
        return []

    subreddit = reddit_instance.subreddit(subreddit_name)
    all_conversations = []
    processed_submission_ids = set() # To avoid duplicate posts if they match multiple keywords

    print(f"\nSearching subreddit r/{subreddit_name} for posts related to GMAT preparation...") # Updated print message

    for keyword in search_keywords:
        print(f"\n--- Searching for: '{keyword}' ---")
        try:
            # Search for submissions (posts) matching the keyword, sorted by relevance, over all time
            for submission in subreddit.search(keyword, sort='relevance', time_filter='all', limit=limit_posts):
                if submission.id not in processed_submission_ids:
                    print(f"\nPost Title: {submission.title}")
                    print(f"URL: {submission.url}")
                    print(f"Score: {submission.score}")
                    print(f"Number of Comments: {submission.num_comments}")
                    if submission.selftext:
                        # Displaying only first 500 characters of selftext to keep output manageable
                        print(f"Self-Text (excerpt): {submission.selftext[:500]}{'...' if len(submission.selftext) > 500 else ''}")

                    # Fetch and display top comments
                    print("Comments:")
                    submission.comments.replace_more(limit=0) # Flatten comment tree, limit=0 removes 'more comments'
                    comments_processed = 0
                    for top_level_comment in submission.comments.list():
                        if comments_processed >= limit_comments:
                            break
                        if isinstance(top_level_comment, praw.models.Comment): # Ensure it's a comment, not MoreComments
                            print(f"  - User: {top_level_comment.author.name if top_level_comment.author else '[deleted]'}")
                            print(f"    Score: {top_level_comment.score}")
                            # Displaying only first 200 characters of comment body
                            print(f"    Comment: {top_level_comment.body[:200]}{'...' if len(top_level_comment.body) > 200 else ''}")
                            comments_processed += 1
                    if comments_processed == 0:
                        print("  No top comments displayed.")
                    print("-" * 50)
                    processed_submission_ids.add(submission.id)

                    all_conversations.append({
                        'title': submission.title,
                        'url': submission.url,
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'selftext': submission.selftext,
                        'comments': [
                            {
                                'author': c.author.name if c.author else '[deleted]',
                                'score': c.score,
                                'body': c.body
                            } for c in submission.comments.list()[:limit_comments] if isinstance(c, praw.models.Comment)
                        ]
                    })
        except Exception as e:
            print(f"Error searching for '{keyword}': {e}")

    print(f"\nFinished searching. Found {len(processed_submission_ids)} unique relevant posts.")
    return all_conversations

# --- Main execution ---
if __name__ == "__main__":
    reddit = initialize_reddit()
    if reddit:
        conversations = get_gre_conversations(
            reddit,
            SUBREDDIT_NAME,
            SEARCH_KEYWORDS,
            LIMIT_POSTS,
            LIMIT_COMMENTS_PER_POST
        )
        # You can now process 'conversations' list further, e.g., save to a file.
        # For this example, we just printed it to console.
