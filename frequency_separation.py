import torch
import numpy as np


class FrequencySeparate:
    """
    Splits an image into high and low frequency layers.
    Feed the original image and a blurred version (from Blur Pro or any blur node).
    The high frequency layer contains texture/detail, the low frequency is passed through.

    Subtract mode: Photoshop-style Linear Light separation.
    Divide mode: Fewer artifacts in dark regions, uses epsilon for safety.
    """

    MODES = ["subtract", "divide"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original": ("IMAGE",),
                "low_frequency": ("IMAGE",),
                "mode": (cls.MODES, {"default": "subtract"}),
            },
            "optional": {
                "epsilon": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.001,
                    "max": 0.99,
                    "step": 0.01,
                    "display": "slider"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("thru", "high_frequency", "low_frequency")
    FUNCTION = "separate"
    CATEGORY = "MachinePaintingNodes/Filter"

    def separate(self, original, low_frequency, mode, epsilon=0.1):
        orig = original.detach().clone()
        low = low_frequency.detach().clone()

        if mode == "subtract":
            # Photoshop Linear Light style: center at 0.5 (mid-gray = no detail)
            high = orig - low + 0.5
        else:
            # Divide mode: ratio-based, epsilon prevents division by zero
            high = ((orig + epsilon) / (low + epsilon)) * 0.5

        high = torch.clamp(high, 0.0, 1.0)

        return (original, high, low_frequency)


class FrequencyCombine:
    """
    Recombines high and low frequency layers back into a final image.
    Use the same mode that was used for separation.

    Subtract mode: result = low + high - 0.5
    Divide mode: result = (high * 2) * (low + eps) - eps
    """

    MODES = ["subtract", "divide"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "high_frequency": ("IMAGE",),
                "low_frequency": ("IMAGE",),
                "mode": (cls.MODES, {"default": "subtract"}),
            },
            "optional": {
                "epsilon": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.001,
                    "max": 0.99,
                    "step": 0.01,
                    "display": "slider"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "combine"
    CATEGORY = "MachinePaintingNodes/Filter"

    def combine(self, high_frequency, low_frequency, mode, epsilon=0.1):
        low = low_frequency.detach().clone()

        if mode == "subtract":
            result = low + high_frequency - 0.5
        else:
            result = (high_frequency * 2.0) * (low + epsilon) - epsilon

        result = torch.clamp(result, 0.0, 1.0)

        return (result,)
