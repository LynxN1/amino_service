import requests
from retrying import retry


@retry
def post(url: str, data=None, headers=None):
    return requests.post(url, data=data, headers=headers)


@retry
def get(url: str, data=None, headers=None):
    return requests.get(url, data=data, headers=headers)


@retry
def delete(url: str, data=None, headers=None):
    return requests.delete(url, data=data, headers=headers)
