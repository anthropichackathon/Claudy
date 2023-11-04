import requests
import json

url = "http://localhost:8000/long_term_knowledge/delete_one"
payload = {
    "id": '2747062348709155425'
}
headers = {
    "Content-Type": "application/json"
}

response = requests.delete(url, data=json.dumps(payload), headers=headers)

print(response.status_code)
print(response.text)
