import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

url = 'https://www.bilibili.com/v/popular/rank/hot'

resp = requests.get(url, headers=headers, timeout=10)
print(f"鐘舵€佺爜: {resp.status_code}")

soup = BeautifulSoup(resp.text, 'html.parser')

titles = soup.find_all('div', class_='title')
for idx, title in enumerate(titles[:10], 1):
    print(f"{idx}. {title.text.strip()}")
