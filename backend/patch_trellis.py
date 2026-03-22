import re

with open("backend/app/integrations/trellis.py", "r") as f:
    code = f.read()

upload_fn = """
def _upload_if_needed(image_str: str) -> str:
    \"\"\"Upload data URI to FAL and return the URL, or return URL if already an HTTP link.\"\"\"
    if image_str.startswith("http"):
        return image_str
    elif image_str.startswith("data:image"):
        import base64
        import fal_client
        header, b64_data = image_str.split(",", 1)
        mime_type = header.split(";")[0].split(":")[1]
        image_bytes = base64.b64decode(b64_data)
        return fal_client.upload(image_bytes, mime_type)
    else:
        # Assume it's a raw base64 string without data uri prefix?
        try:
            import base64
            import fal_client
            image_bytes = base64.b64decode(image_str)
            return fal_client.upload(image_bytes, "image/png")
        except Exception:
            return image_str
"""

# Insert upload function after imports
if "def _upload_if_needed" not in code:
    code = re.sub(r'(import fal_client\n)', r'\1\n' + upload_fn + '\n', code)

# Look for modifying the images array before sending to fal
replacement = """
            use_multi = use_multi_image and len(images) > 1
            
            # Ensure images are uploaded if they are data URIs
            images = [_upload_if_needed(img) for img in images]
            
            logger.info("=" * 80)
"""
code = code.replace("""
            use_multi = use_multi_image and len(images) > 1
            
            logger.info("=" * 80)
""", replacement)

with open("backend/app/integrations/trellis.py", "w") as f:
    f.write(code)

