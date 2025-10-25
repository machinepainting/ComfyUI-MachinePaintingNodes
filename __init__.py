"""
ComfyUI-MachinePaintingNodes v1.0.0
Professional Color Grading & Switching Suite
"""

from .color_match_blend import ColorMatchBlend
from .color_adjust_blend import ColorAdjustBlend
from .image_blend_pro import ImageBlendPro
from .slider_pro import SliderPro


NODE_CLASS_MAPPINGS = {
    "ColorMatchBlend": ColorMatchBlend,
    "ColorAdjustBlend": ColorAdjustBlend,
    "ImageBlendPro": ImageBlendPro,
    "SliderPro": SliderPro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ColorMatchBlend": "👾 Color Match Blend",
    "ColorAdjustBlend": "👾 Color Adjust Blend",
    "ImageBlendPro": "👾 Image Blend Pro",
    "SliderPro": "👾 Slider Pro",
}

WEB_DIRECTORY = "./js"
print("✅ ComfyUI-MachinePaintingNodes: LOADED SUCCESSFULLY")