import torch
import numpy as np
import cv2
from PIL import Image
import folder_paths
import os


class NoiseGrainPro:
    """
    Realistic film grain / noise generator with control over grain size,
    sharpness, color vs mono, saturation, and blend mode.
    """

    DESCRIPTION = "Film grain and noise with size, sharpness and 6 blend modes."

    BLEND_MODES = ["overlay", "soft_light", "hard_light", "linear_light", "multiply", "screen"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "blend_mode": (cls.BLEND_MODES, {"default": "overlay"}),
            },
            "optional": {
                "amount": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                "size": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.5,
                    "max": 10.0,
                    "step": 0.5,
                    "display": "slider"
                }),
                "sharpness": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                "saturation": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                "monochromatic": ("BOOLEAN", {"default": True, "label_on": "mono", "label_off": "color"}),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                    "step": 1,
                }),
                "mask": ("MASK",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    OUTPUT_NODE = True
    FUNCTION = "apply_grain"
    CATEGORY = "MachinePaintingNodes/Filter"

    def apply_grain(self, image, blend_mode,
                    amount=0.5, size=1.0, sharpness=0.5, saturation=0.0,
                    monochromatic=True, seed=0, mask=None, unique_id=None):

        img = image[0].cpu().numpy().astype(np.float32)
        h, w = img.shape[:2]

        # Generate noise at reduced resolution for grain size control
        grain_h = max(int(h / size), 1)
        grain_w = max(int(w / size), 1)

        rng = np.random.RandomState(seed)

        if monochromatic:
            noise = rng.normal(0.0, 1.0, (grain_h, grain_w)).astype(np.float32)
            noise = np.stack([noise, noise, noise], axis=-1)
        else:
            noise = rng.normal(0.0, 1.0, (grain_h, grain_w, 3)).astype(np.float32)

        # Upscale noise to image size
        if grain_h != h or grain_w != w:
            noise = cv2.resize(noise, (w, h), interpolation=cv2.INTER_LINEAR)

        # Sharpness: 0 = very soft grain, 1 = sharp grain
        # Apply gaussian blur inversely proportional to sharpness
        blur_amount = (1.0 - sharpness) * 4.0 + 0.5
        if blur_amount > 0.6:
            ksize = max(int(blur_amount * 2) | 1, 3)
            noise = cv2.GaussianBlur(noise, (ksize, ksize), blur_amount)

        # Saturation control for color grain
        if not monochromatic and saturation < 1.0:
            gray = noise.mean(axis=-1, keepdims=True)
            noise = gray * (1.0 - saturation) + noise * saturation

        # Normalize noise to [-1, 1] range for consistent blending
        noise_std = noise.std()
        if noise_std > 0:
            noise = noise / (noise_std * 3.0)
        noise = np.clip(noise, -1.0, 1.0)

        # Convert noise to 0-1 centered at 0.5 for blend mode input
        grain = noise * 0.5 + 0.5

        # Apply blend mode
        blended = self._apply_blend(img, grain, blend_mode)

        # Mix original and blended by amount
        result = img * (1.0 - amount) + blended * amount

        # Apply mask
        if mask is not None:
            if len(mask.shape) == 3:
                mask_np = mask[0].cpu().numpy().astype(np.float32)
            else:
                mask_np = mask.cpu().numpy().astype(np.float32)
            if mask_np.shape[:2] != (h, w):
                mask_np = cv2.resize(mask_np, (w, h), interpolation=cv2.INTER_LINEAR)
            mask_3ch = np.expand_dims(mask_np, axis=-1)
            result = img * (1.0 - mask_3ch) + result * mask_3ch

        result = np.clip(result, 0.0, 1.0)

        result_tensor = torch.from_numpy(result).unsqueeze(0)

        # Preview
        preview_img = (result * 255).astype(np.uint8)
        preview_results = self._save_preview(preview_img, unique_id)

        return {
            "ui": {"images": preview_results},
            "result": (result_tensor,)
        }

    def _apply_blend(self, base, grain, mode):
        """Apply blend mode between base image and grain layer."""
        a = base
        b = grain

        if mode == "overlay":
            result = np.where(a < 0.5, 2 * a * b, 1 - 2 * (1 - a) * (1 - b))
        elif mode == "soft_light":
            result = np.where(
                b < 0.5,
                a - (1 - 2 * b) * a * (1 - a),
                a + (2 * b - 1) * (np.where(a <= 0.25, ((16 * a - 12) * a + 4) * a, np.sqrt(a)) - a)
            )
        elif mode == "hard_light":
            result = np.where(b < 0.5, 2 * a * b, 1 - 2 * (1 - a) * (1 - b))
        elif mode == "linear_light":
            result = a + 2 * b - 1
        elif mode == "multiply":
            result = a * b
        elif mode == "screen":
            result = 1 - (1 - a) * (1 - b)
        else:
            result = a

        return np.clip(result, 0.0, 1.0)

    def _save_preview(self, img_np, unique_id):
        temp_dir = folder_paths.get_temp_directory()
        filename = f"noise_grain_{unique_id}.png"
        filepath = os.path.join(temp_dir, filename)
        img_pil = Image.fromarray(img_np, mode='RGB')
        img_pil.save(filepath)
        return [{"filename": filename, "subfolder": "", "type": "temp"}]
