import requests

TOKEN = "8857941292:AAGjnUfYKZk6K6GiTZ0cqL9lkS2pCrnfxlQ"

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(url)

print(response.json())