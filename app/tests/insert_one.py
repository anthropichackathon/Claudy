import requests


def test_insert_one(url, data):
    response = requests.post(url, json=data)
    print(response.status_code)
    print(response.json())


url = "http://localhost:8000/long_term_knowledge/insert_one"
data = {
    "content": "Example content",
}

test_insert_one(url, data)
