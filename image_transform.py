import torch
import numpy as np
from PIL import Image
import folder_paths
import os

from .transform_utils import (
    build_matrix,
    coverage_mask,
    fit_scale,
    normalize_mask,
    snap_angle,
    transparency_grid,
    warp_image,
    warp_single,
    zoom_to_scale,
)


class ImageTransformPro:
    """
    Rotate, scale and reposition an image inside a definable canvas.

    Rotation reads counter-clockwise to the left of centre and clockwise to the
    right. The "fixed" method snaps the angle to 45 degree increments. Zoom is
    centred on 0 (1.0x) and exponential: -100 = 0.25x, -50 = 0.5x, +50 = 2x,
    +100 = 4x. An optional mask input rides the exact same matrix so it stays
    registered to the image, and cuts the image out: whatever the mask leaves
    out is filled with the selected background. With no mask supplied, the
    transformed image extent becomes the mask.
    """

    # ComfyUI reads DESCRIPTION (not the docstring) for the node tooltip and
    # indexes it for node search, so name the verbs the node is looked up by.
    DESCRIPTION = (
        "Rotate, scale, zoom and move an image inside a definable canvas. "
        "Free or fixed 45 degree rotation, centre-zero zoom and XY placement. "
        "An optional mask is transformed with the image and cuts it out over a "
        "transparent, black or white background."
    )

    ROTATION_METHODS = ["free", "fixed"]
    BACKGROUNDS = ["transparent", "black", "white"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "mask": ("MASK",),

                # --- Canvas (0 = match the incoming image) ---
                "canvas_width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 8
                }),
                "canvas_height": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 8
                }),
                "background": (cls.BACKGROUNDS, {"default": "transparent"}),

                # --- Rotation ---
                "rotation_method": (cls.ROTATION_METHODS, {"default": "free"}),
                "rotation_angle": ("FLOAT", {
                    "default": 0.0,
                    "min": -180.0,
                    "max": 180.0,
                    "step": 0.1,
                    "display": "slider"
                }),

                # --- Zoom ---
                "zoom": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "slider"
                }),

                # --- Placement (percent of canvas) ---
                "offset_x": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "slider"
                }),
                "offset_y": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.1,
                    "display": "slider"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("image", "mask", "mask_bw")
    OUTPUT_NODE = True
    FUNCTION = "rotate_image"
    CATEGORY = "MachinePaintingNodes/Rotate/Scale"

    def rotate_image(self, image, mask=None, canvas_width=0, canvas_height=0,
                     background="transparent", rotation_method="free",
                     rotation_angle=0.0, zoom=0.0, offset_x=0.0, offset_y=0.0,
                     unique_id=None):

        img = image[0].cpu().numpy().astype(np.float32)
        src_h, src_w = img.shape[:2]

        # Canvas: 0 means "match the incoming image"
        dst_w = int(canvas_width) if canvas_width > 0 else src_w
        dst_h = int(canvas_height) if canvas_height > 0 else src_h
        dst_shape = (dst_h, dst_w)

        angle = snap_angle(rotation_angle, rotation_method)

        # Fit the source inside the canvas first, then apply zoom on top, so
        # zoom 0 always shows the whole image whatever the canvas size is.
        scale = fit_scale(img.shape, dst_shape) * zoom_to_scale(zoom)

        M = build_matrix(img.shape, dst_shape, angle, scale, offset_x, offset_y)

        warped = warp_image(img, M, dst_shape)
        coverage = coverage_mask(img.shape, M, dst_shape)

        # An incoming mask rides the same matrix so it stays aligned, and it
        # decides what stays visible in the image. Without one, the transformed
        # image extent becomes the mask.
        if mask is not None:
            mask_np = normalize_mask(mask, (src_h, src_w))
            # Multiply by coverage so the mask can never claim area outside the
            # transformed image, even when it is white right to its own edges.
            out_mask = warp_single(mask_np, M, dst_shape) * coverage
        else:
            out_mask = coverage

        # Fill everything that isn't visible. "transparent" is carried by the
        # mask output, since a ComfyUI IMAGE tensor has no alpha channel.
        if background == "white":
            bg = np.ones((dst_h, dst_w, 3), dtype=np.float32)
        else:
            bg = np.zeros((dst_h, dst_w, 3), dtype=np.float32)

        vis_3ch = np.expand_dims(out_mask, axis=-1)
        result = warped * vis_3ch + bg * (1.0 - vis_3ch)
        result = np.clip(result, 0.0, 1.0)

        # Build outputs
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        mask_tensor = torch.from_numpy(out_mask).unsqueeze(0)

        mask_bw = np.stack([out_mask, out_mask, out_mask], axis=2)
        mask_bw_tensor = torch.from_numpy(mask_bw).unsqueeze(0)

        # Preview
        if background == "transparent":
            grid = transparency_grid(result.shape)
            preview = (result * 255.0) * vis_3ch + grid * (1.0 - vis_3ch)
            preview_img = np.clip(preview, 0, 255).astype(np.uint8)
        else:
            preview_img = (result * 255.0).astype(np.uint8)

        preview_results = self._save_preview(preview_img, unique_id)

        return {
            "ui": {"images": preview_results},
            "result": (result_tensor, mask_tensor, mask_bw_tensor)
        }

    def _save_preview(self, img_np, unique_id):
        temp_dir = folder_paths.get_temp_directory()
        filename = f"image_transform_{unique_id}.png"
        filepath = os.path.join(temp_dir, filename)
        img_pil = Image.fromarray(img_np, mode='RGB')
        img_pil.save(filepath)
        return [{"filename": filename, "subfolder": "", "type": "temp"}]
