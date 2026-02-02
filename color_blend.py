import torch
import numpy as np
import cv2

class ColorMatchBlend:
    """
    Match colors from a reference image to a target image with blending options.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "target": ("IMAGE",),
                "reference": ("IMAGE",),
            },
            "optional": {
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05, "display": "slider"}),
                "color_space": (["lab", "rgb", "hsv"], {"default": "lab"}),
                "match_mean": ("BOOLEAN", {"default": True}),
                "match_std": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "match_colors"
    CATEGORY = "MachinePaintingNodes"

    def match_colors(self, target, reference, strength=1.0, color_space="lab", 
                     match_mean=True, match_std=True):
        target_img = target[0].cpu().numpy()
        ref_img = reference[0].cpu().numpy()
        
        original = target_img.copy()
        
        # Convert to uint8 for color space conversion
        target_uint8 = (target_img * 255).astype(np.uint8)
        ref_uint8 = (ref_img * 255).astype(np.uint8)
        
        # Resize reference if needed
        if ref_uint8.shape[:2] != target_uint8.shape[:2]:
            ref_uint8 = cv2.resize(ref_uint8, (target_uint8.shape[1], target_uint8.shape[0]))
        
        if color_space == "lab":
            target_cvt = cv2.cvtColor(target_uint8, cv2.COLOR_RGB2LAB).astype(np.float32)
            ref_cvt = cv2.cvtColor(ref_uint8, cv2.COLOR_RGB2LAB).astype(np.float32)
        elif color_space == "hsv":
            target_cvt = cv2.cvtColor(target_uint8, cv2.COLOR_RGB2HSV).astype(np.float32)
            ref_cvt = cv2.cvtColor(ref_uint8, cv2.COLOR_RGB2HSV).astype(np.float32)
        else:
            target_cvt = target_uint8.astype(np.float32)
            ref_cvt = ref_uint8.astype(np.float32)
        
        result = target_cvt.copy()
        
        for c in range(3):
            target_mean = target_cvt[:, :, c].mean()
            target_std = target_cvt[:, :, c].std() + 1e-6
            ref_mean = ref_cvt[:, :, c].mean()
            ref_std = ref_cvt[:, :, c].std() + 1e-6
            
            channel = target_cvt[:, :, c]
            
            if match_std:
                channel = (channel - target_mean) * (ref_std / target_std)
            else:
                channel = channel - target_mean
            
            if match_mean:
                channel = channel + ref_mean
            else:
                channel = channel + target_mean
            
            result[:, :, c] = channel
        
        # Convert back
        if color_space == "lab":
            result = np.clip(result, 0, 255).astype(np.uint8)
            result = cv2.cvtColor(result, cv2.COLOR_LAB2RGB)
        elif color_space == "hsv":
            result[:, :, 0] = np.clip(result[:, :, 0], 0, 179)
            result[:, :, 1:] = np.clip(result[:, :, 1:], 0, 255)
            result = result.astype(np.uint8)
            result = cv2.cvtColor(result, cv2.COLOR_HSV2RGB)
        else:
            result = np.clip(result, 0, 255).astype(np.uint8)
        
        result = result.astype(np.float32) / 255.0
        
        # Blend with original
        result = original * (1 - strength) + result * strength
        result = np.clip(result, 0, 1)
        
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        return (result_tensor,)


class ColorAdjustBlend:
    """
    HSL adjustments with shadow/midtone/highlight zone controls.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Global adjustments
                "hue": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0, "display": "slider"}),
                "saturation": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                "lightness": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                # Zone controls
                "shadows_hue": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0, "display": "slider"}),
                "shadows_sat": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                "midtones_hue": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0, "display": "slider"}),
                "midtones_sat": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                "highlights_hue": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0, "display": "slider"}),
                "highlights_sat": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                # Blend
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05, "display": "slider"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "adjust_color"
    CATEGORY = "MachinePaintingNodes"

    def adjust_color(self, image, hue=0.0, saturation=0.0, lightness=0.0,
                     shadows_hue=0.0, shadows_sat=0.0,
                     midtones_hue=0.0, midtones_sat=0.0,
                     highlights_hue=0.0, highlights_sat=0.0,
                     strength=1.0):
        
        img = image[0].cpu().numpy()
        original = img.copy()
        
        img_uint8 = (img * 255).astype(np.uint8)
        hsv = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # Calculate luminance for zone masks
        lum = 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]
        
        # Create smooth zone masks using cosine interpolation
        shadows_mask = np.clip(1.0 - (lum / 0.33), 0, 1) ** 0.5
        highlights_mask = np.clip((lum - 0.67) / 0.33, 0, 1) ** 0.5
        midtones_mask = 1.0 - shadows_mask - highlights_mask
        midtones_mask = np.clip(midtones_mask, 0, 1)
        
        # Apply global adjustments
        hsv[:, :, 0] = (hsv[:, :, 0] + hue / 2.0) % 180
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + saturation / 100.0), 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + lightness / 100.0), 0, 255)
        
        # Apply zone adjustments
        hsv[:, :, 0] = (hsv[:, :, 0] + shadows_hue / 2.0 * shadows_mask) % 180
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + shadows_sat / 100.0 * shadows_mask), 0, 255)
        
        hsv[:, :, 0] = (hsv[:, :, 0] + midtones_hue / 2.0 * midtones_mask) % 180
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + midtones_sat / 100.0 * midtones_mask), 0, 255)
        
        hsv[:, :, 0] = (hsv[:, :, 0] + highlights_hue / 2.0 * highlights_mask) % 180
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + highlights_sat / 100.0 * highlights_mask), 0, 255)
        
        # Convert back
        hsv = hsv.astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0
        
        # Blend with original
        result = original * (1 - strength) + result * strength
        result = np.clip(result, 0, 1)
        
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        return (result_tensor,)
