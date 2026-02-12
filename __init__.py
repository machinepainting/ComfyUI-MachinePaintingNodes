# __init__.py

"""
ComfyUI-MachinePaintingNodes v2.0.2
Professional color grading, mask tools, and utilities for ComfyUI
"""

# Combined files
from .boolean_utils import (
    Boolean, BooleanInvert, BooleanSwitchValueOutput, 
    BooleanInputValueSwitch, BooleanMasterSwitch
)
from .analysis_view import HistogramView, ColorWheelView
from .tonal_adjust import LevelsAdjust, AutoLevels, BrightnessContrastAdjust
from .color_blend import ColorMatchBlend, ColorAdjustBlend
from .remove_background import RemoveBackgroundPro, MaskEditor, ApplyMask

# Standalone files
from .image_blend_pro import ImageBlendPro
from .curves_adjust_pro import CurvesAdjustPro
from .channel_mask_pro import ChannelMaskPro
from .selective_color_pro import SelectiveColorPro
from .lut_apply import LUTApply
from .seed_lock import SeedLock
from .text_notes import TextNotes
from .show_text import ShowText
from .text_string import TextString

NODE_CLASS_MAPPINGS = {
    # Color Adjustment
    "CurvesAdjustPro": CurvesAdjustPro,
    "LevelsAdjust": LevelsAdjust,
    "AutoLevels": AutoLevels,
    "BrightnessContrastAdjust": BrightnessContrastAdjust,
    "SelectiveColorPro": SelectiveColorPro,
    "ColorMatchBlend": ColorMatchBlend,
    "ColorAdjustBlend": ColorAdjustBlend,
    "LUTApply": LUTApply,
    # Blending
    "ImageBlendPro": ImageBlendPro,
    # Mask & Background
    "RemoveBackgroundPro": RemoveBackgroundPro,
    "MaskEditor": MaskEditor,
    "ApplyMask": ApplyMask,
    "ChannelMaskPro": ChannelMaskPro,
    # Analysis
    "HistogramView": HistogramView,
    "ColorWheelView": ColorWheelView,
    # Utilities
    "Boolean": Boolean,
    "BooleanInvert": BooleanInvert,
    "BooleanSwitchValueOutput": BooleanSwitchValueOutput,
    "BooleanInputValueSwitch": BooleanInputValueSwitch,
    "BooleanMasterSwitch": BooleanMasterSwitch,
    "SeedLock": SeedLock,
    "TextNotes": TextNotes,
    "ShowText": ShowText,
    "TextString": TextString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Color Adjustment
    "CurvesAdjustPro": "👾 Curves Adjust Pro",
    "LevelsAdjust": "👾 Levels Adjust",
    "AutoLevels": "👾 Auto Levels",
    "BrightnessContrastAdjust": "👾 Brightness Contrast Adjust",
    "SelectiveColorPro": "👾 Selective Color Pro",
    "ColorMatchBlend": "👾 Color Match Blend",
    "ColorAdjustBlend": "👾 Color Adjust Blend",
    "LUTApply": "👾 LUT Apply",
    # Blending
    "ImageBlendPro": "👾 Image Blend Pro",
    # Mask & Background
    "RemoveBackgroundPro": "👾 Remove Background Pro",
    "MaskEditor": "👾 Mask Editor",
    "ApplyMask": "👾 Apply Mask",
    "ChannelMaskPro": "👾 Channel Mask Pro",
    # Analysis
    "HistogramView": "👾 Histogram View",
    "ColorWheelView": "👾 Color Wheel View",
    # Utilities
    "Boolean": "👾 Boolean",
    "BooleanInvert": "👾 Boolean Invert",
    "BooleanSwitchValueOutput": "👾 Boolean Switch Value Output",
    "BooleanInputValueSwitch": "👾 Boolean Input Value Switch",
    "BooleanMasterSwitch": "👾 Boolean Master Switch",
    "SeedLock": "👾 Seed Lock",
    "TextNotes": "👾 Text Notes",
    "ShowText": "👾 Show Text",
    "TextString": "👾 Text String",
}

WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print("ComfyUI-MachinePaintingNodes v2.0.2: Loaded 24 nodes")
