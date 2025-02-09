import requests

from config import PROXY, URL_L_SITE

proxy = PROXY
proxies = {
    "http": proxy,
    "https": proxy,
}

try:
    response = requests.get(URL_L_SITE, proxies=proxies, timeout=10)
    print("Proxy is working:", response.status_code)
except Exception as e:
    print("Proxy failed:", e)
