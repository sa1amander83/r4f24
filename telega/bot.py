import requests
from django.conf import settings

from r4f24.settings import TOKEN_BOT

url = f"https://api.telegram.org/bot{TOKEN_BOT}/setWebhook?url=http://zabeg.su/"
data = {
    "url": "http://zabeg.su/webhook/"
}


response = requests.post(url, data=data)
print(response.json())