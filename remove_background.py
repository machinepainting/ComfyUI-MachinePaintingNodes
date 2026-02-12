import torch
import numpy as np
import cv2
from PIL import Image
import folder_paths
import os

class RemoveBackgroundPro:
    """
    Background removal with in-node preview and mask editing tools.
    Supports multiple rembg models and provides mask refinement options.
    """
    
    # Available rembg models
    MODELS = [
        "u2net",
        "u2netp", 
        "u2net_human_seg",
        "u2net_cloth_seg",
        "silueta",
        "isnet-general-use",
        "isnet-anime",
        "sam"
    ]
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "model": (cls.MODELS, {"default": "u2net"}),
            },
            "optional": {
                # Mask editing tools
                "grow_shrink": ("INT", {
                    "default": 0, 
                    "min": -100, 
                    "max": 100, 
                    "step": 1,
                    "display": "slider"
                }),
                "blur_radius": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0.0, 
                    "max": 50.0, 
                    "step": 0.5,
                    "display": "slider"
                }),
                "fill_holes": ("BOOLEAN", {"default": False}),
                "hole_size_threshold": ("INT", {
                    "default": 500,
                    "min": 100,
                    "max": 10000,
                    "step": 100,
                    "display": "slider"
                }),
                "invert_mask": ("BOOLEAN", {"default": False}),
                # Preview options
                "preview_mode": (["transparency_grid", "black_bg", "white_bg", "no_bg", "mask_bw", "original"], {"default": "transparency_grid"}),
                # Alpha matting options
                "alpha_matting": ("BOOLEAN", {"default": False}),
                "alpha_matting_foreground_threshold": ("INT", {
                    "default": 240,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "display": "slider"
                }),
                "alpha_matting_background_threshold": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "display": "slider"
                }),
                "alpha_matting_erode_size": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 40,
                    "step": 1,
                    "display": "slider"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("image_passthrough", "masked_image", "mask", "mask_bw")
    OUTPUT_NODE = True
    FUNCTION = "remove_background"
    CATEGORY = "MachinePaintingNodes/Mask"

    def remove_background(self, image, model,
                          grow_shrink=0, blur_radius=0.0, fill_holes=False,
                          hole_size_threshold=500, invert_mask=False,
                          preview_mode="masked_image", alpha_matting=False,
                          alpha_matting_foreground_threshold=240,
                          alpha_matting_background_threshold=10,
                          alpha_matting_erode_size=10,
                          unique_id=None):
        
        # Import rembg here to avoid loading if not used
        try:
            from rembg import remove, new_session
        except ImportError:
            raise ImportError("rembg is required. Install with: pip install rembg")
        
        # Convert tensor to PIL
        img_np = (image[0].cpu().numpy() * 255).astype(np.uint8)
        img_pil = Image.fromarray(img_np, mode='RGB')
        
        # Create session with selected model
        session = new_session(model)
        
        # Remove background
        if alpha_matting:
            result_pil = remove(
                img_pil,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=alpha_matting_background_threshold,
                alpha_matting_erode_size=alpha_matting_erode_size
            )
        else:
            result_pil = remove(img_pil, session=session)
        
        # Convert to numpy and extract alpha channel as mask
        result_np = np.array(result_pil)
        
        # Get original image dimensions
        orig_h, orig_w = img_np.shape[:2]
        
        if result_np.shape[2] == 4:
            # Has alpha channel
            mask = result_np[:, :, 3].astype(np.float32) / 255.0
            rgb = result_np[:, :, :3]
        else:
            # No alpha, create mask from non-zero pixels
            mask = np.any(result_np > 0, axis=2).astype(np.float32)
            rgb = result_np
        
        # Resize mask to match original image if needed
        if mask.shape[0] != orig_h or mask.shape[1] != orig_w:
            mask = cv2.resize(mask, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
        
        # Apply mask editing
        mask = self.edit_mask(mask, grow_shrink, blur_radius, fill_holes, hole_size_threshold)
        
        # Invert if requested
        if invert_mask:
            mask = 1.0 - mask
        
        # Create outputs
        h, w = img_np.shape[:2]
        
        # Passthrough (original image)
        passthrough = image
        
        # Masked image (RGB with transparency applied - checkerboard for transparency)
        mask_3ch = np.stack([mask, mask, mask], axis=2)
        masked_rgb = (img_np.astype(np.float32) / 255.0) * mask_3ch
        masked_image = torch.from_numpy(masked_rgb).unsqueeze(0)
        
        # Mask output (single channel)
        mask_tensor = torch.from_numpy(mask).unsqueeze(0)
        
        # Black and white mask image (3 channel for preview)
        mask_bw = np.stack([mask, mask, mask], axis=2)
        mask_bw_tensor = torch.from_numpy(mask_bw).unsqueeze(0)
        
        # Create preview image based on preview_mode
        if preview_mode == "transparency_grid":
            preview_img = self.create_transparency_grid_preview(img_np, mask)
        elif preview_mode == "black_bg":
            preview_img = self.create_solid_bg_preview(img_np, mask, (0, 0, 0))
        elif preview_mode == "white_bg":
            preview_img = self.create_solid_bg_preview(img_np, mask, (255, 255, 255))
        elif preview_mode == "no_bg":
            # Return RGBA image with actual transparency (PNG with alpha)
            preview_img = self.create_rgba_preview(img_np, mask)
        elif preview_mode == "mask_bw":
            preview_img = (mask_bw * 255).astype(np.uint8)
        else:  # original
            preview_img = img_np
        
        # Save preview image for in-node display
        preview_results = self.save_preview_image(preview_img, unique_id)
        
        return {
            "ui": {"images": preview_results},
            "result": (passthrough, masked_image, mask_tensor, mask_bw_tensor)
        }

    def create_transparency_grid_preview(self, img_np, mask):
        """Create preview with soft transparency grid background."""
        h, w = img_np.shape[:2]
        
        # Create soft grid (lower contrast - gray tones)
        check_size = 16
        grid = np.zeros((h, w, 3), dtype=np.uint8)
        for y in range(0, h, check_size):
            for x in range(0, w, check_size):
                is_light = ((x // check_size) + (y // check_size)) % 2 == 0
                color = 160 if is_light else 140  # Soft contrast
                y_end = min(y + check_size, h)
                x_end = min(x + check_size, w)
                grid[y:y_end, x:x_end] = color
        
        # Composite image over grid
        mask_3ch = np.stack([mask, mask, mask], axis=2)
        preview = (img_np.astype(np.float32) * mask_3ch + 
                   grid.astype(np.float32) * (1 - mask_3ch))
        
        return preview.astype(np.uint8)

    def create_rgba_preview(self, img_np, mask):
        """Create RGBA image with actual transparency."""
        h, w = img_np.shape[:2]
        
        # Create RGBA array
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[:, :, :3] = img_np
        rgba[:, :, 3] = (mask * 255).astype(np.uint8)
        
        return rgba

    def create_solid_bg_preview(self, img_np, mask, bg_color):
        """Create preview with solid color background."""
        h, w = img_np.shape[:2]
        
        # Create solid background
        background = np.full((h, w, 3), bg_color, dtype=np.uint8)
        
        # Composite image over background
        mask_3ch = np.stack([mask, mask, mask], axis=2)
        preview = (img_np.astype(np.float32) * mask_3ch + 
                   background.astype(np.float32) * (1 - mask_3ch))
        
        return preview.astype(np.uint8)

    def save_preview_image(self, img_np, unique_id):
        """Save preview image and return results for UI."""
        # Get temp directory
        temp_dir = folder_paths.get_temp_directory()
        
        # Create filename
        filename = f"rembg_preview_{unique_id}.png"
        filepath = os.path.join(temp_dir, filename)
        
        # Save image (handle both RGB and RGBA)
        if img_np.shape[2] == 4:
            img_pil = Image.fromarray(img_np, mode='RGBA')
        else:
            img_pil = Image.fromarray(img_np, mode='RGB')
        img_pil.save(filepath)
        
        return [{
            "filename": filename,
            "subfolder": "",
            "type": "temp"
        }]

    def edit_mask(self, mask, grow_shrink, blur_radius, fill_holes, hole_size_threshold):
        """Apply mask editing operations."""
        
        # Convert to uint8 for OpenCV operations
        mask_uint8 = (mask * 255).astype(np.uint8)
        
        # Fill holes
        if fill_holes:
            mask_uint8 = self.fill_mask_holes(mask_uint8, hole_size_threshold)
        
        # Grow/shrink (dilate/erode)
        if grow_shrink != 0:
            kernel_size = abs(grow_shrink) * 2 + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            
            if grow_shrink > 0:
                # Grow/expand
                mask_uint8 = cv2.dilate(mask_uint8, kernel, iterations=1)
            else:
                # Shrink/contract
                mask_uint8 = cv2.erode(mask_uint8, kernel, iterations=1)
        
        # Blur edges
        if blur_radius > 0:
            # Use odd kernel size
            ksize = int(blur_radius * 2) | 1
            mask_uint8 = cv2.GaussianBlur(mask_uint8, (ksize, ksize), blur_radius)
        
        # Convert back to float
        return mask_uint8.astype(np.float32) / 255.0

    def fill_mask_holes(self, mask, threshold):
        """Fill small holes in the mask."""
        # Find contours
        contours, hierarchy = cv2.findContours(
            255 - mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Fill small holes
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < threshold:
                cv2.drawContours(mask, [contour], -1, 255, -1)
        
        return mask


class MaskEditor:
    """
    Standalone mask editing node for refining any mask.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
            },
            "optional": {
                "grow_shrink": ("INT", {
                    "default": 0, 
                    "min": -100, 
                    "max": 100, 
                    "step": 1,
                    "display": "slider"
                }),
                "blur_radius": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0.0, 
                    "max": 50.0, 
                    "step": 0.5,
                    "display": "slider"
                }),
                "fill_holes": ("BOOLEAN", {"default": False}),
                "hole_size_threshold": ("INT", {
                    "default": 500,
                    "min": 100,
                    "max": 10000,
                    "step": 100,
                    "display": "slider"
                }),
                "invert": ("BOOLEAN", {"default": False}),
                "threshold": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                "apply_threshold": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("MASK", "IMAGE")
    RETURN_NAMES = ("mask", "mask_preview")
    FUNCTION = "edit_mask"
    CATEGORY = "MachinePaintingNodes/Mask"

    def edit_mask(self, mask, grow_shrink=0, blur_radius=0.0, fill_holes=False,
                  hole_size_threshold=500, invert=False, threshold=0.5, apply_threshold=False):
        
        # Handle batch dimension
        if len(mask.shape) == 3:
            mask_np = mask[0].cpu().numpy()
        else:
            mask_np = mask.cpu().numpy()
        
        mask_np = mask_np.astype(np.float32)
        
        # Ensure 0-1 range
        if mask_np.max() > 1.0:
            mask_np = mask_np / 255.0
        
        # Convert to uint8 for OpenCV
        mask_uint8 = (mask_np * 255).astype(np.uint8)
        
        # Fill holes
        if fill_holes:
            contours, _ = cv2.findContours(255 - mask_uint8, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) < hole_size_threshold:
                    cv2.drawContours(mask_uint8, [contour], -1, 255, -1)
        
        # Grow/shrink
        if grow_shrink != 0:
            kernel_size = abs(grow_shrink) * 2 + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            if grow_shrink > 0:
                mask_uint8 = cv2.dilate(mask_uint8, kernel, iterations=1)
            else:
                mask_uint8 = cv2.erode(mask_uint8, kernel, iterations=1)
        
        # Blur
        if blur_radius > 0:
            ksize = int(blur_radius * 2) | 1
            mask_uint8 = cv2.GaussianBlur(mask_uint8, (ksize, ksize), blur_radius)
        
        # Convert back to float
        result = mask_uint8.astype(np.float32) / 255.0
        
        # Apply threshold
        if apply_threshold:
            result = (result > threshold).astype(np.float32)
        
        # Invert
        if invert:
            result = 1.0 - result
        
        # Create outputs
        mask_tensor = torch.from_numpy(result).unsqueeze(0)
        
        # Preview (3 channel)
        preview = np.stack([result, result, result], axis=2)
        preview_tensor = torch.from_numpy(preview).unsqueeze(0)
        
        return (mask_tensor, preview_tensor)


class ApplyMask:
    """
    Apply a mask to an image with various blend options.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
            },
            "optional": {
                "background": (["transparent", "black", "white", "color"], {"default": "transparent"}),
                "bg_color_r": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "display": "slider"}),
                "bg_color_g": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "display": "slider"}),
                "bg_color_b": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "display": "slider"}),
                "invert_mask": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("masked_image", "rgba_image")
    FUNCTION = "apply_mask"
    CATEGORY = "MachinePaintingNodes/Mask"

    def apply_mask(self, image, mask, background="transparent", 
                   bg_color_r=0, bg_color_g=0, bg_color_b=0, invert_mask=False):
        
        img = image[0].cpu().numpy()
        
        # Handle mask dimensions
        if len(mask.shape) == 3:
            mask_np = mask[0].cpu().numpy()
        else:
            mask_np = mask.cpu().numpy()
        
        # Resize mask if needed
        if mask_np.shape[:2] != img.shape[:2]:
            mask_np = cv2.resize(mask_np, (img.shape[1], img.shape[0]))
        
        # Invert if requested
        if invert_mask:
            mask_np = 1.0 - mask_np
        
        # Create background
        h, w = img.shape[:2]
        if background == "black":
            bg = np.zeros((h, w, 3), dtype=np.float32)
        elif background == "white":
            bg = np.ones((h, w, 3), dtype=np.float32)
        elif background == "color":
            bg = np.zeros((h, w, 3), dtype=np.float32)
            bg[:, :, 0] = bg_color_r / 255.0
            bg[:, :, 1] = bg_color_g / 255.0
            bg[:, :, 2] = bg_color_b / 255.0
        else:  # transparent - use black
            bg = np.zeros((h, w, 3), dtype=np.float32)
        
        # Apply mask
        mask_3ch = np.stack([mask_np, mask_np, mask_np], axis=2)
        masked = img * mask_3ch + bg * (1 - mask_3ch)
        
        # Create RGBA output (for transparent background)
        rgba = np.zeros((h, w, 4), dtype=np.float32)
        rgba[:, :, :3] = img
        rgba[:, :, 3] = mask_np
        
        masked_tensor = torch.from_numpy(masked).unsqueeze(0)
        rgba_tensor = torch.from_numpy(rgba[:, :, :3]).unsqueeze(0)  # Return RGB, mask is separate
        
        return (masked_tensor, rgba_tensor)
