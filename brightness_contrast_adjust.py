# brightness_contrast_adjust.py

from PIL import Image, ImageEnhance
import torch
import numpy as np

def tensor2pil(image):
    return Image.fromarray((image.squeeze(0).cpu().numpy() * 255).astype('uint8'))

def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype('float32') / 255).unsqueeze(0)

def RGB2RGBA(rgb, alpha):
    return Image.merge('RGBA', (*rgb.split(), alpha))

def log(msg, message_type='info'):
    print(f"[MachinePainting] {msg}")

class BrightnessContrastAdjust:
    def __init__(self):
        self.NODE_NAME = 'Brightness Contrast Adjust'

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "brightness": ("FLOAT", {"default": 1, "min": 0.0, "max": 3, "step": 0.01}),
                "contrast": ("FLOAT", {"default": 1, "min": 0.0, "max": 3, "step": 0.01}),
                "saturation": ("FLOAT", {"default": 1, "min": 0.0, "max": 3, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "adjust"
    CATEGORY = 'MachinePainting'

    def adjust(self, image, brightness, contrast, saturation):
        ret_images = []
        for i in image:
            i = torch.unsqueeze(i, 0)
            img = tensor2pil(i).convert('RGB')
            if brightness != 1:
                img = ImageEnhance.Brightness(img).enhance(brightness)
            if contrast != 1:
                img = ImageEnhance.Contrast(img).enhance(contrast)
            if saturation != 1:
                img = ImageEnhance.Color(img).enhance(saturation)
            orig = tensor2pil(i)
            if orig.mode == 'RGBA':
                img = RGB2RGBA(img, orig.split()[-1])
            ret_images.append(pil2tensor(img))
        log(f"{self.NODE_NAME} Processed {len(ret_images)} image(s).", 'finish')
        return (torch.cat(ret_images, dim=0),)