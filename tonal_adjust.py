import torch
import numpy as np
import cv2

class LevelsAdjust:
    """
    Adjust image levels - black point, white point, gamma, and output levels.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "black_point": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.5, "step": 0.01, "display": "slider"}),
                "white_point": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 1.0, "step": 0.01, "display": "slider"}),
                "gamma": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.05, "display": "slider"}),
                "output_black": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.5, "step": 0.01, "display": "slider"}),
                "output_white": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 1.0, "step": 0.01, "display": "slider"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "adjust_levels"
    CATEGORY = "MachinePaintingNodes"

    def adjust_levels(self, image, black_point=0.0, white_point=1.0, gamma=1.0, 
                      output_black=0.0, output_white=1.0):
        img = image[0].cpu().numpy().astype(np.float32)
        
        # Input levels
        result = (img - black_point) / (white_point - black_point)
        result = np.clip(result, 0, 1)
        
        # Gamma
        if gamma != 1.0:
            result = np.power(result, 1.0 / gamma)
        
        # Output levels
        result = result * (output_white - output_black) + output_black
        result = np.clip(result, 0, 1)
        
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        return (result_tensor,)


class AutoLevels:
    """
    Automatically adjust image levels based on histogram analysis.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "clip_percent": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 5.0, "step": 0.1, "display": "slider"}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05, "display": "slider"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "auto_levels"
    CATEGORY = "MachinePaintingNodes"

    def auto_levels(self, image, clip_percent=0.1, strength=1.0):
        img = image[0].cpu().numpy().astype(np.float32)
        original = img.copy()
        
        result = np.zeros_like(img)
        
        for c in range(3):
            channel = img[:, :, c]
            
            # Find clip points
            hist, bins = np.histogram(channel.flatten(), bins=256, range=(0, 1))
            total_pixels = hist.sum()
            clip_pixels = total_pixels * clip_percent / 100.0
            
            # Find black point
            cumsum = np.cumsum(hist)
            black_idx = np.searchsorted(cumsum, clip_pixels)
            black_point = black_idx / 255.0
            
            # Find white point
            cumsum_rev = np.cumsum(hist[::-1])
            white_idx = 255 - np.searchsorted(cumsum_rev, clip_pixels)
            white_point = white_idx / 255.0
            
            # Apply levels
            if white_point > black_point:
                adjusted = (channel - black_point) / (white_point - black_point)
                result[:, :, c] = np.clip(adjusted, 0, 1)
            else:
                result[:, :, c] = channel
        
        # Blend with original based on strength
        result = original * (1 - strength) + result * strength
        result = np.clip(result, 0, 1)
        
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        return (result_tensor,)


class BrightnessContrastAdjust:
    """
    Simple brightness and contrast adjustment.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "brightness": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                "contrast": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "adjust"
    CATEGORY = "MachinePaintingNodes"

    def adjust(self, image, brightness, contrast):
        img = image[0].cpu().numpy().astype(np.float32)
        
        # Brightness (-100 to 100 -> -0.5 to 0.5)
        result = img + (brightness / 200.0)
        
        # Contrast (-100 to 100 -> 0.5 to 1.5 factor)
        factor = 1.0 + (contrast / 100.0)
        result = (result - 0.5) * factor + 0.5
        
        result = np.clip(result, 0, 1)
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        
        return (result_tensor,)
