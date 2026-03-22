import asyncio
import logging
import base64
from typing import Dict, Any, List, Optional

import fal_client

from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiError(Exception):
    """Gemini service errors."""
    pass

class QuotaExceededError(GeminiError):
    """API quota exceeded."""
    pass

class SafetyError(GeminiError):
    """Content blocked by safety filters."""
    pass

def _upload_if_needed(image_str: str) -> str:
    """Upload data URI to FAL and return the URL, or return URL if already an HTTP link."""
    if image_str.startswith("http"):
        return image_str
    elif image_str.startswith("data:image"):
        header, b64_data = image_str.split(",", 1)
        mime_type = header.split(";")[0].split(":")[1]
        image_bytes = base64.b64decode(b64_data)
        logger.info(f"[gemini-image] Uploading reference image of size {len(image_bytes)} bytes")
        url = fal_client.upload(image_bytes, mime_type)
        return url
    else:
        # Assume it's a raw base64 string without data uri prefix?
        # Try decoding it
        try:
            image_bytes = base64.b64decode(image_str)
            url = fal_client.upload(image_bytes, "image/png")
            return url
        except Exception:
            # Maybe it is a path or invalid string
            logger.warning("[gemini-image] Provided image reference is not a data URI or HTTP link. Returning as is.")
            return image_str

class GeminiImageService:
    """Service for product asset generation using Gemini 3 Image API via Fal AI."""
    
    def __init__(self):
        # We rely on FAL_KEY from environment or settings instead of GEMINI_API_KEY directly 
        self.pro_model = settings.GEMINI_PRO_MODEL  # Expected: fal-ai/gemini-3-pro-image
        self.flash_model = settings.GEMINI_FLASH_MODEL  # Expected: fal-ai/gemini-flash-edit

        # Image generation settings
        self.image_size = settings.GEMINI_IMAGE_SIZE
        self.aspect_ratio = settings.GEMINI_IMAGE_ASPECT_RATIO
        
        logger.info(f"[gemini-image] Initialized with fal.ai Pro model: {self.pro_model}, Flash model: {self.flash_model}")

    def generate_product_images_sync(
        self,
        prompt: str,
        workflow: str,
        image_count: int = 1,
        reference_images: Optional[List[str]] = None,
        is_texture: bool = False,
        base_description: Optional[str] = None,
    ) -> List[str]:
        """Generate clean product views using Gemini Image API via fal.ai (synchronous).
        
        Args:
            prompt: Description of the product or edit instruction
            workflow: "create" or "edit" - determines model selection
            image_count: Number of images to generate
            reference_images: Reference images for edit workflow
            
        Returns:
            List of image URLs
        """
        if workflow == "create":
            model_to_use = self.pro_model
            logger.info(f"[gemini] CREATE workflow: using {model_to_use}")
        elif workflow == "edit":
            model_to_use = self.flash_model
            logger.info(f"[gemini] EDIT workflow: using {model_to_use}")
        else:
            raise ValueError(f"Unknown workflow: {workflow}. Expected 'create' or 'edit'")
        
        valid_images = []
        is_create_flow = workflow == "create"
        
        for i in range(image_count):
            try:
                # For create flow: first image establishes the product, subsequent use it as reference
                if is_create_flow and i == 0:
                    img = self._generate_single_image(
                        prompt,
                        None,
                        model_to_use,
                        angle_index=i,
                        is_texture=is_texture,
                        base_description=base_description,
                    )
                elif is_create_flow and i > 0:
                    # Subsequent views
                    img = self._generate_single_image(
                        prompt,
                        valid_images[:1],
                        model_to_use,
                        angle_index=i,
                        is_texture=is_texture,
                        base_description=base_description,
                    )
                else:
                    # Edit flow
                    img = self._generate_single_image(
                        prompt,
                        reference_images,
                        model_to_use,
                        angle_index=i,
                        is_texture=is_texture,
                        base_description=base_description,
                    )
                
                if img:
                    valid_images.append(img)
                    logger.info(f"[gemini] Image {i+1}/{image_count} generated successfully with model {model_to_use}")
                else:
                    logger.warning(f"[gemini] Image {i+1}/{image_count} generation returned None")
            except Exception as exc:
                logger.error(f"[gemini] Image {i+1}/{image_count} generation failed: {exc}")
                
        logger.info(f"[gemini] Generated {len(valid_images)}/{image_count} valid product images using {model_to_use}")
        return valid_images
    
    async def generate_product_images(
        self,
        prompt: str,
        workflow: str,
        image_count: int = 1,
        reference_images: Optional[List[str]] = None,
        is_texture: bool = False,
        base_description: Optional[str] = None,
    ) -> List[str]:
        return await asyncio.to_thread(
            self.generate_product_images_sync,
            prompt,
            workflow,
            image_count,
            reference_images,
            is_texture,
            base_description,
        )

    def _generate_single_image(
        self,
        prompt: str,
        reference_images: Optional[List[str]],
        model: str,
        angle_index: int = 0,
        is_texture: bool = False,
        base_description: Optional[str] = None,
    ) -> Optional[str]:
        angles = [
            "front view at eye level, perfectly centered",
            "side profile view from the left at eye level",
            "side profile view from the right at eye level",
            "back view at eye level, perfectly centered"
        ]
        angle_description = angles[angle_index] if angle_index < len(angles) else "alternate angle"
        
        if is_texture:
            enhanced_prompt = prompt
        elif reference_images and ("edit" in model.lower() or "image-to-image" in model.lower()):
            # Edit workflow implies gemini-flash-edit which requires prompt and an image URL
            base_desc = (base_description or "").strip() or "the existing product"
            edit_instruction = prompt.strip() or "Apply the requested edit."
            enhanced_prompt = (
                "You are editing the exact same product shown in the reference image.\n\n"
                f"BASE PRODUCT: {base_desc}\n"
                f"USER EDIT REQUEST: {edit_instruction}\n\n"
                "Follow these rules strictly:\n"
                "1. Keep the same product family, proportions, and materials unless the instruction explicitly "
                "changes them. Every other detail must stay identical.\n"
                "2. Interpret casual phrases like \"make it...\", \"color it...\", \"give it...\" as concrete, "
                "visible edits. Exaggerate the requested change so it is obvious in a comparison.\n"
                "3. Maintain the pure white studio background, matching lighting, lens, framing, and camera height.\n"
                f"4. Deliver a crisp studio photograph from {angle_description}. No extra props, text, or watermarks.\n"
            )
        else:
            # CREATE flow
            enhanced_prompt = (
                f"Create a professional studio product photograph of {prompt}, "
                f"shot from a {angle_description}. "
                f"Photograph the product on a pure white background with professional studio lighting that creates "
                f"soft, subtle shadows. Use sharp focus to capture clear, well-defined edges. "
                f"Center the product in the frame and fill the frame while ensuring the entire product is visible - "
                f"nothing should be cropped or cut off. The design should be consistent and suitable for viewing "
                f"from multiple camera angles. Avoid any text overlays, watermarks, or distracting elements."
            )
        
        arguments = {"prompt": enhanced_prompt}
        
        # Determine appropriate arguments based on the model endpoint
        # For gemini-flash-edit, it specifically requires an 'image_url'
        # For gemini-pro-image (text-to-image), it takes 'images' or might not need reference image for prompt unless it's strictly image-to-image
        if reference_images:
            image_url = _upload_if_needed(reference_images[0])
            
            if "nano" in model.lower() and "edit" in model.lower():
                arguments["image_urls"] = [image_url]
            else:
                arguments["image_url"] = image_url

        try:
            logger.info(f"[gemini] Calling fal.ai API with model: {model}, prompt length: {len(enhanced_prompt)}")
            
            result = fal_client.subscribe(
                model,
                arguments=arguments
            )
            
            if isinstance(result, dict) and "images" in result and result["images"]:
                # The format is typically {"images": [{"url": "...", ...}]} or {"image": {"url": "..."}}
                images_list = result.get("images", [])
                if isinstance(images_list, list) and len(images_list) > 0:
                    url = images_list[0].get("url")
                    if url:
                        return url
            
            # fal-ai/gemini-flash-edit might return {"image": {"url": "...", ...}} directly instead of "images" list
            if isinstance(result, dict) and "image" in result:
                url = result["image"].get("url")
                if url:
                    return url
                    
            logger.warning(f"[gemini] Unknown result structure from fal.ai: {result}")
            return None
        except Exception as exc:
            logger.error(f"[gemini] Fal API call failed: {exc}", exc_info=True)
            raise GeminiError(f"Fal API call failed: {exc}") from exc


# Initialize service
gemini_image_service = GeminiImageService()
