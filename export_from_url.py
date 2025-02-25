import json
import requests
import sys

def fetch_reddit_json(url):
    """
    Fetch the Reddit post JSON from the provided URL.
    Reddit posts can be fetched in JSON format by appending ".json" to the URL.
    """
    # Ensure URL ends with .json
    if not url.endswith(".json"):
        if url.endswith("/"):
            url = url[:-1]
        url = url + ".json"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; RedditPostExporter/1.0)"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching Reddit JSON: {response.status_code}")
        print("Response text:", response.text)
        sys.exit(1)
    try:
        data = response.json()
    except Exception as e:
        print("Error decoding JSON:", e)
        print("Response text:", response.text)
        sys.exit(1)
    return data

def convert_reddit_json(data):
    """
    Convert the fetched Reddit JSON into structured fields.
    Reddit returns a list where:
      - data[0] contains the post information.
      - data[1] contains the comments.
    This function extracts:
      - Title (from the post data).
      - Post Body (from the selftext field).
      - Comments: up to 10 separate fields (comment 1, comment 2, ..., comment 10).
    """
    if isinstance(data, list) and len(data) > 0:
        try:
            post_data = data[0]["data"]["children"][0]["data"]
        except Exception as e:
            print("Error extracting post data:", e)
            sys.exit(1)

        title = post_data.get("title", "")
        selftext = post_data.get("selftext", "")
        comments = []

        if len(data) > 1:
            comments_listing = data[1]["data"]["children"]
            for comment in comments_listing:
                if comment.get("kind") == "t1":
                    comment_data = comment.get("data", {})
                    comments.append(comment_data.get("body", ""))

        # Prepare structured output for Airtable
        fields = {
            "title": title,
            "post body": selftext
        }

        # Store comments separately in "comment 1" to "comment 10" fields
        for i in range(10):
            field_name = f"comment {i+1}"
            fields[field_name] = comments[i] if i < len(comments) else ""

        # 🚨 Ensure "comments" is NEVER included 🚨
        if "comments" in fields:
            del fields["comments"]

        return fields

    else:
        print("Unexpected JSON structure.")
        sys.exit(1)

def export_to_airtable(fields):
    """
    Export the provided fields to Airtable.
    """
    airtable_url = "https://api.airtable.com/v0/app5lpnKo3yC9K68N/tblM4dvAAT2l801un"
    headers = {
        "Authorization": "Bearer pat2TDZox4w7gOeVF.6f38d37f23e501c699d81044875f8f5ecdf17d60735878f88fb0d396bf21f875",
        "Content-Type": "application/json"
    }

    # 🚨 Ensure "comments" is NOT in the request 🚨
    if "comments" in fields:
        del fields["comments"]

    payload = {
        "fields": fields
    }

    response = requests.post(airtable_url, headers=headers, json=payload)
    return response

def main():
    if len(sys.argv) < 2:
        print("Usage: python export_from_url.py <reddit_post_url>")
        sys.exit(1)
    url = sys.argv[1]
    reddit_json = fetch_reddit_json(url)
    fields = convert_reddit_json(reddit_json)
    print("Extracted fields:")
    print(fields)
    
    response = export_to_airtable(fields)
    print("\nAirtable response:")
    print("Status code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("Response text:", response.text)

if __name__ == "__main__":
    main()
