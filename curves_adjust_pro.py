import torch
import numpy as np
import json
import cv2

class CurvesAdjustPro:
    """
    Photoshop-style curves adjustment with interactive curve editor.
    Click to add points, drag to adjust, shift+click to remove points.
    Supports mask input to limit effect to specific areas.
    """
    
    # Color presets - all have endpoint anchors [[0,0],[1,1]]
    PRESETS = {
        "none": {"rgb": [[0,0],[1,1]], "red": [[0,0],[1,1]], "green": [[0,0],[1,1]], "blue": [[0,0],[1,1]]},
        "auto_enhance": {
            "rgb": [[0, 0], [0.25, 0.22], [0.5, 0.5], [0.75, 0.78], [1, 1]],
            "red": [[0,0],[1,1]], "green": [[0,0],[1,1]], "blue": [[0,0],[1,1]]
        },
        "high_contrast": {
            "rgb": [[0, 0], [0.25, 0.15], [0.5, 0.5], [0.75, 0.85], [1, 1]],
            "red": [[0,0],[1,1]], "green": [[0,0],[1,1]], "blue": [[0,0],[1,1]]
        },
        "low_contrast": {
            "rgb": [[0, 0.1], [0.5, 0.5], [1, 0.9]],
            "red": [[0,0],[1,1]], "green": [[0,0],[1,1]], "blue": [[0,0],[1,1]]
        },
        "warm_tones": {
            "rgb": [[0,0],[1,1]],
            "red": [[0, 0], [0.5, 0.55], [1, 1]],
            "green": [[0,0],[1,1]],
            "blue": [[0, 0], [0.5, 0.45], [1, 1]]
        },
        "cool_tones": {
            "rgb": [[0,0],[1,1]],
            "red": [[0, 0], [0.5, 0.45], [1, 1]],
            "green": [[0,0],[1,1]],
            "blue": [[0, 0], [0.5, 0.55], [1, 1]]
        },
        "vintage_fade": {
            "rgb": [[0, 0.05], [1, 0.95]],
            "red": [[0, 0.02], [0.5, 0.52], [1, 1]],
            "green": [[0, 0], [0.5, 0.48], [1, 0.95]],
            "blue": [[0, 0.05], [0.5, 0.45], [1, 0.9]]
        },
        "cinematic": {
            "rgb": [[0, 0.03], [0.5, 0.5], [1, 0.97]],
            "red": [[0, 0], [0.5, 0.48], [1, 1]],
            "green": [[0, 0], [0.5, 0.5], [1, 0.98]],
            "blue": [[0, 0.05], [0.5, 0.52], [1, 1]]
        },
        "matte_look": {
            "rgb": [[0, 0.08], [0.25, 0.28], [0.75, 0.75], [1, 0.92]],
            "red": [[0,0],[1,1]], "green": [[0,0],[1,1]], "blue": [[0,0],[1,1]]
        },
        "cross_process": {
            "rgb": [[0,0],[1,1]],
            "red": [[0, 0.05], [0.5, 0.45], [1, 1]],
            "green": [[0, 0], [0.5, 0.55], [1, 0.95]],
            "blue": [[0, 0.1], [0.5, 0.4], [1, 0.9]]
        },
        "sepia_tone": {
            "rgb": [[0, 0], [0.5, 0.5], [1, 0.95]],
            "red": [[0, 0], [0.5, 0.55], [1, 1]],
            "green": [[0, 0], [0.5, 0.48], [1, 0.9]],
            "blue": [[0, 0], [0.5, 0.35], [1, 0.8]]
        },
        "bleach_bypass": {
            "rgb": [[0, 0], [0.2, 0.12], [0.5, 0.5], [0.8, 0.88], [1, 1]],
            "red": [[0,0],[1,1]], "green": [[0,0],[1,1]],
            "blue": [[0, 0], [0.5, 0.45], [1, 1]]
        },
        "golden_hour": {
            "rgb": [[0, 0], [0.5, 0.52], [1, 1]],
            "red": [[0, 0], [0.5, 0.55], [1, 1]],
            "green": [[0, 0], [0.5, 0.52], [1, 0.98]],
            "blue": [[0, 0], [0.5, 0.4], [1, 0.85]]
        },
        "moonlight": {
            "rgb": [[0, 0], [0.5, 0.48], [1, 0.95]],
            "red": [[0, 0], [0.5, 0.45], [1, 0.9]],
            "green": [[0, 0], [0.5, 0.5], [1, 0.95]],
            "blue": [[0, 0.05], [0.5, 0.55], [1, 1]]
        },
        "vibrant_pop": {
            "rgb": [[0, 0], [0.2, 0.15], [0.5, 0.5], [0.8, 0.85], [1, 1]],
            "red": [[0, 0], [0.5, 0.52], [1, 1]],
            "green": [[0, 0], [0.5, 0.52], [1, 1]],
            "blue": [[0, 0], [0.5, 0.52], [1, 1]]
        },
        "noir": {
            "rgb": [[0, 0], [0.15, 0.05], [0.5, 0.5], [0.85, 0.95], [1, 1]],
            "red": [[0, 0], [0.5, 0.48], [1, 1]],
            "green": [[0, 0], [0.5, 0.48], [1, 1]],
            "blue": [[0, 0], [0.5, 0.48], [1, 1]]
        },
        "sunset_glow": {
            "rgb": [[0,0],[1,1]],
            "red": [[0, 0], [0.5, 0.58], [1, 1]],
            "green": [[0, 0], [0.5, 0.48], [1, 0.95]],
            "blue": [[0, 0], [0.5, 0.38], [1, 0.8]]
        },
        "forest_green": {
            "rgb": [[0, 0.02], [0.5, 0.5], [1, 0.98]],
            "red": [[0, 0], [0.5, 0.45], [1, 0.95]],
            "green": [[0, 0], [0.5, 0.55], [1, 1]],
            "blue": [[0, 0], [0.5, 0.45], [1, 0.9]]
        }
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        preset_list = list(cls.PRESETS.keys())
        return {
            "required": {
                "image": ("IMAGE",),
                "curve_data": ("STRING", {
                    "default": '{"rgb":[[0,0],[1,1]],"red":[[0,0],[1,1]],"green":[[0,0],[1,1]],"blue":[[0,0],[1,1]]}',
                    "multiline": False,
                }),
                "preset": (preset_list, {"default": "none"}),
            },
            "optional": {
                "mask": ("MASK",),
                "invert_mask": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_curves"
    CATEGORY = "MachinePaintingNodes"

    def catmull_rom_spline(self, points, num_samples=256):
        """Create smooth curve through control points. Empty = no change."""
        if len(points) < 2:
            return np.linspace(0, 1, num_samples)
        
        points = sorted(points, key=lambda p: p[0])
        
        # Extend to endpoints
        if points[0][0] > 0.001:
            points.insert(0, [0, points[0][1]])
        if points[-1][0] < 0.999:
            points.append([1, points[-1][1]])
        
        lut = np.zeros(num_samples)
        
        for i in range(num_samples):
            x = i / (num_samples - 1)
            
            seg = 0
            for j in range(len(points) - 1):
                if points[j][0] <= x <= points[j + 1][0]:
                    seg = j
                    break
                if j == len(points) - 2:
                    seg = j
            
            p0 = points[max(0, seg - 1)]
            p1 = points[seg]
            p2 = points[min(len(points) - 1, seg + 1)]
            p3 = points[min(len(points) - 1, seg + 2)]
            
            x0, x1 = p1[0], p2[0]
            t = 0 if x1 - x0 < 0.0001 else (x - x0) / (x1 - x0)
            
            t2 = t * t
            t3 = t2 * t
            
            y = 0.5 * (
                (2 * p1[1]) +
                (-p0[1] + p2[1]) * t +
                (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            
            lut[i] = np.clip(y, 0, 1)
        
        return lut

    def apply_lut(self, channel, lut):
        indices = (channel * 255).astype(np.int32)
        indices = np.clip(indices, 0, 255)
        return lut[indices]

    def apply_curves(self, image, curve_data, preset="none", mask=None, invert_mask=False):
        # Parse curve data
        try:
            curves = json.loads(curve_data)
        except:
            curves = {"rgb": [], "red": [], "green": [], "blue": []}
        
        # Check if curves are all empty - if so, use preset
        all_empty = all(len(curves.get(ch, [])) == 0 for ch in ["rgb", "red", "green", "blue"])
        
        if all_empty and preset != "none":
            curves = self.PRESETS.get(preset, curves)
        
        img = image[0].cpu().numpy().astype(np.float32)
        original = img.copy()
        result = img.copy()
        
        # Apply curves
        rgb_points = curves.get("rgb", [])
        r_points = curves.get("red", [])
        g_points = curves.get("green", [])
        b_points = curves.get("blue", [])
        
        if len(rgb_points) >= 2:
            rgb_lut = self.catmull_rom_spline(rgb_points)
            for ch in range(3):
                result[:, :, ch] = self.apply_lut(result[:, :, ch], rgb_lut)
        
        if len(r_points) >= 2:
            r_lut = self.catmull_rom_spline(r_points)
            result[:, :, 0] = self.apply_lut(result[:, :, 0], r_lut)
        
        if len(g_points) >= 2:
            g_lut = self.catmull_rom_spline(g_points)
            result[:, :, 1] = self.apply_lut(result[:, :, 1], g_lut)
        
        if len(b_points) >= 2:
            b_lut = self.catmull_rom_spline(b_points)
            result[:, :, 2] = self.apply_lut(result[:, :, 2], b_lut)
        
        result = np.clip(result, 0, 1)
        
        # Apply mask if provided
        if mask is not None:
            # Get mask as numpy
            if len(mask.shape) == 3:
                mask_np = mask[0].cpu().numpy()
            else:
                mask_np = mask.cpu().numpy()
            
            # Resize mask if needed
            if mask_np.shape[:2] != img.shape[:2]:
                mask_np = cv2.resize(mask_np, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
            
            # Invert if requested
            if invert_mask:
                mask_np = 1.0 - mask_np
            
            # Blend original and result using mask
            mask_3ch = np.stack([mask_np, mask_np, mask_np], axis=2)
            result = original * (1 - mask_3ch) + result * mask_3ch
        
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        
        return (result_tensor,)
