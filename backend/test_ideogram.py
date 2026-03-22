import fal_client
import sys
from dotenv import load_dotenv

load_dotenv()

models = ["fal-ai/ideogram/v2", "fal-ai/ideogram/v2-turbo"]
for m in models:
    print(f"Checking {m}")
    try:
        res = fal_client.subscribe(m, arguments={"prompt": "test"})
        print(f"Success {m}")
    except Exception as e:
        print(f"Failed {m}: {e}")
