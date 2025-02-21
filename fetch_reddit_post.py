import praw
import json



reddit = praw.Reddit(
    client_id="ufnfNmsCtZRjWVrK9GZIMw",
    client_secret="-nFy49lyA9961GYy0Z_ArMJR-3Vcjg",
    user_agent="thriveatfiftyfive script"
)

# Function to fetch Reddit post details
def fetch_reddit_post(post_url):
    submission = reddit.submission(url=post_url)
    submission_data = {
        "title": submission.title,
        "op": submission.selftext,
        "comments": []
    }

    # Fetch top-level comments
    submission.comments.replace_more(limit=0)  # Avoid "load more comments"
    for comment in submission.comments.list():
        submission_data["comments"].append(comment.body)

    return submission_data

# Save to JSON
def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Input: Reddit post URL
post_url = input("Enter the Reddit post URL: ")
data = fetch_reddit_post(post_url)
save_to_json(data, "reddit_post.json")

print("Reddit post data saved to 'reddit_post.json'.")