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
        print("Request received")
        data = request.json
        post_url = data.get('url')
        print(f"Extracted URL: {post_url}")
        
        if not post_url:
            return jsonify({'error': 'No URL provided'}), 400

        # Check if environment variables exist and print their status
        env_vars = {
            'REDDIT_CLIENT_ID': bool(os.environ.get('REDDIT_CLIENT_ID')),
            'REDDIT_CLIENT_SECRET': bool(os.environ.get('REDDIT_CLIENT_SECRET')),
            'REDDIT_USER_AGENT': bool(os.environ.get('REDDIT_USER_AGENT'))
        }
        print(f"Environment variables status: {env_vars}")
        
        if not all(env_vars.values()):
            return jsonify({'error': 'Missing Reddit credentials'}), 500

        scraper = RedditScraper(
            client_id=os.environ.get('REDDIT_CLIENT_ID'),
            client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
            user_agent=os.environ.get('REDDIT_USER_AGENT')
        )
        
        try:
            print("Attempting to scrape post...")
            result = scraper.scrape_post(post_url)
            print("Scraping successful")
            return jsonify(result)
        except Exception as e:
            print(f"Reddit API Error: {str(e)}")
            return jsonify({'error': f'Reddit API Error: {str(e)}'}), 500
            
    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({'error': f'Server Error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)