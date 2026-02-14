from nodes import EmptyLatentImage


class ZImageEmptyLatentImage:
    """
    Empty Latent Image node with Z-Image recommended resolutions.
    Supports resolutions from 512x512 to 2048x2048 optimized for Z-Image model.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dimensions": (
                    [
                        # Landscape
                        '2048 x 1024  (landscape 2:1)',
                        '1920 x 1080  (landscape 16:9)',
                        '1536 x 1024  (landscape 3:2)',
                        '1344 x 896   (landscape 3:2)',
                        '1280 x 720   (landscape 16:9)',
                        '1216 x 832   (landscape 3:2)',
                        '1152 x 768   (landscape 3:2)',
                        # Square
                        '1024 x 1024  (square)',
                        ' 768 x 768   (square)',
                        ' 512 x 512   (square)',
                        # Portrait
                        ' 768 x 1152  (portrait 2:3)',
                        ' 832 x 1216  (portrait 2:3)',
                        ' 720 x 1280  (portrait 9:16)',
                        ' 896 x 1344  (portrait 2:3)',
                        '1024 x 1536  (portrait 2:3)',
                        '1080 x 1920  (portrait 9:16)',
                        '1024 x 2048  (portrait 1:2)',
                    ],
                    {
                        "default": '1024 x 1024  (square)'
                    }
                ),
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 64
                }),
            },
        }
    
    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("LATENT", "WIDTH", "HEIGHT")
    FUNCTION = "generate"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def generate(self, dimensions, batch_size):
        """Generates the latent and exposes the width and height"""
        result = [x.strip() for x in dimensions.split('x')]
        width = int(result[0])
        height = int(result[1].split(' ')[0].strip())
        
        latent = EmptyLatentImage().generate(width, height, batch_size)[0]
        
        return (latent, width, height)
