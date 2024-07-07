import os

import requests
from django.conf import settings



url = f"https://api.telegram.org/bot{os.getenv('TOKEN_BOT')}/setWebhook?url=http://zabeg.su/"
data = {
    "url": "http://zabeg.su/webhook/"
}


response = requests.post(url, data=data)
print(response.json())