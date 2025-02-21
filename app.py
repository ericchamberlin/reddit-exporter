from flask import Flask, request, jsonify
import praw
import json
from datetime import datetime
import os

app = Flask(__name__)

# Add health check route
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "API is running"}), 200

class RedditScraper:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def scrape_post(self, post_url):
        submission = self.reddit.submission(url=post_url)
        
        post_data = {
            "title": submission.title,
            "content": f"Original Post:\n{submission.selftext}\n\n",
            "comments": [],
            "plain_text": ""
        }

        submission.comments.replace_more(limit=None)
        all_comments = submission.comments.list()
        sorted_comments = sorted(all_comments, key=lambda x: x.score, reverse=True)[:10]

        formatted_comments = []
        for i, comment in enumerate(sorted_comments, 1):
            comment_text = f"Comment #{i}:\n{comment.body}\n"
            formatted_comments.append(comment_text)
            post_data["comments"].append({
                "text": comment.body,
                "score": comment.score
            })

        post_data["plain_text"] = (
            f"Title: {post_data['title']}\n\n"
            f"{post_data['content']}\n"
            "Top Comments:\n\n" +
            "\n".join(formatted_comments)
        )

        return post_data

@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    try:
        data = request.json
        post_url = data.get('url')
        
        if not post_url:
            return jsonify({'error': 'No URL provided'}), 400

        # Log environment variables (without secrets)
        print(f"Checking credentials: {bool(os.environ.get('REDDIT_CLIENT_ID'))}")
        
        scraper = RedditScraper(
            client_id=os.environ.get('REDDIT_CLIENT_ID'),
            client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
            user_agent=os.environ.get('REDDIT_USER_AGENT')
        )
        
        result = scraper.scrape_post(post_url)
        return jsonify(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)