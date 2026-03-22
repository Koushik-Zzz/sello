import os
import fal_client
from dotenv import load_dotenv

load_dotenv()

image_url = "https://v3b.fal.media/files/b/0a930d07/r3469uLEfFUdqsyX_U10u.jpg"

try:
    print("Testing image-to-image...")
    result = fal_client.subscribe(
        "fal-ai/flux/dev/image-to-image",
        arguments={
            "prompt": "make it winter",
            "image_url": image_url
        }
    )
    print("Success flux i2i:", result)
except Exception as e:
    print("Error i2i:", e)
