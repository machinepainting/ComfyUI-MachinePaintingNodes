import torch
import numpy as np
from PIL import Image
import folder_paths
import os
import cv2

class ChannelMaskPro:
    """
    Separates RGB and Alpha channels into individual black and white outputs.
    Each channel is output as both an IMAGE (3-channel B&W) and MASK (single channel).
    Includes contrast/levels adjustments applied to all outputs.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # Mask input
                "mask": ("MASK",),
                "invert_input_mask": ("BOOLEAN", {"default": False}),
                # Levels adjustments
                "black_point": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.5, "step": 0.01, "display": "slider"}),
                "white_point": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 1.0, "step": 0.01, "display": "slider"}),
                "gamma": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.05, "display": "slider"}),
                # Contrast
                "contrast": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                "brightness": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "display": "slider"}),
                # Invert channel output
                "invert_channel_mask": ("BOOLEAN", {"default": False}),
                # Preview
                "preview_channel": (["all", "red", "green", "blue", "alpha"], {"default": "all"}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("MASK", "MASK", "MASK", "MASK")
    RETURN_NAMES = ("red_mask", "green_mask", "blue_mask", "alpha_mask")
    OUTPUT_NODE = True
    FUNCTION = "separate_channels"
    CATEGORY = "MachinePaintingNodes/Mask"

    def apply_levels(self, channel, black_point, white_point, gamma):
        """Apply levels adjustment to a channel."""
        # Normalize to black/white points
        result = (channel - black_point) / (white_point - black_point)
        result = np.clip(result, 0, 1)
        # Apply gamma
        result = np.power(result, 1.0 / gamma)
        return result

    def apply_contrast_brightness(self, channel, contrast, brightness):
        """Apply contrast and brightness to a channel."""
        # Contrast: -100 to 100 -> 0.5 to 1.5 multiplier
        contrast_factor = 1.0 + (contrast / 100.0)
        # Apply contrast around midpoint
        result = (channel - 0.5) * contrast_factor + 0.5
        # Apply brightness
        brightness_factor = brightness / 100.0
        result = result + brightness_factor
        return np.clip(result, 0, 1)

    def process_channel(self, channel, black_point, white_point, gamma, contrast, brightness, invert):
        """Apply all adjustments to a channel."""
        result = channel.copy()
        
        # Apply levels
        if black_point > 0 or white_point < 1 or gamma != 1.0:
            result = self.apply_levels(result, black_point, white_point, gamma)
        
        # Apply contrast/brightness
        if contrast != 0 or brightness != 0:
            result = self.apply_contrast_brightness(result, contrast, brightness)
        
        # Invert
        if invert:
            result = 1.0 - result
        
        return result.astype(np.float32)

    def separate_channels(self, image, mask=None, invert_input_mask=False,
                          black_point=0.0, white_point=1.0, gamma=1.0,
                          contrast=0.0, brightness=0.0, invert_channel_mask=False,
                          preview_channel="all", unique_id=None):
        img = image[0].cpu().numpy()
        h, w = img.shape[:2]
        
        # Handle input mask
        if mask is not None:
            if len(mask.shape) == 3:
                input_mask = mask[0].cpu().numpy()
            else:
                input_mask = mask.cpu().numpy()
            
            # Resize mask if needed
            if input_mask.shape[:2] != (h, w):
                input_mask = cv2.resize(input_mask, (w, h), interpolation=cv2.INTER_LINEAR)
            
            # Invert input mask if requested
            if invert_input_mask:
                input_mask = 1.0 - input_mask
        else:
            input_mask = None
        
        # Extract RGB channels
        red = img[:, :, 0].astype(np.float32)
        green = img[:, :, 1].astype(np.float32)
        blue = img[:, :, 2].astype(np.float32)
        
        # Check for alpha channel (if 4 channels)
        if img.shape[2] == 4:
            alpha = img[:, :, 3].astype(np.float32)
        else:
            alpha = np.ones((h, w), dtype=np.float32)
        
        # Apply adjustments to each channel
        red = self.process_channel(red, black_point, white_point, gamma, contrast, brightness, invert_channel_mask)
        green = self.process_channel(green, black_point, white_point, gamma, contrast, brightness, invert_channel_mask)
        blue = self.process_channel(blue, black_point, white_point, gamma, contrast, brightness, invert_channel_mask)
        alpha = self.process_channel(alpha, black_point, white_point, gamma, contrast, brightness, invert_channel_mask)
        
        # Apply input mask to all channel outputs if provided
        if input_mask is not None:
            red = red * input_mask
            green = green * input_mask
            blue = blue * input_mask
            alpha = alpha * input_mask
        
        # Masks (single channel)
        red_mask = torch.from_numpy(red).unsqueeze(0)
        green_mask = torch.from_numpy(green).unsqueeze(0)
        blue_mask = torch.from_numpy(blue).unsqueeze(0)
        alpha_mask = torch.from_numpy(alpha).unsqueeze(0)
        
        # Create preview image
        preview_img = self.create_preview(red, green, blue, alpha, preview_channel)
        preview_results = self.save_preview(preview_img, unique_id)
        
        return {
            "ui": {"images": preview_results},
            "result": (red_mask, green_mask, blue_mask, alpha_mask)
        }

    def create_preview(self, red, green, blue, alpha, mode):
        """Create preview showing channel(s) as black and white."""
        h, w = red.shape
        
        if mode == "all":
            # Create 2x2 grid of all channels as B&W
            max_size = 256
            if h > max_size or w > max_size:
                scale = max_size / max(h, w)
                preview_h = int(h * scale)
                preview_w = int(w * scale)
            else:
                preview_h, preview_w = h, w
            
            grid_h = preview_h * 2 + 4
            grid_w = preview_w * 2 + 4
            preview = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)
            
            def resize_channel(ch):
                ch_uint8 = (ch * 255).astype(np.uint8)
                pil_img = Image.fromarray(ch_uint8, mode='L')
                pil_img = pil_img.resize((preview_w, preview_h), Image.LANCZOS)
                return np.array(pil_img)
            
            red_small = resize_channel(red)
            green_small = resize_channel(green)
            blue_small = resize_channel(blue)
            alpha_small = resize_channel(alpha)
            
            # Red channel (top-left) - B&W
            preview[0:preview_h, 0:preview_w, 0] = red_small
            preview[0:preview_h, 0:preview_w, 1] = red_small
            preview[0:preview_h, 0:preview_w, 2] = red_small
            
            # Green channel (top-right) - B&W
            preview[0:preview_h, preview_w+4:preview_w*2+4, 0] = green_small
            preview[0:preview_h, preview_w+4:preview_w*2+4, 1] = green_small
            preview[0:preview_h, preview_w+4:preview_w*2+4, 2] = green_small
            
            # Blue channel (bottom-left) - B&W
            preview[preview_h+4:preview_h*2+4, 0:preview_w, 0] = blue_small
            preview[preview_h+4:preview_h*2+4, 0:preview_w, 1] = blue_small
            preview[preview_h+4:preview_h*2+4, 0:preview_w, 2] = blue_small
            
            # Alpha/Combined channel (bottom-right) - B&W grayscale of combined RGB
            # Show luminance of all channels combined
            combined = (red * 0.299 + green * 0.587 + blue * 0.114)
            combined_small = resize_channel(combined)
            preview[preview_h+4:preview_h*2+4, preview_w+4:preview_w*2+4, 0] = combined_small
            preview[preview_h+4:preview_h*2+4, preview_w+4:preview_w*2+4, 1] = combined_small
            preview[preview_h+4:preview_h*2+4, preview_w+4:preview_w*2+4, 2] = combined_small
            
            # Add labels (colored to match channel)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(preview, "R", (5, 20), font, 0.6, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(preview, "G", (preview_w + 9, 20), font, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(preview, "B", (5, preview_h + 24), font, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(preview, "L", (preview_w + 9, preview_h + 24), font, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
            
        else:
            # Single channel preview
            channel_map = {"red": red, "green": green, "blue": blue, "alpha": alpha}
            ch = channel_map.get(mode, red)
            preview = (np.stack([ch, ch, ch], axis=2) * 255).astype(np.uint8)
        
        return preview

    def save_preview(self, img_np, unique_id):
        temp_dir = folder_paths.get_temp_directory()
        filename = f"channel_mask_{unique_id}.png"
        filepath = os.path.join(temp_dir, filename)
        img_pil = Image.fromarray(img_np)
        img_pil.save(filepath)
        return [{"filename": filename, "subfolder": "", "type": "temp"}]
