import os
import fal_client
from dotenv import load_dotenv

load_dotenv()

print(f"FAL_KEY=***{str(os.environ.get('FAL_KEY'))[-4:]}")

try:
    result = fal_client.subscribe(
        "fal-ai/flux/dev",
        arguments={"prompt": "A cute cat"}
    )
    print("Success flux:", result)
except Exception as e:
    print("Error:", e)
