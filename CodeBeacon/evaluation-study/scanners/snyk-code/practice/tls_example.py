"""Independent setup fixture; scanned as text, never executed by the runner."""
import requests


def unchecked_request(url):
    return requests.get(url, verify=False, timeout=10)


def checked_request(url):
    return requests.get(url, verify=True, timeout=10)
