import torch
import numpy as np
import cv2

class ColorAdjustBlend:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "r_shadows": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
                "g_shadows": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
                "b_shadows": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
                "r_midtones": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
                "g_midtones": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
                "b_midtones": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
                "r_highlights": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
                "g_highlights": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
                "b_highlights": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0}),
            },
            "optional": {
                # NEW TOGGLE - CONTROLS COLOR INPUT!
                "enable_color_overlay": ("BOOLEAN", {"default": False}),
                "color_input": ("IMAGE",),
                "color_blend_mode": ([
                    "normal", "overlay", "multiply", "screen", "soft_light", 
                    "hard_light", "linear_light", "difference", "color", "luminosity",
                    "darken", "lighten", "color_dodge", "color_burn", "exclusion"
                ], {"default": "overlay"}),
                "color_input_opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_color_adjust_blend"
    CATEGORY = "Color"

    def apply_color_adjust_blend(self, image, 
                               r_shadows=0.0, g_shadows=0.0, b_shadows=0.0,
                               r_midtones=0.0, g_midtones=0.0, b_midtones=0.0,
                               r_highlights=0.0, g_highlights=0.0, b_highlights=0.0,
                               enable_color_overlay=False, color_input=None, 
                               color_blend_mode="overlay", color_input_opacity=1.0):
        
        img = (image[0].cpu().numpy() * 255).astype(np.uint8)
        h, w = img.shape[:2]
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # STEP 1: ALWAYS APPLY RGB ADJUSTMENTS
        img_bgr = self.photoshop_color_balance(img_bgr, 
                                             r_shadows, g_shadows, b_shadows,
                                             r_midtones, g_midtones, b_midtones,
                                             r_highlights, g_highlights, b_highlights)

        # STEP 2: APPLY COLOR OVERLAY ONLY IF TOGGLE IS ON
        if enable_color_overlay and color_input is not None and color_input_opacity > 0:
            color = (color_input[0].cpu().numpy() * 255).astype(np.uint8)
            color_bgr = cv2.resize(cv2.cvtColor(color, cv2.COLOR_RGB2BGR), (w, h))
            img_bgr = self.apply_blend_mode(img_bgr, color_bgr, color_blend_mode, color_input_opacity)

        result_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        result_tensor = torch.from_numpy(result_rgb).float() / 255.0
        result_tensor = result_tensor.unsqueeze(0)
        return (result_tensor,)

    def photoshop_color_balance(self, bgr, r_shadows, g_shadows, b_shadows,
                              r_midtones, g_midtones, b_midtones,
                              r_highlights, g_highlights, b_highlights):
        b, g, r = cv2.split(bgr)
        b_f = b.astype(np.float32) / 255.0
        g_f = g.astype(np.float32) / 255.0
        r_f = r.astype(np.float32) / 255.0
        
        luminance = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f
        
        shadows_weight = np.clip((0.3 - luminance) / 0.3, 0, 1) ** 2
        midtones_weight = np.clip(1 - np.abs(luminance - 0.5) * 2, 0, 1)
        highlights_weight = np.clip((luminance - 0.6) / 0.4, 0, 1) ** 0.5
        
        def apply_adjustment(channel, shadows_adj, midtones_adj, highlights_adj):
            shadows_mult = 1.0 + (shadows_adj / 100.0)
            midtones_mult = 1.0 + (midtones_adj / 100.0)
            highlights_mult = 1.0 + (highlights_adj / 100.0)
            
            adjusted = channel * (
                shadows_weight * shadows_mult + 
                midtones_weight * midtones_mult + 
                highlights_weight * highlights_mult +
                (1.0 - shadows_weight - midtones_weight - highlights_weight)
            )
            return np.clip(adjusted, 0, 1)
        
        r_f = apply_adjustment(r_f, r_shadows, r_midtones, r_highlights)
        g_f = apply_adjustment(g_f, g_shadows, g_midtones, g_highlights)
        b_f = apply_adjustment(b_f, b_shadows, b_midtones, b_highlights)
        
        result_bgr = cv2.merge([
            (b_f * 255).astype(np.uint8),
            (g_f * 255).astype(np.uint8),
            (r_f * 255).astype(np.uint8)
        ])
        return result_bgr

    def apply_blend_mode(self, bottom, top, mode, opacity):
        bottom_f = bottom.astype(np.float32) / 255.0
        top_f = top.astype(np.float32) / 255.0
        
        if mode == "normal": result = top_f
        elif mode == "overlay":
            screen = 1 - (1 - bottom_f) * (1 - top_f)
            multiply = bottom_f * top_f
            result = np.where(bottom_f < 0.5, 2 * screen * bottom_f, 2 * multiply)
        elif mode == "multiply": result = bottom_f * top_f
        elif mode == "screen": result = 1 - (1 - bottom_f) * (1 - top_f)
        elif mode == "soft_light": result = (1 - 2 * top_f) * (bottom_f**2) + 2 * top_f * bottom_f
        elif mode == "hard_light": result = np.where(top_f < 0.5, 2 * bottom_f * top_f, 1 - 2 * (1 - bottom_f) * (1 - top_f))
        elif mode == "linear_light": result = np.clip(bottom_f + 2 * top_f - 1, 0, 1)
        elif mode == "difference": result = np.abs(bottom_f - top_f)
        elif mode == "color": result = self.blend_color(bottom_f, top_f)
        elif mode == "luminosity": result = self.blend_luminosity(bottom_f, top_f)
        elif mode == "darken": result = np.minimum(bottom_f, top_f)
        elif mode == "lighten": result = np.maximum(bottom_f, top_f)
        elif mode == "color_dodge": result = np.where(top_f == 0, 0, np.minimum(bottom_f / (1 - top_f), 1))
        elif mode == "color_burn": result = np.where(top_f == 1, 1, np.maximum(1 - ((1 - bottom_f) / top_f), 0))
        elif mode == "exclusion": result = bottom_f + top_f - 2 * bottom_f * top_f
        else: result = bottom_f
        
        result = bottom_f * (1 - opacity) + result * opacity
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