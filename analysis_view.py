import torch
import numpy as np
from PIL import Image
import folder_paths
import os

class HistogramView:
    """
    Display RGB and luminance histogram in-node.
    Auto-scales to node width.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "mode": (["rgb", "luminance", "rgb+luminance"], {"default": "rgb"}),
                "width": ("INT", {"default": 400, "min": 256, "max": 1024, "step": 8}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "create_histogram"
    CATEGORY = "MachinePaintingNodes"

    def create_histogram(self, image, mode="rgb", width=400, unique_id=None):
        img = image[0].cpu().numpy()
        img_uint8 = (img * 255).astype(np.uint8)
        
        height = int(width * 0.6)
        histogram_img = np.zeros((height, width, 3), dtype=np.uint8)
        histogram_img[:] = (30, 30, 30)
        
        bins = 256
        
        if mode in ["rgb", "rgb+luminance"]:
            for i, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
                hist, _ = np.histogram(img_uint8[:, :, i].flatten(), bins=bins, range=(0, 256))
                hist = hist.astype(np.float32)
                hist = hist / (hist.max() + 1e-6)
                
                for x in range(width):
                    bin_idx = int(x * bins / width)
                    bar_height = int(hist[bin_idx] * (height - 10))
                    if bar_height > 0:
                        histogram_img[height - bar_height - 5:height - 5, x, i] = color[i] // 2
        
        if mode in ["luminance", "rgb+luminance"]:
            lum = (0.299 * img_uint8[:, :, 0] + 0.587 * img_uint8[:, :, 1] + 0.114 * img_uint8[:, :, 2]).astype(np.uint8)
            hist, _ = np.histogram(lum.flatten(), bins=bins, range=(0, 256))
            hist = hist.astype(np.float32)
            hist = hist / (hist.max() + 1e-6)
            
            for x in range(width):
                bin_idx = int(x * bins / width)
                bar_height = int(hist[bin_idx] * (height - 10))
                if bar_height > 0:
                    for y in range(height - bar_height - 5, height - 5):
                        histogram_img[y, x] = np.maximum(histogram_img[y, x], [180, 180, 180])
        
        preview_results = self.save_preview(histogram_img, unique_id)
        
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
    Display vectorscope/color wheel visualization in-node.
    Shows color distribution of the image.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "size": ("INT", {"default": 400, "min": 256, "max": 1024, "step": 8}),
                "intensity": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "create_color_wheel"
    CATEGORY = "MachinePaintingNodes"

    def create_color_wheel(self, image, size=400, intensity=1.0, unique_id=None):
        img = image[0].cpu().numpy()
        img_uint8 = (img * 255).astype(np.uint8)
        
        # Create color wheel background
        wheel_img = np.zeros((size, size, 3), dtype=np.uint8)
        wheel_img[:] = (25, 25, 25)
        
        center = size // 2
        radius = center - 10
        
        # Draw circle outline
        for angle in range(360):
            rad = np.radians(angle)
            x = int(center + radius * np.cos(rad))
            y = int(center + radius * np.sin(rad))
            wheel_img[y-1:y+2, x-1:x+2] = (60, 60, 60)
        
        # Draw crosshairs
        wheel_img[center-1:center+2, 10:size-10] = (40, 40, 40)
        wheel_img[10:size-10, center-1:center+2] = (40, 40, 40)
        
        # Sample pixels and plot on wheel
        h, w = img_uint8.shape[:2]
        sample_step = max(1, (h * w) // 50000)
        
        for y in range(0, h, sample_step):
            for x in range(0, w, sample_step):
                r, g, b = img_uint8[y, x]
                
                # Convert to color wheel position (simplified UV)
                u = (r - 128) / 128.0
                v = (b - 128) / 128.0
                
                px = int(center + u * radius * 0.8)
                py = int(center + v * radius * 0.8)
                
                if 0 <= px < size and 0 <= py < size:
                    wheel_img[py, px] = np.minimum(255, wheel_img[py, px].astype(np.float32) + np.array([r, g, b]) * intensity * 0.3).astype(np.uint8)
        
        preview_results = self.save_preview(wheel_img, unique_id)
        
        return {"ui": {"images": preview_results}}

    def save_preview(self, img_np, unique_id):
        temp_dir = folder_paths.get_temp_directory()
        filename = f"colorwheel_{unique_id}.png"
        filepath = os.path.join(temp_dir, filename)
        img_pil = Image.fromarray(img_np)
        img_pil.save(filepath)
        return [{"filename": filename, "subfolder": "", "type": "temp"}]
