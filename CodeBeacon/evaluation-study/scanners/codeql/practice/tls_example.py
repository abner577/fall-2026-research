import requests


def unchecked_request(url):
    return requests.get(url, verify=False, timeout=10)


def checked_request(url):
    return requests.get(url, verify=True, timeout=10)