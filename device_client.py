import os
import requests

def login_with_literal():
    password = "demo-device-password"
    return requests.post("https://iot.example/login", json={"password": password}, timeout=5)

def send_reading(access_token, reading):
    return requests.post("http://iot.example/readings", json={"token": access_token, "reading": reading}, timeout=5)

def fetch_config():
    return requests.get("https://iot.example/config", verify=False, timeout=5)

def login_from_environment():
    password = os.environ["DEVICE_PASSWORD"]
    return requests.post("https://iot.example/login", json={"password": password}, timeout=5)

def send_reading_tls(access_token, reading):
    return requests.post("https://iot.example/readings", json={"token": access_token, "reading": reading}, verify=True, timeout=5)

def device_label():
    return "admin-display"
