import json
import requests
import sys
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Airtable details
AIRTABLE_URL = "https://api.airtable.com/v0/app5lpnKo3yC9K68N/tblM4dvAAT2l801un"
AIRTABLE_HEADERS = {
    "Authorization": "Bearer pat2TDZox4w7gOeVF.6f38d37f23e501c699d81044875f8f5ecdf17d60735878f88fb0d396bf21f875",
    "Content-Type": "application/json"
}

def fetch_reddit_json(url):
    """Fetch Reddit post JSON"""
    if not url.endswith(".json"):
        url = url.rstrip("/") + ".json"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RedditPostExporter/1.0)"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed to fetch Reddit JSON: {response.status_code}"}
    return response.json()

def convert_reddit_json(data):
    """Extract post title, body, and top 10 comments"""
    if isinstance(data, list) and len(data) > 0:
        post_data = data[0]["data"]["children"][0]["data"]
        title = post_data.get("title", "")
        selftext = post_data.get("selftext", "")
        comments = []

        if len(data) > 1:
            comments_listing = data[1]["data"]["children"]
            for comment in comments_listing[:10]:  # Limit to top 10 comments
                if comment.get("kind") == "t1":
                    comment_data = comment.get("data", {})
                    comments.append(comment_data.get("body", ""))

        fields = {"title": title, "post body": selftext}
        for i in range(10):
            fields[f"comment {i+1}"] = comments[i] if i < len(comments) else ""

        return fields
    return {"error": "Invalid Reddit JSON structure"}

def export_to_airtable(fields):
    """Send extracted data to Airtable"""
    payload = {"fields": fields}
    response = requests.post(AIRTABLE_URL, headers=AIRTABLE_HEADERS, json=payload)
    return response

@app.route("/export", methods=["GET"])
def export():
    """API Endpoint to trigger Reddit export"""
    reddit_url = request.args.get("url")
    if not reddit_url:
        return jsonify({"error": "Missing Reddit URL"}), 400

    reddit_json = fetch_reddit_json(reddit_url)
    extracted_data = convert_reddit_json(reddit_json)
    
    if "error" in extracted_data:
        return jsonify(extracted_data), 400
    
    airtable_response = export_to_airtable(extracted_data)
    
    return jsonify({
        "status": airtable_response.status_code,
        "airtable_response": airtable_response.json(),
        "extracted_data": extracted_data
    })

def main():
    """Run script manually (for local testing)"""
    if len(sys.argv) < 2:
        print("Usage: python export_from_url.py <reddit_post_url>")
        sys.exit(1)

    url = sys.argv[1]
    reddit_json = fetch_reddit_json(url)
    fields = convert_reddit_json(reddit_json)
    print("Extracted fields:", json.dumps(fields, indent=4))

    airtable_response = export_to_airtable(fields)
    print("\nAirtable response:", airtable_response.status_code)
    print(airtable_response.json())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        app.run(host="0.0.0.0", port=10000)