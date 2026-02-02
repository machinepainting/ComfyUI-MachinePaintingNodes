import torch
import numpy as np
import cv2

class SelectiveColorPro:
    """
    Photoshop-style selective color adjustment.
    Adjust cyan, magenta, yellow, black for specific color ranges.
    Uses smooth falloff for natural-looking color adjustments.
    """
    
    COLOR_RANGES = ["reds", "yellows", "greens", "cyans", "blues", "magentas", "whites", "neutrals", "blacks"]
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "target_color": (cls.COLOR_RANGES, {"default": "reds"}),
                "cyan": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                "magenta": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                "yellow": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                "black": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
            },
            "optional": {
                "mask": ("MASK",),
                "invert_mask": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_selective_color"
    CATEGORY = "MachinePaintingNodes"

    def get_color_mask(self, img_rgb, target_color):
        """
        Create a smooth mask for the target color range.
        Uses RGB-based color detection with smooth falloff like Photoshop.
        """
        r, g, b = img_rgb[:,:,0], img_rgb[:,:,1], img_rgb[:,:,2]
        
        # Calculate color components
        max_rgb = np.maximum(np.maximum(r, g), b)
        min_rgb = np.minimum(np.minimum(r, g), b)
        chroma = max_rgb - min_rgb + 1e-10
        
        # Saturation (0-1)
        saturation = np.where(max_rgb > 0, chroma / (max_rgb + 1e-10), 0)
        
        # Lightness (0-1)
        lightness = (max_rgb + min_rgb) / 2
        
        if target_color == "reds":
            # Red dominance with smooth falloff
            red_strength = (r - np.maximum(g, b)) / (chroma + 1e-10)
            red_strength = np.clip(red_strength, 0, 1)
            # Also catch magentas and oranges that lean red
            mask = red_strength * saturation
            
        elif target_color == "yellows":
            # Yellow = high red AND green, low blue
            yellow_strength = (np.minimum(r, g) - b) / (chroma + 1e-10)
            yellow_strength = np.clip(yellow_strength, 0, 1)
            mask = yellow_strength * saturation
            
        elif target_color == "greens":
            # Green dominance
            green_strength = (g - np.maximum(r, b)) / (chroma + 1e-10)
            green_strength = np.clip(green_strength, 0, 1)
            mask = green_strength * saturation
            
        elif target_color == "cyans":
            # Cyan = high green AND blue, low red
            cyan_strength = (np.minimum(g, b) - r) / (chroma + 1e-10)
            cyan_strength = np.clip(cyan_strength, 0, 1)
            mask = cyan_strength * saturation
            
        elif target_color == "blues":
            # Blue dominance
            blue_strength = (b - np.maximum(r, g)) / (chroma + 1e-10)
            blue_strength = np.clip(blue_strength, 0, 1)
            mask = blue_strength * saturation
            
        elif target_color == "magentas":
            # Magenta = high red AND blue, low green
            magenta_strength = (np.minimum(r, b) - g) / (chroma + 1e-10)
            magenta_strength = np.clip(magenta_strength, 0, 1)
            mask = magenta_strength * saturation
            
        elif target_color == "whites":
            # High lightness, low saturation
            white_strength = np.clip((lightness - 0.7) / 0.3, 0, 1)
            sat_falloff = np.clip(1 - saturation * 3, 0, 1)
            mask = white_strength * sat_falloff
            
        elif target_color == "blacks":
            # Low lightness with smooth falloff
            black_strength = np.clip((0.3 - lightness) / 0.3, 0, 1)
            mask = black_strength
            
        else:  # neutrals
            # Low saturation, mid lightness
            neutral_sat = np.clip(1 - saturation * 4, 0, 1)
            neutral_light = 1 - np.abs(lightness - 0.5) * 2
            neutral_light = np.clip(neutral_light, 0, 1)
            mask = neutral_sat * neutral_light
        
        # Smooth the mask slightly to avoid any harsh edges
        mask = cv2.GaussianBlur(mask.astype(np.float32), (3, 3), 0)
        
        return mask

    def apply_cmyk_adjustment(self, img, color_mask, cyan, magenta, yellow, black):
        """
        Apply CMYK adjustments to masked areas.
        Photoshop-style: adjustments are relative to the current color values.
        """
        result = img.copy()
        
        # Convert adjustments to factors (-1 to 1)
        c_adj = cyan / 100.0
        m_adj = magenta / 100.0
        y_adj = yellow / 100.0
        k_adj = black / 100.0
        
        # Expand mask to 3 channels
        mask = color_mask[:, :, np.newaxis]
        
        # CMYK to RGB relationship:
        # Cyan reduces Red
        # Magenta reduces Green  
        # Yellow reduces Blue
        # Black reduces all (lightness)
        
        # Apply adjustments proportionally to mask and current pixel values
        # Positive cyan = reduce red, Negative cyan = add red
        if c_adj != 0:
            adjustment = c_adj * mask * result[:,:,0:1]
            result[:,:,0:1] = result[:,:,0:1] - adjustment
            
        if m_adj != 0:
            adjustment = m_adj * mask * result[:,:,1:2]
            result[:,:,1:2] = result[:,:,1:2] - adjustment
            
        if y_adj != 0:
            adjustment = y_adj * mask * result[:,:,2:3]
            result[:,:,2:3] = result[:,:,2:3] - adjustment
        
        # Black adjustment affects luminosity
        if k_adj != 0:
            # Positive black = darken, negative = lighten
            if k_adj > 0:
                # Darken: multiply by (1 - k_adj * mask)
                darkness = k_adj * mask
                result = result * (1 - darkness)
            else:
                # Lighten: move toward white
                lightness = -k_adj * mask
                result = result + (1 - result) * lightness
        
        return np.clip(result, 0, 1)

    def apply_selective_color(self, image, target_color, cyan, magenta, yellow, black, 
                               mask=None, invert_mask=False):
        
        img = image[0].cpu().numpy().astype(np.float32)
        original = img.copy()
        
        # Get smooth color mask
        color_mask = self.get_color_mask(img, target_color)
        
        # Apply CMYK adjustments
        result = self.apply_cmyk_adjustment(img, color_mask, cyan, magenta, yellow, black)
        
        # Apply external mask if provided
        if mask is not None:
            if len(mask.shape) == 3:
                mask_np = mask[0].cpu().numpy()
            else:
                mask_np = mask.cpu().numpy()
            
            if mask_np.shape[:2] != img.shape[:2]:
                mask_np = cv2.resize(mask_np, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
            
            if invert_mask:
                mask_np = 1.0 - mask_np
            
            mask_3ch = mask_np[:, :, np.newaxis]
            result = original * (1 - mask_3ch) + result * mask_3ch
        
        result = np.clip(result, 0, 1)
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        
        return (result_tensor,)
