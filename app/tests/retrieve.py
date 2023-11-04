import requests
import json

url = "http://localhost:8000/long_term_knowledge"
payload = {
    "query": "Example",
    "top_k": 5  # Replace with your value
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)

print(response.json())
