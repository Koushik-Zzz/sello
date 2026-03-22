import os
import fal_client
from dotenv import load_dotenv

load_dotenv()

print("Testing Nano Banana 2 (Creation)...")
try:
    res = fal_client.subscribe("fal-ai/nano-banana-2", arguments={"prompt": "a cute cat"})
    print("Success T2I:", res)
except Exception as e:
    print("Failed T2I:", e)

