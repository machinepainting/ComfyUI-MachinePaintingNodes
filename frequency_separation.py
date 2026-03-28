import torch
import numpy as np


class FrequencySeparate:
    """
    Splits an image into high and low frequency layers using the Photoshop
    Apply Image method: Scale 2, Offset 128, Subtract.

    Feed the original image and a blurred version (from Blur Pro or any blur node).
    The high frequency output is a neutral gray layer containing texture/detail only.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original": ("IMAGE",),
                "low_frequency": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("thru", "high_frequency", "low_frequency")
    FUNCTION = "separate"
    CATEGORY = "MachinePaintingNodes/Filter"

    def separate(self, original, low_frequency):
        orig = original.detach().clone()
        low = low_frequency.detach().clone()

        # Photoshop Apply Image: Scale 2, Offset 128, Subtract
        # high = (original - low) / 2 + 0.5
        high = (orig - low) / 2.0 + 0.5

        high = torch.clamp(high, 0.0, 1.0)

        return (original, high, low_frequency)


class FrequencyCombine:
    """
    Recombines high and low frequency layers using Linear Light blend.

    result = low + 2 * (high - 0.5)

    Opacity controls how much texture (high frequency) is applied.
    At 0: just the low frequency (smooth). At 1: full reconstruction.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "high_frequency": ("IMAGE",),
                "low_frequency": ("IMAGE",),
            },
            "optional": {
                "opacity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "combine"
    CATEGORY = "MachinePaintingNodes/Filter"

    def combine(self, high_frequency, low_frequency, opacity=1.0):
        low = low_frequency.detach().clone()

        # Linear Light: result = low + 2 * (high - 0.5)
        # With opacity: result = low + 2 * (high - 0.5) * opacity
        result = low + 2.0 * (high_frequency - 0.5) * opacity

        result = torch.clamp(result, 0.0, 1.0)

        return (result,)
