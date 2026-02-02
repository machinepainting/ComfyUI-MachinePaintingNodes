import torch
import numpy as np
import cv2

class SelectiveColorPro:
    """
    Photoshop-style selective color adjustment.
    Adjust cyan, magenta, yellow, black for specific color ranges.
    Connect to Live Adjust Preview node to see changes in real-time.
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

    def get_color_mask(self, img_hsv, target_color):
        """Create a mask for the target color range."""
        h, s, v = img_hsv[:,:,0], img_hsv[:,:,1], img_hsv[:,:,2]
        
        if target_color == "reds":
            mask = ((h <= 15) | (h >= 165)) & (s > 25)
        elif target_color == "yellows":
            mask = (h >= 15) & (h <= 45) & (s > 25)
        elif target_color == "greens":
            mask = (h >= 45) & (h <= 75) & (s > 25)
        elif target_color == "cyans":
            mask = (h >= 75) & (h <= 105) & (s > 25)
        elif target_color == "blues":
            mask = (h >= 105) & (h <= 135) & (s > 25)
        elif target_color == "magentas":
            mask = (h >= 135) & (h <= 165) & (s > 25)
        elif target_color == "whites":
            mask = (v >= 200) & (s <= 30)
        elif target_color == "blacks":
            mask = (v <= 55)
        else:  # neutrals
            mask = (s <= 25) & (v > 55) & (v < 200)
        
        mask_float = mask.astype(np.float32)
        mask_float = cv2.GaussianBlur(mask_float, (5, 5), 0)
        
        return mask_float

    def apply_cmyk_adjustment(self, img, color_mask, cyan, magenta, yellow, black):
        """Apply CMYK adjustments to masked areas."""
        result = img.copy()
        
        c_adj = cyan / 100.0
        m_adj = magenta / 100.0
        y_adj = yellow / 100.0
        k_adj = black / 100.0
        
        mask_3ch = np.stack([color_mask, color_mask, color_mask], axis=2)
        
        # Cyan affects Red (inverse)
        result[:,:,0] = result[:,:,0] - (c_adj * mask_3ch[:,:,0] * result[:,:,0])
        # Magenta affects Green (inverse)
        result[:,:,1] = result[:,:,1] - (m_adj * mask_3ch[:,:,1] * result[:,:,1])
        # Yellow affects Blue (inverse)
        result[:,:,2] = result[:,:,2] - (y_adj * mask_3ch[:,:,2] * result[:,:,2])
        
        # Black affects all channels
        if k_adj != 0:
            darkness = k_adj * mask_3ch
            result = result * (1 - darkness * 0.5)
        
        return np.clip(result, 0, 1)

    def apply_selective_color(self, image, target_color, cyan, magenta, yellow, black, 
                               mask=None, invert_mask=False):
        
        img = image[0].cpu().numpy().astype(np.float32)
        original = img.copy()
        
        img_uint8 = (img * 255).astype(np.uint8)
        img_hsv = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2HSV)
        
        color_mask = self.get_color_mask(img_hsv, target_color)
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
            
            mask_3ch = np.stack([mask_np, mask_np, mask_np], axis=2)
            result = original * (1 - mask_3ch) + result * mask_3ch
        
        result = np.clip(result, 0, 1)
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        
        return (result_tensor,)
