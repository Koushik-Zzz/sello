import os
from dotenv import load_dotenv
import fal_client

load_dotenv()

try:
    print("Testing text to image")
    result = fal_client.subscribe(
        "fal-ai/gemini-3-pro-image-preview",
        arguments={
            "prompt": "A cute small white coffee cup"
        }
    )
    print("t2i result:", result)
except Exception as e:
    print("t2i failed:", e)

