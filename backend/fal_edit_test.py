import os
from dotenv import load_dotenv
import fal_client

load_dotenv()

try:
    result = fal_client.subscribe(
        "fal-ai/gemini-3-pro-image-preview",
        arguments={
            "prompt": "A cute small white coffee cup",
            "image_url": "https://v3b.fal.media/files/b/0a930c60/qnoY5pZSSGUPi2Be3F54E.png"
        }
    )
    print("t2i result:", result)
except Exception as e:
    print("t2i failed:", e)

