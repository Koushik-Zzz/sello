import os
import fal_client
from dotenv import load_dotenv

load_dotenv()

try:
    result = fal_client.subscribe(
        "fal-ai/gemini-3-pro-image",
        arguments={"prompt": "A cute cat"}
    )
    print("Success gemini:", result)
except Exception as e:
    print("Error:", e)
