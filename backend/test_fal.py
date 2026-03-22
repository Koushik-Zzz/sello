import os
import fal_client
from app.core.config import settings

print(f"FAL_KEY={os.environ.get('FAL_KEY')}")

try:
    result = fal_client.subscribe(
        "fal-ai/fast-lcm",
        arguments={"prompt": "A cute cat"}
    )
    print("Success fast-lcm:", result)
except Exception as e:
    print("Error:", e)
