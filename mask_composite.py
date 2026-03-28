import torch
import numpy as np
import cv2


class _MaskCompositeBase:
    """Base class for Mask Composite Pro variants."""

    MAX_MASKS = 2  # Override in subclasses

    @classmethod
    def INPUT_TYPES(cls):
        n = cls.MAX_MASKS
        select_options = ["all"] + [str(i) for i in range(1, n + 1)]

        inputs = {
            "required": {
                "mask_1": ("MASK",),
                "output_select": (select_options, {"default": "all"}),
                "invert_output": ("BOOLEAN", {"default": False, "label_on": "inverted", "label_off": "normal"}),
            },
            "optional": {}
        }

        for i in range(2, n + 1):
            inputs["optional"][f"mask_{i}"] = ("MASK",)

        for i in range(1, n + 1):
            inputs["optional"][f"blur_mask_{i}"] = ("FLOAT", {
                "default": 0.0,
                "min": 0.0,
                "max": 50.0,
                "step": 0.5,
                "display": "slider",
            })
            inputs["optional"][f"grow_shrink_mask_{i}"] = ("INT", {
                "default": 0,
                "min": -100,
                "max": 100,
                "step": 1,
                "display": "slider",
            })
            inputs["optional"][f"opacity_mask_{i}"] = ("FLOAT", {
                "default": 1.0,
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "display": "slider",
            })

        return inputs

    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "composite"
    CATEGORY = "MachinePaintingNodes/Mask"

    def composite(self, mask_1, output_select="all", invert_output=False, **kwargs):
        n = self.MAX_MASKS

        masks_in = [mask_1] + [kwargs.get(f"mask_{i}") for i in range(2, n + 1)]
        blurs = [kwargs.get(f"blur_mask_{i}", 0.0) for i in range(1, n + 1)]
        grow_shrinks = [kwargs.get(f"grow_shrink_mask_{i}", 0) for i in range(1, n + 1)]
        opacities = [kwargs.get(f"opacity_mask_{i}", 1.0) for i in range(1, n + 1)]

        m1 = self._to_numpy(mask_1)
        h, w = m1.shape[:2]

        processed = []
        for i in range(n):
            if masks_in[i] is None:
                processed.append(None)
                continue
            m = self._to_numpy(masks_in[i])
            if m.shape[:2] != (h, w):
                m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
            m = self._grow_shrink(m, grow_shrinks[i])
            m = self._blur(m, blurs[i])
            m = m * opacities[i]
            m = np.clip(m, 0.0, 1.0)
            processed.append(m)

        if output_select != "all":
            idx = int(output_select) - 1
            if idx < len(processed) and processed[idx] is not None:
                result = processed[idx]
            else:
                result = np.zeros((h, w), dtype=np.float32)
        else:
            result = np.zeros((h, w), dtype=np.float32)
            for m in processed:
                if m is not None:
                    result = 1.0 - (1.0 - result) * (1.0 - m)
            result = np.clip(result, 0.0, 1.0)

        if invert_output:
            result = 1.0 - result

        return (torch.from_numpy(result).unsqueeze(0),)

    def _to_numpy(self, mask_tensor):
        if len(mask_tensor.shape) == 3:
            return mask_tensor[0].cpu().numpy().astype(np.float32)
        return mask_tensor.cpu().numpy().astype(np.float32)

    def _grow_shrink(self, mask, amount):
        if amount == 0:
            return mask
        kernel_size = abs(amount) * 2 + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        mask_u8 = (mask * 255).astype(np.uint8)
        if amount > 0:
            mask_u8 = cv2.dilate(mask_u8, kernel, iterations=1)
        else:
            mask_u8 = cv2.erode(mask_u8, kernel, iterations=1)
        return mask_u8.astype(np.float32) / 255.0

    def _blur(self, mask, radius):
        if radius <= 0:
            return mask
        ksize = max(int(radius * 2) | 1, 3)
        return cv2.GaussianBlur(mask, (ksize, ksize), radius)


class MaskCompositePro2X(_MaskCompositeBase):
    """Combine 2 masks with per-mask blur, grow/shrink, and opacity."""
    MAX_MASKS = 2


class MaskCompositePro6X(_MaskCompositeBase):
    """Combine up to 6 masks with per-mask blur, grow/shrink, and opacity."""
    MAX_MASKS = 6
