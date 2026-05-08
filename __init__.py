# __init__.py

"""
ComfyUI-MachinePaintingNodes v2.1.4
Professional color grading, mask tools, filters, and utilities for ComfyUI
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
from .show_value import ShowValue
from .mega_slider import MegaSliderMasterValue, MegaSliderX1, MegaSliderX3, MegaSliderX6, MegaSliderX12
from .dynamic_value_range import DynamicValueRange
from .zimage_latent import ZImageEmptyLatentImage
from .blur_pro import BlurPro
from .image_mask_switch import ImageMaskSwitch
from .frequency_separation import FrequencySeparate, FrequencyCombine
from .noise_grain_pro import NoiseGrainPro
from .inpaint_mask_pro import InpaintMaskPro
from .mask_composite import MaskCompositePro2X, MaskCompositePro6X

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
    "ShowValue": ShowValue,
    "MegaSliderMasterValue": MegaSliderMasterValue,
    "MegaSliderX1": MegaSliderX1,
    "MegaSliderX3": MegaSliderX3,
    "MegaSliderX6": MegaSliderX6,
    "MegaSliderX12": MegaSliderX12,
    "DynamicValueRange": DynamicValueRange,
    "ZImageEmptyLatentImage": ZImageEmptyLatentImage,
    # Filters
    "BlurPro": BlurPro,
    # Utilities (continued)
    "MP_ImageMaskSwitch": ImageMaskSwitch,
    # Frequency Separation
    "FrequencySeparate": FrequencySeparate,
    "FrequencyCombine": FrequencyCombine,
    "NoiseGrainPro": NoiseGrainPro,
    # Inpainting
    "InpaintMaskPro": InpaintMaskPro,
    "MaskCompositePro2X": MaskCompositePro2X,
    "MaskCompositePro6X": MaskCompositePro6X,
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
    "ShowValue": "👾 Show Value",
    "MegaSliderMasterValue": "👾 Mega Slider Master Value",
    "MegaSliderX1": "👾 Mega Slider X1",
    "MegaSliderX3": "👾 Mega Slider X3",
    "MegaSliderX6": "👾 Mega Slider X6",
    "MegaSliderX12": "👾 Mega Slider X12",
    "DynamicValueRange": "👾 Dynamic Value Range",
    "ZImageEmptyLatentImage": "👾 Z-Image Empty Latent Image",
    # Filters
    "BlurPro": "👾 Blur Pro",
    # Utilities (continued)
    "MP_ImageMaskSwitch": "👾 Image <> Mask Switch",
    # Frequency Separation
    "FrequencySeparate": "👾 Frequency Separate",
    "FrequencyCombine": "👾 Frequency Combine",
    "NoiseGrainPro": "👾 Noise Grain Pro",
    # Inpainting
    "InpaintMaskPro": "👾 Inpaint Mask Pro",
    "MaskCompositePro2X": "👾 Mask Composite Pro 2X",
    "MaskCompositePro6X": "👾 Mask Composite Pro 6X",
}

WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print("ComfyUI-MachinePaintingNodes v2.1.4: Loaded 40 nodes")
