import requests
import json

url = "http://localhost:8000/long_term_knowledge/delete_one"
payload = {
    "id": 'S7104518790811934488'
}
headers = {
    "Content-Type": "application/json"
}

response = requests.delete(url, data=json.dumps(payload), headers=headers)

print(response.status_code)
print(response.text)
