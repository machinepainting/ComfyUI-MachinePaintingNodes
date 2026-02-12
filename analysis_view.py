import torch
import numpy as np
import cv2
from PIL import Image
import folder_paths
import os

class HistogramView:
    """
    Displays RGB and luminance histogram with in-node preview.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "show_rgb": ("BOOLEAN", {"default": True}),
                "show_luminance": ("BOOLEAN", {"default": True}),
                "line_thickness": ("INT", {"default": 1, "min": 1, "max": 5, "step": 1}),
                "background": (["black", "gray", "white"], {"default": "black"}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "create_histogram"
    CATEGORY = "MachinePaintingNodes/Analysis"

    def create_histogram(self, image, show_rgb=True, show_luminance=True, 
                         line_thickness=1, background="black", unique_id=None):
        
        img = (image[0].cpu().numpy() * 255).astype(np.uint8)
        
        # Fixed size
        width = 400
        height = int(width * 0.6)
        
        # Background color
        bg_colors = {"black": (0, 0, 0), "white": (255, 255, 255), "gray": (40, 40, 40)}
        bg_color = bg_colors.get(background, (0, 0, 0))
        
        # Create histogram canvas
        hist_img = np.full((height, width, 3), bg_color, dtype=np.uint8)
        
        # Calculate histograms
        colors = []
        hists = []
        
        if show_rgb:
            hist_r = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
            hists.append(hist_r)
            colors.append((255, 80, 80))
            
            hist_g = cv2.calcHist([img], [1], None, [256], [0, 256]).flatten()
            hists.append(hist_g)
            colors.append((80, 255, 80))
            
            hist_b = cv2.calcHist([img], [2], None, [256], [0, 256]).flatten()
            hists.append(hist_b)
            colors.append((80, 80, 255))
        
        if show_luminance:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            hist_l = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
            hists.append(hist_l)
            colors.append((200, 200, 200))
        
        if hists:
            max_val = max(h.max() for h in hists)
            if max_val == 0:
                max_val = 1
            
            bin_width = width / 256
            
            for hist, color in zip(hists, colors):
                hist_normalized = (hist / max_val * (height - 20)).astype(np.int32)
                points = []
                for i in range(256):
                    x = int(i * bin_width)
                    y = height - 10 - hist_normalized[i]
                    points.append((x, y))
                
                for i in range(len(points) - 1):
                    cv2.line(hist_img, points[i], points[i+1], color, line_thickness, cv2.LINE_AA)
            
            # Grid lines
            grid_color = (60, 60, 60) if background == "black" else (180, 180, 180)
            for val in [64, 128, 192]:
                x = int(val * bin_width)
                cv2.line(hist_img, (x, 0), (x, height), grid_color, 1)
            
            # Labels
            font = cv2.FONT_HERSHEY_SIMPLEX
            label_color = (100, 100, 100)
            cv2.putText(hist_img, "Shadows", (5, height - 3), font, 0.35, label_color, 1, cv2.LINE_AA)
            cv2.putText(hist_img, "Mids", (width//2 - 15, height - 3), font, 0.35, label_color, 1, cv2.LINE_AA)
            cv2.putText(hist_img, "Highlights", (width - 55, height - 3), font, 0.35, label_color, 1, cv2.LINE_AA)
        
        # Save preview
        preview_results = self.save_preview(hist_img, unique_id)
        
        return {"ui": {"images": preview_results}}

    def save_preview(self, img_np, unique_id):
        temp_dir = folder_paths.get_temp_directory()
        filename = f"histogram_{unique_id}.png"
        filepath = os.path.join(temp_dir, filename)
        img_pil = Image.fromarray(img_np)
        img_pil.save(filepath)
        return [{"filename": filename, "subfolder": "", "type": "temp"}]


class ColorWheelView:
    """
    Vectorscope-style color wheel showing color distribution.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "intensity": ("FLOAT", {"default": 1.0, "min": 0.2, "max": 3.0, "step": 0.1, "display": "slider"}),
                "show_skin_line": ("BOOLEAN", {"default": True}),
                "show_color_targets": ("BOOLEAN", {"default": True}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "create_vectorscope"
    CATEGORY = "MachinePaintingNodes/Analysis"

    def create_vectorscope(self, image, intensity=1.0, show_skin_line=True, 
                           show_color_targets=True, unique_id=None):
        img = (image[0].cpu().numpy() * 255).astype(np.uint8)
        
        # Fixed size
        size = 400
        
        # Convert to YUV
        yuv = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
        
        # Create scope
        scope = np.zeros((size, size, 3), dtype=np.float32)
        center = size // 2
        radius = size // 2 - 15
        
        # Draw circle outlines
        cv2.circle(scope, (center, center), radius, (0.2, 0.2, 0.2), 1)
        cv2.circle(scope, (center, center), int(radius * 0.75), (0.15, 0.15, 0.15), 1)
        cv2.circle(scope, (center, center), int(radius * 0.5), (0.12, 0.12, 0.12), 1)
        cv2.circle(scope, (center, center), int(radius * 0.25), (0.1, 0.1, 0.1), 1)
        
        # Draw crosshairs
        cv2.line(scope, (center, 10), (center, size - 10), (0.15, 0.15, 0.15), 1)
        cv2.line(scope, (10, center), (size - 10, center), (0.15, 0.15, 0.15), 1)
        
        # Color targets
        if show_color_targets:
            targets = [
                (0.5, -0.4, (0.4, 0.1, 0.1), "R"),
                (0.3, 0.5, (0.1, 0.4, 0.1), "G"),
                (-0.4, -0.5, (0.1, 0.1, 0.4), "B"),
                (-0.5, 0.4, (0.1, 0.3, 0.3), "C"),
                (-0.3, -0.5, (0.3, 0.1, 0.3), "M"),
                (0.4, 0.5, (0.3, 0.3, 0.1), "Y"),
            ]
            for u, v, color, label in targets:
                tx = int(center + u * radius * 0.85)
                ty = int(center - v * radius * 0.85)
                cv2.rectangle(scope, (tx-4, ty-4), (tx+4, ty+4), color, 1)
        
        # Skin tone line
        if show_skin_line:
            angle = np.radians(123)
            x1 = int(center + radius * 0.1 * np.cos(angle))
            y1 = int(center - radius * 0.1 * np.sin(angle))
            x2 = int(center + radius * np.cos(angle))
            y2 = int(center - radius * np.sin(angle))
            cv2.line(scope, (x1, y1), (x2, y2), (0.5, 0.35, 0.25), 2)
        
        # Sample pixels (subsample for large images)
        img_h, img_w = img.shape[:2]
        sample_step = max(1, int(np.sqrt(img_h * img_w / 50000)))
        
        u_vals = yuv[::sample_step, ::sample_step, 1].flatten().astype(np.float32) - 128
        v_vals = yuv[::sample_step, ::sample_step, 2].flatten().astype(np.float32) - 128
        
        scale = radius / 128
        x_coords = (center + u_vals * scale).astype(np.int32)
        y_coords = (center - v_vals * scale).astype(np.int32)
        
        # Accumulate with color
        for x, y in zip(x_coords, y_coords):
            if 0 <= x < size and 0 <= y < size:
                hue = np.arctan2(center - y, x - center)
                r = 0.5 + 0.5 * np.cos(hue)
                g = 0.5 + 0.5 * np.cos(hue - 2.094)
                b = 0.5 + 0.5 * np.cos(hue + 2.094)
                scope[y, x] += np.array([r, g, b]) * intensity * 0.05
        
        scope = np.clip(scope, 0, 1)
        scope_uint8 = (scope * 255).astype(np.uint8)
        
        # Save preview
        preview_results = self.save_preview(scope_uint8, unique_id)
        
        return {"ui": {"images": preview_results}}

    def save_preview(self, img_np, unique_id):
        temp_dir = folder_paths.get_temp_directory()
        filename = f"colorwheel_{unique_id}.png"
        filepath = os.path.join(temp_dir, filename)
        img_pil = Image.fromarray(img_np)
        img_pil.save(filepath)
        return [{"filename": filename, "subfolder": "", "type": "temp"}]
