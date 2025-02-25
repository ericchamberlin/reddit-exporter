import json
import requests

def convert_json_to_fields(json_data):
    """
    Extract fields from Reddit JSON and format them for Airtable.
    """
    title = json_data.get("title", "")
    post_body = json_data.get("selftext", "")

    # Extract up to 10 comments, but do not store them in a "comments" field.
    comments_list = [
        comment.get("body", "") if isinstance(comment, dict) else comment 
        for comment in json_data.get("comments", [])
    ]

    # Prepare the Airtable field mapping (excluding "comments")
    fields = {
        "title": title,
        "post body": post_body  # ✅ Matches Airtable's "post body"
    }

    # Assign comments to separate fields
    for i in range(10):
        field_name = f"comment {i+1}"
        fields[field_name] = comments_list[i] if i < len(comments_list) else ""

    # 🚨 Explicitly remove "comments" if it's still present 🚨
    if "comments" in fields:
        del fields["comments"]

    return fields

def export_to_airtable(fields):
    """
    Export the extracted fields to Airtable.
    """
    airtable_url = "https://api.airtable.com/v0/app5lpnKo3yC9K68N/tblM4dvAAT2l801un"
    headers = {
        "Authorization": "Bearer pat2TDZox4w7gOeVF.6f38d37f23e501c699d81044875f8f5ecdf17d60735878f88fb0d396bf21f875",
        "Content-Type": "application/json"
    }
    payload = {"fields": fields}

    response = requests.post(airtable_url, headers=headers, json=payload)
    return response

def main():
    input_file = "reddit_post_20250124_075808.json"
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return

    # Extract fields properly
    fields = convert_json_to_fields(json_data)

    # 🚨 Debugging Step: Print to Confirm "comments" is NOT in the output 🚨
    print("Extracted fields BEFORE sending to Airtable:")
    print(json.dumps(fields, indent=4))

    if "comments" in fields:
        print("🚨 WARNING: 'comments' field is still present! It should be removed before sending to Airtable.")
        del fields["comments"]  # Final safeguard

    # Export to Airtable
    response = export_to_airtable(fields)
    print("\nAirtable response:")
    print("Status code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("Response text:", response.text)

if __name__ == "__main__":
    main()