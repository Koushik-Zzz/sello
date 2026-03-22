import fal_client
import os

os.environ["FAL_KEY"] = "5ce92dd1-24d6-4d1d-ba2b-3c39711bddee:4987d987a9504b6900325fa01869e071" # From the .env file
try:
    result = fal_client.subscribe(
        "fal-ai/google/gemini-3-pro-image",
        arguments={ "prompt": "a test image", "image_size": "square" }
    )
    print("Success:", result)
except Exception as e:
    print("Error:", e)
