import os
import fal_client
from dotenv import load_dotenv

load_dotenv()

image_url = "https://v3b.fal.media/files/b/0a930d07/r3469uLEfFUdqsyX_U10u.jpg"

try:
    print("Testing flux dev with extra unused image_url parameter...")
    result = fal_client.subscribe(
        "fal-ai/flux/dev",
        arguments={
            "prompt": "a cute cat",
            "image_url": image_url
        }
    )
    print("Success flux:", result)
except Exception as e:
    print("Error flux:", e)
