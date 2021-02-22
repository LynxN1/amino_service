import requests
from retrying import retry


@retry
def request(method: str, url: str, data=None, headers=None):
    if method == "POST":
        return requests.post(url, data=data, headers=headers)
    elif method == "GET":
        return requests.get(url, data=data, headers=headers)
    elif method == "DELETE":
        return requests.delete(url, headers=headers, data=data)
