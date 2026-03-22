import fal_client
import sys
import os
from dotenv import load_dotenv

load_dotenv()

try:
    models = ["fal-ai/nanobana", "fal-ai/nanobana-pro", "nanobana", "nanobana-pro"]
    for m in models:
        print(f"Checking {m}")
        try:
            res = fal_client.subscribe(m, arguments={"prompt": "test"})
            print(f"Success {m}")
        except Exception as e:
            print(f"Failed {m}: {e}")
except Exception as e:
    print(e)
