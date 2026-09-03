import torch
import numpy as np


class ImageMaskSwitch:
    """
    Converts between IMAGE and MASK types with a boolean toggle.
    Image to Mask: converts RGB image to single-channel grayscale mask.
    Mask to Image: converts single-channel mask to 3-channel RGB image.
    """

    DESCRIPTION = "Convert between IMAGE and MASK with a toggle."

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "switch_mode": ("BOOLEAN", {"default": False, "label_on": "mask_to_image", "label_off": "image_to_mask"}),
            },
            "optional": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("MASK", "IMAGE")
    RETURN_NAMES = ("mask", "image")
    FUNCTION = "switch"
    CATEGORY = "MachinePaintingNodes/Util"

    def switch(self, switch_mode, image=None, mask=None):
        if not switch_mode:
            # Image to Mask
            if image is None:
                # No image input — output blank
                out_mask = torch.zeros(1, 64, 64, dtype=torch.float32)
                out_image = torch.zeros(1, 64, 64, 3, dtype=torch.float32)
                return (out_mask, out_image)

            img = image[0].cpu().numpy().astype(np.float32)
            # Convert to grayscale using Rec. 601 luma
            gray = 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]
            out_mask = torch.from_numpy(gray).unsqueeze(0)
            # Pass through the original image
            return (out_mask, image)
        else:
            # Mask to Image
            if mask is None:
                out_mask = torch.zeros(1, 64, 64, dtype=torch.float32)
                out_image = torch.zeros(1, 64, 64, 3, dtype=torch.float32)
                return (out_mask, out_image)

            if len(mask.shape) == 3:
                mask_np = mask[0].cpu().numpy().astype(np.float32)
            else:
                mask_np = mask.cpu().numpy().astype(np.float32)

            # Convert single channel to 3-channel RGB
            img_3ch = np.stack([mask_np, mask_np, mask_np], axis=-1)
            out_image = torch.from_numpy(img_3ch).unsqueeze(0)
            # Pass through the original mask
            return (mask, out_image)
