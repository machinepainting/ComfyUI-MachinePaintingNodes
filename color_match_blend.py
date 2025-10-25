import torch
import numpy as np
import cv2

class ColorMatchBlend:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "target_image": ("IMAGE",),
                "reference_image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),
                "enable_match_blend": ("BOOLEAN", {"default": True}),
                "saturation": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_color_match_blend"
    CATEGORY = "Image / Color"

    def apply_color_match_blend(self, target_image, reference_image, strength, enable_match_blend, saturation):
        target = (target_image[0].cpu().numpy() * 255).astype(np.uint8)
        h, w = target.shape[:2]
        target_bgr = cv2.cvtColor(target, cv2.COLOR_RGB2BGR)

        if enable_match_blend:
            reference = (reference_image[0].cpu().numpy() * 255).astype(np.uint8)
            reference_bgr = cv2.resize(cv2.cvtColor(reference, cv2.COLOR_RGB2BGR), (w, h))
            
            target_hsv = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2HSV)
            reference_hsv = cv2.cvtColor(reference_bgr, cv2.COLOR_BGR2HSV)
            
            result_hsv = target_hsv.copy()
            result_hsv[:, :, 0] = reference_hsv[:, :, 0]
            result_hsv[:, :, 1] = reference_hsv[:, :, 1]
            result_hsv[:, :, 2] = target_hsv[:, :, 2]
            
            result_bgr = cv2.cvtColor(result_hsv, cv2.COLOR_HSV2BGR)
            result = cv2.addWeighted(target_bgr, 1 - strength, result_bgr, strength, 0)
        else:
            result = target_bgr

        result = self.apply_saturation(result, saturation)
        
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        result_tensor = torch.from_numpy(result_rgb).float() / 255.0
        result_tensor = result_tensor.unsqueeze(0)
        return (result_tensor,)

    def apply_saturation(self, bgr, saturation):
        if saturation == 0:
            return bgr
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + saturation / 100.0), 0, 255)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)