import praw
import json
from datetime import datetime
from airtable import Airtable
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

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
            "author": str(submission.author),
            "content": submission.selftext,
            "score": submission.score,
            "created_utc": datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "comments": []
        }

        # Replace "More Comments" with actual comments
        submission.comments.replace_more(limit=None)

        # Get top 10 comments by score
        all_comments = submission.comments.list()
        sorted_comments = sorted(all_comments, key=lambda x: x.score, reverse=True)[:10]

        for comment in sorted_comments:
            comment_data = {
                "author": str(comment.author),
                "content": comment.body,
                "score": comment.score,
                "created_utc": datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "depth": comment.depth
            }
            post_data["comments"].append(comment_data)

        return post_data

# API endpoint
@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    data = request.json
    post_url = data.get('url')
    
    if not post_url:
        return jsonify({'error': 'No URL provided'}), 400

    scraper = RedditScraper(
        client_id=os.environ.get('REDDIT_CLIENT_ID'),
        client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
        user_agent=os.environ.get('REDDIT_USER_AGENT')
    )
    
    try:
        result = scraper.scrape_post(post_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)