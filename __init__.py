# __init__.py

"""
ComfyUI-MachinePaintingNodes v1.0.1
Professional tools + Boolean Master & Value Switches
"""

from .color_match_blend import ColorMatchBlend
from .color_adjust_blend import ColorAdjustBlend
from .image_blend_pro import ImageBlendPro
from .brightness_contrast_adjust import BrightnessContrastAdjust
from .boolean_switch_value_output import BooleanSwitchValueOutput      
from .boolean_input_value_switch import BooleanInputValueSwitch         
from .boolean_master_switch import BooleanMasterSwitch
from .boolean import Boolean
from .seed_boolean_lock import SeedBooleanLock

NODE_CLASS_MAPPINGS = {
    "ColorMatchBlend": ColorMatchBlend,
    "ColorAdjustBlend": ColorAdjustBlend,
    "ImageBlendPro": ImageBlendPro,
    "BrightnessContrastAdjust": BrightnessContrastAdjust,
    "BooleanSwitchValueOutput": BooleanSwitchValueOutput,         
    "BooleanInputValueSwitch": BooleanInputValueSwitch,           
    "BooleanMasterSwitch": BooleanMasterSwitch,
    "Boolean": Boolean,
    "SeedBooleanLock": SeedBooleanLock,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ColorMatchBlend": "👾 Color Match Blend",
    "ColorAdjustBlend": "👾 Color Adjust Blend",
    "ImageBlendPro": "👾 Image Blend Pro",
    "BrightnessContrastAdjust": "👾 Brightness Contrast Adjust",
    "BooleanSwitchValueOutput": "👾 Boolean Switch Value Output",
    "BooleanInputValueSwitch": "👾 Boolean Input Value Switch",
    "BooleanMasterSwitch": "👾 Boolean Master Switch",
    "Boolean": "👾 Boolean",
    "SeedBooleanLock": "👾 Seed Boolean Lock",
}

WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print("ComfyUI-MachinePaintingNodes: LOADED SUCCESSFULLY")
