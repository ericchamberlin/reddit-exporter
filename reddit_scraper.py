import praw
import json
from datetime import datetime

class RedditScraper:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def scrape_post(self, post_url):
        submission = self.reddit.submission(url=post_url)
        
        # Get post data
        post_data = {
            "title": submission.title,
            "content": f"Original Post:\n{submission.selftext}\n\n",
            "comments": [],
            "plain_text": ""  # New field for formatted text
        }

        # Replace "More Comments" with actual comments
        submission.comments.replace_more(limit=None)

        # Get top 10 comments by score
        all_comments = submission.comments.list()
        sorted_comments = sorted(all_comments, key=lambda x: x.score, reverse=True)[:10]

        # Format comments into plain text
        formatted_comments = []
        for i, comment in enumerate(sorted_comments, 1):
            comment_text = f"Comment #{i}:\n{comment.body}\n"
            formatted_comments.append(comment_text)
            post_data["comments"].append({
                "text": comment.body,
                "score": comment.score
            })

        # Create a clean plain text version
        post_data["plain_text"] = (
            f"Title: {post_data['title']}\n\n"
            f"{post_data['content']}\n"
            "Top Comments:\n\n" +
            "\n".join(formatted_comments)
        )

        return post_data

    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# Usage example
if __name__ == "__main__":
    CLIENT_ID = "29G1hvW7cVvNstfws-u4Ng"
    CLIENT_SECRET = "5pLKG-wpeW-06BWIOAI8paPwZ1TpYQ"
    USER_AGENT = "conversations/1.0.0"
    
    scraper = RedditScraper(CLIENT_ID, CLIENT_SECRET, USER_AGENT)
    
    post_url = "https://www.reddit.com/r/retirement/comments/1i7oyh9/thinking_of_retiring_earlier_than_planned/"
    
    # Scrape the post and comments
    post_data = scraper.scrape_post(post_url)
    
    # Save to JSON file
    output_filename = f"reddit_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    scraper.save_to_json(post_data, output_filename)