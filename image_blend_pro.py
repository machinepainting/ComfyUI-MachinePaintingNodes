# image_blend_pro.py
import torch
import numpy as np
import cv2

class ImageBlendPro:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "blend_amount": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "blend_mode": ([
                    "normal", "overlay", "multiply", "screen", "soft_light", 
                    "hard_light", "linear_light", "difference", "color", "luminosity",
                    "darken", "lighten", "color_dodge", "color_burn", "exclusion"
                ], {"default": "normal"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "blend_images"
    CATEGORY = "Image"

    def blend_images(self, image1, image2, blend_amount, blend_mode):
        img1 = (image1[0].cpu().numpy() * 255).astype(np.uint8)
        img2 = (image2[0].cpu().numpy() * 255).astype(np.uint8)
        
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        # Resize to match
        if (h1, w1) != (h2, w2):
            img2 = cv2.resize(img2, (w1, h1))
        
        img1_bgr = cv2.cvtColor(img1, cv2.COLOR_RGB2BGR)
        img2_bgr = cv2.cvtColor(img2, cv2.COLOR_RGB2BGR)
        
        result_bgr = self.apply_blend_mode(img1_bgr, img2_bgr, blend_mode, blend_amount)
        
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        result_tensor = torch.from_numpy(result_rgb).float() / 255.0
        result_tensor = result_tensor.unsqueeze(0)
        
        return (result_tensor,)

    def apply_blend_mode(self, bottom, top, mode, opacity):
        bottom_f = bottom.astype(np.float32) / 255.0
        top_f = top.astype(np.float32) / 255.0
        
        if mode == "normal":
            result = top_f * opacity + bottom_f * (1 - opacity)
        elif mode == "overlay":
            screen = 1 - (1 - bottom_f) * (1 - top_f)
            multiply = bottom_f * top_f
            result = np.where(bottom_f < 0.5, 2 * screen * bottom_f, 2 * multiply)
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "multiply":
            result = bottom_f * top_f
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "screen":
            result = 1 - (1 - bottom_f) * (1 - top_f)
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "soft_light":
            result = (1 - 2 * top_f) * (bottom_f**2) + 2 * top_f * bottom_f
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "hard_light":
            result = np.where(top_f < 0.5, 2 * bottom_f * top_f, 1 - 2 * (1 - bottom_f) * (1 - top_f))
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "linear_light":
            result = np.clip(bottom_f + 2 * top_f - 1, 0, 1)
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "difference":
            result = np.abs(bottom_f - top_f)
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "color":
            result = self.blend_color(bottom_f, top_f)
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "luminosity":
            result = self.blend_luminosity(bottom_f, top_f)
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "darken":
            result = np.minimum(bottom_f, top_f)
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "lighten":
            result = np.maximum(bottom_f, top_f)
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "color_dodge":
            result = np.where(top_f == 0, 0, np.minimum(bottom_f / (1 - top_f), 1))
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "color_burn":
            result = np.where(top_f == 1, 1, np.maximum(1 - ((1 - bottom_f) / top_f), 0))
            result = bottom_f * (1 - opacity) + result * opacity
        elif mode == "exclusion":
            result = bottom_f + top_f - 2 * bottom_f * top_f
            result = bottom_f * (1 - opacity) + result * opacity
        else:
            result = top_f * opacity + bottom_f * (1 - opacity)
        
        return (np.clip(result, 0, 1) * 255).astype(np.uint8)

    def blend_color(self, bottom, top):
        bottom_uint8 = (bottom * 255).astype(np.uint8)
        top_uint8 = (top * 255).astype(np.uint8)
        hsv_bottom = cv2.cvtColor(bottom_uint8, cv2.COLOR_RGB2HSV)
        hsv_top = cv2.cvtColor(top_uint8, cv2.COLOR_RGB2HSV)
        hsv_result = hsv_top.copy()
        hsv_result[:, :, 2] = hsv_bottom[:, :, 2]
        rgb_result = cv2.cvtColor(hsv_result, cv2.COLOR_HSV2RGB)
        return rgb_result.astype(np.float32) / 255.0

    def blend_luminosity(self, bottom, top):
        bottom_uint8 = (bottom * 255).astype(np.uint8)
        top_uint8 = (top * 255).astype(np.uint8)
        hsv_bottom = cv2.cvtColor(bottom_uint8, cv2.COLOR_RGB2HSV)
        hsv_top = cv2.cvtColor(top_uint8, cv2.COLOR_RGB2HSV)
        hsv_result = hsv_bottom.copy()
        hsv_result[:, :, 2] = hsv_top[:, :, 2]
        rgb_result = cv2.cvtColor(hsv_result, cv2.COLOR_HSV2RGB)
        return rgb_result.astype(np.float32) / 255.0
