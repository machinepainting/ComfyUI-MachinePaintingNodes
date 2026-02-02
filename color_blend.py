import torch
import numpy as np
import cv2

class ColorMatchBlend:
    
    BLEND_MODES = ["normal", "overlay", "multiply", "screen", "soft_light", 
                   "hard_light", "color", "luminosity", "darken", "lighten"]
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "target_image": ("IMAGE",),
                "reference_image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.05, "display": "slider"}),
                "enable_match_blend": ("BOOLEAN", {"default": True}),
                "saturation": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
            },
            "optional": {
                "match_method": (["statistical", "histogram", "reinhard"], {
                    "default": "statistical"
                }),
                "blend_mode": (cls.BLEND_MODES, {"default": "normal"}),
                "luminance_match": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05,
                    "display": "slider"
                }),
                "color_match": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05,
                    "display": "slider"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_color_match_blend"
    CATEGORY = "MachinePaintingNodes"

    def apply_color_match_blend(self, target_image, reference_image, strength, 
                                 enable_match_blend, saturation,
                                 match_method="statistical", blend_mode="normal",
                                 luminance_match=0.0, color_match=1.0):
        
        target = (target_image[0].cpu().numpy() * 255).astype(np.uint8)
        h, w = target.shape[:2]
        target_bgr = cv2.cvtColor(target, cv2.COLOR_RGB2BGR)

        if enable_match_blend and strength > 0:
            reference = (reference_image[0].cpu().numpy() * 255).astype(np.uint8)
            reference_bgr = cv2.cvtColor(reference, cv2.COLOR_RGB2BGR)
            
            # Resize reference to match target
            if reference_bgr.shape[:2] != target_bgr.shape[:2]:
                reference_bgr = cv2.resize(reference_bgr, (w, h))
            
            if match_method == "statistical":
                matched = self.statistical_lab_match(target_bgr, reference_bgr, 
                                                     luminance_match, color_match)
            elif match_method == "histogram":
                matched = self.histogram_lab_match(target_bgr, reference_bgr,
                                                   luminance_match, color_match)
            else:  # reinhard
                matched = self.reinhard_color_transfer(target_bgr, reference_bgr,
                                                       luminance_match, color_match)
            
            # Apply blend mode
            if blend_mode != "normal":
                matched = self.apply_blend_mode(target_bgr, matched, blend_mode)
            
            result = cv2.addWeighted(target_bgr, 1 - strength, matched, strength, 0)
        else:
            result = target_bgr

        result = self.apply_saturation(result, saturation)
        
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        result_tensor = torch.from_numpy(result_rgb).float() / 255.0
        result_tensor = result_tensor.unsqueeze(0)
        return (result_tensor,)

    def apply_blend_mode(self, bottom, top, mode):
        bottom_f = bottom.astype(np.float32) / 255.0
        top_f = top.astype(np.float32) / 255.0
        
        if mode == "multiply":
            result = bottom_f * top_f
        elif mode == "screen":
            result = 1 - (1 - bottom_f) * (1 - top_f)
        elif mode == "overlay":
            result = np.where(bottom_f < 0.5, 
                            2 * bottom_f * top_f, 
                            1 - 2 * (1 - bottom_f) * (1 - top_f))
        elif mode == "soft_light":
            result = (1 - 2 * top_f) * (bottom_f ** 2) + 2 * top_f * bottom_f
        elif mode == "hard_light":
            result = np.where(top_f < 0.5,
                            2 * bottom_f * top_f,
                            1 - 2 * (1 - bottom_f) * (1 - top_f))
        elif mode == "color":
            result = self.blend_color(bottom_f, top_f)
        elif mode == "luminosity":
            result = self.blend_luminosity(bottom_f, top_f)
        elif mode == "darken":
            result = np.minimum(bottom_f, top_f)
        elif mode == "lighten":
            result = np.maximum(bottom_f, top_f)
        else:
            result = top_f
        
        return (np.clip(result, 0, 1) * 255).astype(np.uint8)

    def blend_color(self, bottom, top):
        # Keep luminosity of bottom, hue/sat of top
        bottom_uint8 = (bottom * 255).astype(np.uint8)
        top_uint8 = (top * 255).astype(np.uint8)
        hsv_bottom = cv2.cvtColor(bottom_uint8, cv2.COLOR_BGR2HSV)
        hsv_top = cv2.cvtColor(top_uint8, cv2.COLOR_BGR2HSV)
        hsv_result = hsv_top.copy()
        hsv_result[:, :, 2] = hsv_bottom[:, :, 2]
        result = cv2.cvtColor(hsv_result, cv2.COLOR_HSV2BGR)
        return result.astype(np.float32) / 255.0

    def blend_luminosity(self, bottom, top):
        # Keep hue/sat of bottom, luminosity of top
        bottom_uint8 = (bottom * 255).astype(np.uint8)
        top_uint8 = (top * 255).astype(np.uint8)
        hsv_bottom = cv2.cvtColor(bottom_uint8, cv2.COLOR_BGR2HSV)
        hsv_top = cv2.cvtColor(top_uint8, cv2.COLOR_BGR2HSV)
        hsv_result = hsv_bottom.copy()
        hsv_result[:, :, 2] = hsv_top[:, :, 2]
        result = cv2.cvtColor(hsv_result, cv2.COLOR_HSV2BGR)
        return result.astype(np.float32) / 255.0

    def statistical_lab_match(self, target_bgr, reference_bgr, lum_strength, color_strength):
        """
        Statistical color matching in LAB space.
        Transfers mean and std of color channels without creating artifacts.
        """
        target_lab = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        ref_lab = cv2.cvtColor(reference_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        result_lab = target_lab.copy()
        
        for i in range(3):
            strength = lum_strength if i == 0 else color_strength
            if strength <= 0:
                continue
                
            t_mean = target_lab[:,:,i].mean()
            t_std = max(target_lab[:,:,i].std(), 1.0)
            r_mean = ref_lab[:,:,i].mean()
            r_std = max(ref_lab[:,:,i].std(), 1.0)
            
            # Normalize, scale, and shift
            normalized = (target_lab[:,:,i] - t_mean) / t_std
            
            # Blend the statistics based on strength
            new_std = t_std + strength * (r_std - t_std)
            new_mean = t_mean + strength * (r_mean - t_mean)
            
            # Limit std ratio to prevent extreme changes
            new_std = np.clip(new_std, t_std * 0.5, t_std * 2.0)
            
            result_lab[:,:,i] = normalized * new_std + new_mean
        
        result_lab[:,:,0] = np.clip(result_lab[:,:,0], 0, 255)
        result_lab[:,:,1] = np.clip(result_lab[:,:,1], 0, 255)
        result_lab[:,:,2] = np.clip(result_lab[:,:,2], 0, 255)
        
        return cv2.cvtColor(result_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

    def gaussian_smooth_1d(self, data, sigma=1.0):
        """Simple 1D gaussian smoothing without scipy."""
        kernel_size = int(sigma * 6) | 1  # Ensure odd
        kernel_size = max(3, kernel_size)
        x = np.arange(kernel_size) - kernel_size // 2
        kernel = np.exp(-0.5 * (x / sigma) ** 2)
        kernel = kernel / kernel.sum()
        
        # Pad and convolve
        padded = np.pad(data, kernel_size // 2, mode='edge')
        smoothed = np.convolve(padded, kernel, mode='valid')
        return smoothed

    def histogram_lab_match(self, target_bgr, reference_bgr, lum_strength, color_strength):
        """
        Histogram matching with smoothing to prevent banding/patchiness.
        Uses interpolated LUT and applies gaussian smoothing to avoid discrete jumps.
        """
        target_lab = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        ref_lab = cv2.cvtColor(reference_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        result_lab = target_lab.copy()
        
        for i in range(3):
            strength = lum_strength if i == 0 else color_strength
            if strength <= 0:
                continue
            
            target_channel = target_lab[:,:,i]
            ref_channel = ref_lab[:,:,i]
            
            # Compute histograms
            t_hist, _ = np.histogram(target_channel.flatten(), bins=256, range=(0, 256))
            r_hist, _ = np.histogram(ref_channel.flatten(), bins=256, range=(0, 256))
            
            # Add small epsilon to avoid zero bins causing issues
            t_hist = t_hist.astype(np.float64) + 1e-10
            r_hist = r_hist.astype(np.float64) + 1e-10
            
            # Compute CDFs
            t_cdf = np.cumsum(t_hist)
            r_cdf = np.cumsum(r_hist)
            
            # Normalize CDFs
            t_cdf = t_cdf / t_cdf[-1]
            r_cdf = r_cdf / r_cdf[-1]
            
            # Create lookup table with interpolation for smoothness
            lut = np.zeros(256, dtype=np.float32)
            for j in range(256):
                # Find where target CDF value falls in reference CDF
                idx = np.searchsorted(r_cdf, t_cdf[j])
                idx = min(idx, 255)
                
                # Linear interpolation for smoother mapping
                if idx > 0 and idx < 255:
                    t_val = t_cdf[j]
                    r_low = r_cdf[idx - 1]
                    r_high = r_cdf[idx]
                    if r_high - r_low > 1e-10:
                        frac = (t_val - r_low) / (r_high - r_low)
                        lut[j] = (idx - 1) + frac
                    else:
                        lut[j] = idx
                else:
                    lut[j] = idx
            
            # Smooth the LUT to reduce banding
            lut = self.gaussian_smooth_1d(lut, sigma=1.5)
            lut = np.clip(lut, 0, 255)
            
            # Apply the smooth lookup using interpolation
            matched = np.interp(target_channel.flatten(), 
                               np.arange(256), lut).reshape(target_channel.shape)
            
            # Blend with original
            result_lab[:,:,i] = target_channel * (1 - strength) + matched * strength
        
        result_lab[:,:,0] = np.clip(result_lab[:,:,0], 0, 255)
        result_lab[:,:,1] = np.clip(result_lab[:,:,1], 0, 255)
        result_lab[:,:,2] = np.clip(result_lab[:,:,2], 0, 255)
        
        return cv2.cvtColor(result_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

    def reinhard_color_transfer(self, target_bgr, reference_bgr, lum_strength, color_strength):
        """
        Classic Reinhard color transfer with per-channel strength control.
        """
        target_lab = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        ref_lab = cv2.cvtColor(reference_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        result_lab = target_lab.copy()
        
        for i in range(3):
            strength = lum_strength if i == 0 else color_strength
            if strength <= 0:
                continue
                
            t_mean = target_lab[:,:,i].mean()
            t_std = max(target_lab[:,:,i].std(), 1.0)
            r_mean = ref_lab[:,:,i].mean()
            r_std = max(ref_lab[:,:,i].std(), 1.0)
            
            # Classic Reinhard: normalize by target stats, scale by reference stats
            std_ratio = np.clip(r_std / t_std, 0.3, 3.0)
            
            transferred = (target_lab[:,:,i] - t_mean) * std_ratio + r_mean
            
            # Blend based on strength
            result_lab[:,:,i] = target_lab[:,:,i] * (1 - strength) + transferred * strength
        
        result_lab[:,:,0] = np.clip(result_lab[:,:,0], 0, 255)
        result_lab[:,:,1] = np.clip(result_lab[:,:,1], 0, 255)
        result_lab[:,:,2] = np.clip(result_lab[:,:,2], 0, 255)
        
        return cv2.cvtColor(result_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

    def apply_saturation(self, bgr, saturation):
        if saturation == 0:
            return bgr
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        factor = 1 + saturation / 100.0
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


class ColorAdjustBlend:
    """
    RGB color balance with shadow/midtone/highlight controls.
    Optional color reference: matches color from reference, applies via blend mode, then RGB adjustments.
    Works standalone as simple color adjust if no reference provided.
    """
    
    BLEND_MODES = ["normal", "overlay", "multiply", "screen", "soft_light", 
                   "hard_light", "color", "luminosity", "darken", "lighten"]
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Color reference (optional)
                "color_reference": ("IMAGE",),
                "reference_strength": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.05, "display": "slider"}),
                "blend_mode": (cls.BLEND_MODES, {"default": "color"}),
                # RGB adjustments (post-process)
                "r_shadows": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
                "g_shadows": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
                "b_shadows": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
                "r_midtones": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
                "g_midtones": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
                "b_midtones": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
                "r_highlights": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
                "g_highlights": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
                "b_highlights": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 5.0, "display": "slider"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_color_adjust_blend"
    CATEGORY = "MachinePaintingNodes"

    def apply_color_adjust_blend(self, image, 
                               color_reference=None, reference_strength=0.75, blend_mode="color",
                               r_shadows=0.0, g_shadows=0.0, b_shadows=0.0,
                               r_midtones=0.0, g_midtones=0.0, b_midtones=0.0,
                               r_highlights=0.0, g_highlights=0.0, b_highlights=0.0):
        
        img = (image[0].cpu().numpy() * 255).astype(np.uint8)
        h, w = img.shape[:2]
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Step 1: If color reference provided, color match then blend
        if color_reference is not None and reference_strength > 0:
            ref = (color_reference[0].cpu().numpy() * 255).astype(np.uint8)
            ref_bgr = cv2.cvtColor(ref, cv2.COLOR_RGB2BGR)
            if ref_bgr.shape[:2] != (h, w):
                ref_bgr = cv2.resize(ref_bgr, (w, h))
            
            # Color match the reference to the image (statistical LAB matching)
            matched = self.statistical_lab_match(img_bgr, ref_bgr)
            
            # Apply blend mode to the matched result
            if blend_mode != "normal":
                blended = self.apply_blend_mode(img_bgr, matched, blend_mode)
            else:
                blended = matched
            
            # Blend with original based on strength
            img_bgr = cv2.addWeighted(img_bgr, 1 - reference_strength, blended, reference_strength, 0)

        # Step 2: Apply RGB color balance adjustments (post-process)
        img_bgr = self.photoshop_color_balance(img_bgr, 
                                             r_shadows, g_shadows, b_shadows,
                                             r_midtones, g_midtones, b_midtones,
                                             r_highlights, g_highlights, b_highlights)

        result_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        result_tensor = torch.from_numpy(result_rgb).float() / 255.0
        result_tensor = result_tensor.unsqueeze(0)
        return (result_tensor,)

    def statistical_lab_match(self, target_bgr, reference_bgr):
        """Match colors from reference to target using LAB color space."""
        target_lab = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        ref_lab = cv2.cvtColor(reference_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        result_lab = target_lab.copy()
        
        for i in range(3):
            t_mean = target_lab[:,:,i].mean()
            t_std = max(target_lab[:,:,i].std(), 1.0)
            r_mean = ref_lab[:,:,i].mean()
            r_std = max(ref_lab[:,:,i].std(), 1.0)
            
            # Normalize, scale, and shift
            normalized = (target_lab[:,:,i] - t_mean) / t_std
            new_std = np.clip(r_std, t_std * 0.5, t_std * 2.0)
            result_lab[:,:,i] = normalized * new_std + r_mean
        
        result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
        return cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)

    def apply_blend_mode(self, bottom, top, mode):
        bottom_f = bottom.astype(np.float32) / 255.0
        top_f = top.astype(np.float32) / 255.0
        
        if mode == "normal":
            result = top_f
        elif mode == "multiply":
            result = bottom_f * top_f
        elif mode == "screen":
            result = 1 - (1 - bottom_f) * (1 - top_f)
        elif mode == "overlay":
            result = np.where(bottom_f < 0.5, 
                            2 * bottom_f * top_f, 
                            1 - 2 * (1 - bottom_f) * (1 - top_f))
        elif mode == "soft_light":
            result = (1 - 2 * top_f) * (bottom_f ** 2) + 2 * top_f * bottom_f
        elif mode == "hard_light":
            result = np.where(top_f < 0.5,
                            2 * bottom_f * top_f,
                            1 - 2 * (1 - bottom_f) * (1 - top_f))
        elif mode == "color":
            result = self.blend_color(bottom_f, top_f)
        elif mode == "luminosity":
            result = self.blend_luminosity(bottom_f, top_f)
        elif mode == "darken":
            result = np.minimum(bottom_f, top_f)
        elif mode == "lighten":
            result = np.maximum(bottom_f, top_f)
        else:
            result = top_f
        
        return (np.clip(result, 0, 1) * 255).astype(np.uint8)

    def blend_color(self, bottom, top):
        bottom_uint8 = (bottom * 255).astype(np.uint8)
        top_uint8 = (top * 255).astype(np.uint8)
        hsv_bottom = cv2.cvtColor(bottom_uint8, cv2.COLOR_BGR2HSV)
        hsv_top = cv2.cvtColor(top_uint8, cv2.COLOR_BGR2HSV)
        hsv_result = hsv_top.copy()
        hsv_result[:, :, 2] = hsv_bottom[:, :, 2]
        result = cv2.cvtColor(hsv_result, cv2.COLOR_HSV2BGR)
        return result.astype(np.float32) / 255.0

    def blend_luminosity(self, bottom, top):
        bottom_uint8 = (bottom * 255).astype(np.uint8)
        top_uint8 = (top * 255).astype(np.uint8)
        hsv_bottom = cv2.cvtColor(bottom_uint8, cv2.COLOR_BGR2HSV)
        hsv_top = cv2.cvtColor(top_uint8, cv2.COLOR_BGR2HSV)
        hsv_result = hsv_bottom.copy()
        hsv_result[:, :, 2] = hsv_top[:, :, 2]
        result = cv2.cvtColor(hsv_result, cv2.COLOR_HSV2BGR)
        return result.astype(np.float32) / 255.0

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
