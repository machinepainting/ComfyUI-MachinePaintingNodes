"""
ComfyUI-MachinePaintingNodes v1.0.0
Professional Color Image Match, Color Adjust, and Image Blending Tools
"""

from .color_match_blend import ColorMatchBlend
from .color_adjust_blend import ColorAdjustBlend
from .image_blend_pro import ImageBlendPro


NODE_CLASS_MAPPINGS = {
    "ColorMatchBlend": ColorMatchBlend,
    "ColorAdjustBlend": ColorAdjustBlend,
    "ImageBlendPro": ImageBlendPro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ColorMatchBlend": "👾 Color Match Blend",
    "ColorAdjustBlend": "👾 Color Adjust Blend",
    "ImageBlendPro": "👾 Image Blend Pro",
}

WEB_DIRECTORY = "./js"
print("✅ ComfyUI-MachinePaintingNodes: LOADED SUCCESSFULLY")