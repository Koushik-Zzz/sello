import os
import fal_client
from dotenv import load_dotenv

load_dotenv()

image_url = "https://v3b.fal.media/files/b/0a930d07/r3469uLEfFUdqsyX_U10u.jpg"
try:
    res = fal_client.subscribe(
        "fal-ai/nano-banana-pro/edit", 
        arguments={
            "prompt": "make the cat orange",
            "image_urls": [image_url]
        }
    )
    print("Success I2I:", res)
except Exception as e:
    print("Failed I2I:", e)
