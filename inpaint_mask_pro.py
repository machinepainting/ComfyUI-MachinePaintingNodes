import torch
import numpy as np
import cv2
from PIL import Image
import folder_paths
import os


class InpaintMaskPro:
    """
    Combines an inpaint mask with an optional silhouette mask or SEGS input
    to produce a clean, cropped inpaint region. Provides multi-color overlay preview
    with independent color/opacity control per mask layer.
    """

    IN_MASK_COLORS = ["red", "light_blue", "black", "white"]
    MASK_COLORS = ["lime_green", "purple", "black", "white"]
    SEGS_COLORS = ["yellow", "orange", "black", "white"]

    COLOR_MAP = {
        "red":        np.array([1.0, 0.2, 0.2], dtype=np.float32),
        "light_blue": np.array([0.3, 0.7, 1.0], dtype=np.float32),
        "black":      np.array([0.0, 0.0, 0.0], dtype=np.float32),
        "white":      np.array([1.0, 1.0, 1.0], dtype=np.float32),
        "lime_green": np.array([0.2, 1.0, 0.2], dtype=np.float32),
        "purple":     np.array([0.7, 0.2, 1.0], dtype=np.float32),
        "yellow":     np.array([1.0, 1.0, 0.2], dtype=np.float32),
        "orange":     np.array([1.0, 0.6, 0.1], dtype=np.float32),
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "inpaint_mask": ("MASK",),
            },
            "optional": {
                # --- Inpaint mask settings ---
                "invert_mask": ("BOOLEAN", {"default": False, "label_on": "inverted", "label_off": "normal"}),
                "inpaint_blur": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 50.0,
                    "step": 0.5,
                    "display": "slider"
                }),

                # --- Inpaint mask display ---
                "show_in_mask": ("BOOLEAN", {"default": True, "label_on": "on", "label_off": "off"}),
                "in_mask_color": (cls.IN_MASK_COLORS, {"default": "red"}),
                "in_mask_opacity": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),

                # --- Mask crop settings ---
                "use_mask": ("BOOLEAN", {"default": False, "label_on": "on", "label_off": "off"}),
                "mask": ("MASK",),
                "mask_blur": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 50.0,
                    "step": 0.5,
                    "display": "slider"
                }),
                "mask_expand": ("INT", {
                    "default": 0,
                    "min": -100,
                    "max": 100,
                    "step": 1,
                    "display": "slider"
                }),

                # --- Mask display ---
                "show_mask": ("BOOLEAN", {"default": False, "label_on": "on", "label_off": "off"}),
                "mask_color": (cls.MASK_COLORS, {"default": "lime_green"}),
                "mask_opacity": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),

                # --- SEGS settings ---
                "use_segs": ("BOOLEAN", {"default": False, "label_on": "on", "label_off": "off"}),
                "segs": ("SEGS",),
                "segs_combine": (["union", "largest"], {"default": "union"}),

                # --- SEGS display ---
                "show_segs": ("BOOLEAN", {"default": False, "label_on": "on", "label_off": "off"}),
                "segs_color": (cls.SEGS_COLORS, {"default": "yellow"}),
                "segs_opacity": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE", "IMAGE")
    RETURN_NAMES = ("image_thru", "mask", "mask_bw", "preview_out")
    OUTPUT_NODE = True
    FUNCTION = "process"
    CATEGORY = "MachinePaintingNodes/Mask"

    def process(self, image, inpaint_mask,
                invert_mask=False, inpaint_blur=0.0,
                show_in_mask=True, in_mask_color="red", in_mask_opacity=0.5,
                use_mask=False, mask=None, mask_blur=0.0, mask_expand=0,
                show_mask=False, mask_color="lime_green", mask_opacity=0.3,
                use_segs=False, segs=None, segs_combine="union",
                show_segs=False, segs_color="yellow", segs_opacity=0.3,
                unique_id=None):

        img = image[0].cpu().numpy().astype(np.float32)
        h, w = img.shape[:2]

        # --- Process inpaint mask ---
        inpaint = self._to_numpy_mask(inpaint_mask, h, w)

        if invert_mask:
            inpaint = 1.0 - inpaint

        if inpaint_blur > 0:
            ksize = max(int(inpaint_blur * 2) | 1, 3)
            inpaint = cv2.GaussianBlur(inpaint, (ksize, ksize), inpaint_blur)

        # --- Process crop mask (from mask input) ---
        crop_mask = None
        if use_mask and mask is not None:
            crop_mask = self._to_numpy_mask(mask, h, w)

            # Expand/contract
            if mask_expand != 0:
                kernel_size = abs(mask_expand) * 2 + 1
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
                mask_u8 = (crop_mask * 255).astype(np.uint8)
                if mask_expand > 0:
                    mask_u8 = cv2.dilate(mask_u8, kernel, iterations=1)
                else:
                    mask_u8 = cv2.erode(mask_u8, kernel, iterations=1)
                crop_mask = mask_u8.astype(np.float32) / 255.0

            if mask_blur > 0:
                ksize = max(int(mask_blur * 2) | 1, 3)
                crop_mask = cv2.GaussianBlur(crop_mask, (ksize, ksize), mask_blur)

        # --- Process SEGS mask ---
        segs_mask = None
        if use_segs and segs is not None:
            segs_mask = self._segs_to_mask(segs, h, w, segs_combine)

        # --- Combine: intersect inpaint mask with crop sources ---
        result_mask = inpaint.copy()

        if crop_mask is not None:
            result_mask = result_mask * crop_mask

        if segs_mask is not None:
            result_mask = result_mask * segs_mask

        result_mask = np.clip(result_mask, 0.0, 1.0)

        # --- Create preview overlay (layer each mask color) ---
        preview_np = img.copy()

        # Layer 1: Mask input (silhouette) — drawn first (background layer)
        if show_mask and crop_mask is not None and mask_opacity > 0:
            preview_np = self._overlay_color(preview_np, crop_mask, mask_color, mask_opacity)

        # Layer 2: SEGS mask
        if show_segs and segs_mask is not None and segs_opacity > 0:
            preview_np = self._overlay_color(preview_np, segs_mask, segs_color, segs_opacity)

        # Layer 3: Inpaint mask (final result) — drawn last (top layer)
        if show_in_mask and in_mask_opacity > 0:
            preview_np = self._overlay_color(preview_np, result_mask, in_mask_color, in_mask_opacity)

        preview_np = np.clip(preview_np, 0.0, 1.0)

        # --- Build outputs ---
        mask_tensor = torch.from_numpy(result_mask).unsqueeze(0)
        mask_bw = np.stack([result_mask, result_mask, result_mask], axis=-1)
        mask_bw_tensor = torch.from_numpy(mask_bw).unsqueeze(0)
        preview_tensor = torch.from_numpy(preview_np).unsqueeze(0)

        # Save in-node preview
        preview_u8 = (preview_np * 255).astype(np.uint8)
        preview_results = self._save_preview(preview_u8, unique_id)

        return {
            "ui": {"images": preview_results},
            "result": (image, mask_tensor, mask_bw_tensor, preview_tensor)
        }

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _to_numpy_mask(self, mask_tensor, h, w):
        """Convert MASK tensor to float32 numpy array, resized to match image."""
        if len(mask_tensor.shape) == 3:
            m = mask_tensor[0].cpu().numpy().astype(np.float32)
        else:
            m = mask_tensor.cpu().numpy().astype(np.float32)
        if m.shape[:2] != (h, w):
            m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
        return m

    def _overlay_color(self, img, mask, color_name, opacity):
        """Blend a color overlay onto image where mask is active."""
        color = self.COLOR_MAP.get(color_name, self.COLOR_MAP["red"])
        mask_3ch = np.expand_dims(mask, axis=-1)
        color_layer = np.ones_like(img) * color
        return img * (1.0 - mask_3ch * opacity) + color_layer * (mask_3ch * opacity)

    def _segs_to_mask(self, segs, h, w, combine_mode):
        """Convert SEGS data to a single mask."""
        try:
            shape, seg_list = segs
            if not seg_list:
                return np.zeros((h, w), dtype=np.float32)

            if combine_mode == "largest":
                best_seg = None
                best_area = 0
                for seg in seg_list:
                    crop_region = seg[3]
                    area = (crop_region[2] - crop_region[0]) * (crop_region[3] - crop_region[1])
                    if area > best_area:
                        best_area = area
                        best_seg = seg
                if best_seg is not None:
                    return self._seg_to_full_mask(best_seg, h, w)
                return np.zeros((h, w), dtype=np.float32)

            else:  # union
                combined = np.zeros((h, w), dtype=np.float32)
                for seg in seg_list:
                    seg_mask = self._seg_to_full_mask(seg, h, w)
                    combined = np.maximum(combined, seg_mask)
                return combined

        except Exception:
            return np.zeros((h, w), dtype=np.float32)

    def _seg_to_full_mask(self, seg, h, w):
        """Place a single SEG's cropped mask into a full-size mask."""
        try:
            cropped_mask = seg[1]
            crop_region = seg[3]

            if isinstance(cropped_mask, torch.Tensor):
                cropped_mask = cropped_mask.cpu().numpy()
            if len(cropped_mask.shape) == 3:
                cropped_mask = cropped_mask[0]
            cropped_mask = cropped_mask.astype(np.float32)
            if cropped_mask.max() > 1.0:
                cropped_mask = cropped_mask / 255.0

            x1, y1, x2, y2 = crop_region
            full_mask = np.zeros((h, w), dtype=np.float32)

            region_h = y2 - y1
            region_w = x2 - x1
            if region_h > 0 and region_w > 0:
                resized = cv2.resize(cropped_mask, (region_w, region_h), interpolation=cv2.INTER_LINEAR)
                paste_y1 = max(y1, 0)
                paste_y2 = min(y2, h)
                paste_x1 = max(x1, 0)
                paste_x2 = min(x2, w)
                src_y1 = paste_y1 - y1
                src_y2 = src_y1 + (paste_y2 - paste_y1)
                src_x1 = paste_x1 - x1
                src_x2 = src_x1 + (paste_x2 - paste_x1)
                full_mask[paste_y1:paste_y2, paste_x1:paste_x2] = resized[src_y1:src_y2, src_x1:src_x2]

            return full_mask
        except Exception:
            return np.zeros((h, w), dtype=np.float32)

    def _save_preview(self, img_np, unique_id):
        temp_dir = folder_paths.get_temp_directory()
        filename = f"inpaint_mask_{unique_id}.png"
        filepath = os.path.join(temp_dir, filename)
        img_pil = Image.fromarray(img_np, mode='RGB')
        img_pil.save(filepath)
        return [{"filename": filename, "subfolder": "", "type": "temp"}]
