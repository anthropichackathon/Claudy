import requests


def test_insert_many(url, data):
    response = requests.post(url, json=data)
    print(response.status_code)
    print(response.json())


url = "http://localhost:8000/long_term_knowledge/insert_many"
data = {
    "contents": [
        {
            "content": "This is some example content 1.",
        },
        {
            "content": "This is some example content 2.",
        },
        {
            "content": "This is some example content 3.",
        }
    ]
}

test_insert_many(url, data)
