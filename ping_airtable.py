import requests

def ping_airtable():
    """
    Sends a GET request to the Airtable API to list records in the target table,
    and prints the status code and response content.
    """
    airtable_url = "https://api.airtable.com/v0/app5lpnKo3yC9K68N/tblM4dvAAT2l801un"
    headers = {
        "Authorization": "Bearer pat2TDZox4w7gOeVF.6f38d37f23e501c699d81044875f8f5ecdf17d60735878f88fb0d396bf21f875",
        "Content-Type": "application/json"
    }
    
    response = requests.get(airtable_url, headers=headers)
    print("Status code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("Response text:", response.text)

if __name__ == "__main__":
    ping_airtable()
