import torch
import numpy as np
import cv2
from PIL import Image
import folder_paths
import os


class BlurPro:
    """
    Professional blur node with multiple blur types: Gaussian, Surface (Bilateral),
    Box, Median, and Motion blur. Supports mask-controlled application and in-node preview.
    """

    BLUR_TYPES = ["gaussian", "surface", "box", "median", "motion"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "blur_type": (cls.BLUR_TYPES, {"default": "gaussian"}),
            },
            "optional": {
                # --- Shared ---
                "strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),

                # --- Gaussian / Surface / Box / Median ---
                "radius": ("FLOAT", {
                    "default": 5.0,
                    "min": 0.5,
                    "max": 100.0,
                    "step": 0.5,
                    "display": "slider"
                }),

                # --- Surface Blur only (advanced) ---
                "threshold": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 255.0,
                    "step": 1.0,
                    "display": "slider",
                    "advanced": True,
                }),

                # --- Motion Blur only (advanced) ---
                "angle": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 360.0,
                    "step": 1.0,
                    "display": "slider",
                    "advanced": True,
                }),
                # --- Mask options ---
                "mask": ("MASK",),
                "invert_mask": ("BOOLEAN", {"default": False}),
                "blur_mask": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    OUTPUT_NODE = True
    FUNCTION = "apply_blur"
    CATEGORY = "MachinePaintingNodes/Filter"

    def apply_blur(self, image, blur_type,
                   strength=1.0, radius=5.0, threshold=30.0,
                   angle=0.0,
                   mask=None, invert_mask=False, blur_mask=False,
                   unique_id=None):

        img = image[0].cpu().numpy().astype(np.float32)
        h, w = img.shape[:2]

        # Apply the selected blur type
        if blur_type == "gaussian":
            blurred = self._gaussian_blur(img, radius)
        elif blur_type == "surface":
            blurred = self._surface_blur(img, radius, threshold)
        elif blur_type == "box":
            blurred = self._box_blur(img, radius)
        elif blur_type == "median":
            blurred = self._median_blur(img, radius)
        elif blur_type == "motion":
            blurred = self._motion_blur(img, angle, radius)
        else:
            blurred = img.copy()

        # Handle mask input
        mask_np = None
        if mask is not None:
            if len(mask.shape) == 3:
                mask_np = mask[0].cpu().numpy().astype(np.float32)
            else:
                mask_np = mask.cpu().numpy().astype(np.float32)

            if mask_np.shape[:2] != (h, w):
                mask_np = cv2.resize(mask_np, (w, h), interpolation=cv2.INTER_LINEAR)

            if invert_mask:
                mask_np = 1.0 - mask_np

        # Blend blurred with original using strength
        result = img * (1.0 - strength) + blurred * strength

        # Apply mask: masked areas get blur, unmasked areas keep original
        if mask_np is not None:
            mask_3ch = np.expand_dims(mask_np, axis=-1)
            result = img * (1.0 - mask_3ch) + result * mask_3ch

        result = np.clip(result, 0.0, 1.0)

        # Handle mask output
        if mask_np is not None:
            out_mask = mask_np.copy()
            if blur_mask:
                if blur_type == "gaussian":
                    out_mask = self._gaussian_blur_single(out_mask, radius)
                elif blur_type == "surface":
                    out_mask = self._surface_blur_single(out_mask, radius, threshold)
                elif blur_type == "box":
                    out_mask = self._box_blur_single(out_mask, radius)
                elif blur_type == "median":
                    out_mask = self._median_blur_single(out_mask, radius)
                elif blur_type == "motion":
                    out_mask = self._motion_blur_single(out_mask, angle, radius)
        else:
            out_mask = np.ones((h, w), dtype=np.float32)

        # Build output tensors
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        mask_tensor = torch.from_numpy(out_mask).unsqueeze(0)

        # Save preview
        preview_img = (np.clip(result, 0, 1) * 255).astype(np.uint8)
        preview_results = self._save_preview(preview_img, unique_id)

        return {
            "ui": {"images": preview_results},
            "result": (result_tensor, mask_tensor)
        }

    # -------------------------------------------------------------------------
    # Large radius optimization
    # -------------------------------------------------------------------------
    # For radius > DOWNSCALE_THRESHOLD, downscale image to ~10%, blur with
    # proportionally smaller kernel, then upscale back. Matches spacepxl's
    # approach — massive speedup for bilateral/median at large radii.

    DOWNSCALE_THRESHOLD = 30
    DOWNSCALE_FACTOR = 0.1

    def _optimized_blur(self, data, blur_fn, radius, *args):
        """Run blur_fn with automatic downscale optimization for large radii."""
        if radius <= self.DOWNSCALE_THRESHOLD:
            return blur_fn(data, radius, *args)

        h, w = data.shape[:2]
        small_h = max(int(h * self.DOWNSCALE_FACTOR), 1)
        small_w = max(int(w * self.DOWNSCALE_FACTOR), 1)
        small_radius = max(radius * self.DOWNSCALE_FACTOR, 0.5)

        small = cv2.resize(data, (small_w, small_h), interpolation=cv2.INTER_AREA)
        blurred_small = blur_fn(small, small_radius, *args)
        return cv2.resize(blurred_small, (w, h), interpolation=cv2.INTER_LINEAR)

    # -------------------------------------------------------------------------
    # Blur algorithms (3-channel image)
    # -------------------------------------------------------------------------

    def _gaussian_blur_core(self, img, radius):
        ksize = max(int(radius * 2) | 1, 1)
        return cv2.GaussianBlur(img, (ksize, ksize), radius)

    def _gaussian_blur(self, img, radius):
        return self._optimized_blur(img, self._gaussian_blur_core, radius)

    def _surface_blur_core(self, img, radius, threshold):
        img_u8 = (img * 255).astype(np.uint8)
        d = max(int(radius * 2) | 1, 3)
        result = cv2.bilateralFilter(img_u8, d=d, sigmaColor=threshold, sigmaSpace=radius)
        return result.astype(np.float32) / 255.0

    def _surface_blur(self, img, radius, threshold):
        return self._optimized_blur(img, self._surface_blur_core, radius, threshold)

    def _box_blur_core(self, img, radius):
        ksize = max(int(radius * 2) | 1, 3)
        return cv2.blur(img, (ksize, ksize))

    def _box_blur(self, img, radius):
        return self._optimized_blur(img, self._box_blur_core, radius)

    def _median_blur_core(self, img, radius):
        ksize = max(int(radius * 2) | 1, 3)
        img_u8 = (img * 255).astype(np.uint8)
        result = cv2.medianBlur(img_u8, ksize)
        return result.astype(np.float32) / 255.0

    def _median_blur(self, img, radius):
        return self._optimized_blur(img, self._median_blur_core, radius)

    def _motion_blur(self, img, angle, distance):
        kernel = self._make_motion_kernel(angle, distance)
        return cv2.filter2D(img, -1, kernel)

    def _make_motion_kernel(self, angle, distance):
        distance = max(int(distance), 1)
        kernel = np.zeros((distance, distance), dtype=np.float32)
        center = distance // 2
        cos_a = np.cos(np.radians(angle))
        sin_a = np.sin(np.radians(angle))
        for i in range(distance):
            offset = i - center
            x = int(round(center + offset * cos_a))
            y = int(round(center + offset * sin_a))
            if 0 <= x < distance and 0 <= y < distance:
                kernel[y, x] = 1.0
        if kernel.sum() > 0:
            kernel /= kernel.sum()
        else:
            kernel[center, center] = 1.0
        return kernel

    # -------------------------------------------------------------------------
    # Blur algorithms (single-channel mask) — same optimization
    # -------------------------------------------------------------------------

    def _gaussian_blur_single(self, mask, radius):
        return self._optimized_blur(mask, self._gaussian_blur_core, radius)

    def _surface_blur_single(self, mask, radius, threshold):
        return self._optimized_blur(mask, self._surface_blur_core, radius, threshold)

    def _box_blur_single(self, mask, radius):
        return self._optimized_blur(mask, self._box_blur_core, radius)

    def _median_blur_single(self, mask, radius):
        return self._optimized_blur(mask, self._median_blur_core, radius)

    def _motion_blur_single(self, mask, angle, distance):
        kernel = self._make_motion_kernel(angle, distance)
        return cv2.filter2D(mask, -1, kernel)

    # -------------------------------------------------------------------------
    # Preview
    # -------------------------------------------------------------------------

    def _save_preview(self, img_np, unique_id):
        temp_dir = folder_paths.get_temp_directory()
        filename = f"blur_pro_{unique_id}.png"
        filepath = os.path.join(temp_dir, filename)
        img_pil = Image.fromarray(img_np, mode='RGB')
        img_pil.save(filepath)
        return [{"filename": filename, "subfolder": "", "type": "temp"}]
