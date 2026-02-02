class Boolean:
    """
    Simple boolean value output.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "execute"
    CATEGORY = "MachinePaintingNodes"

    def execute(self, value):
        return (value,)


class BooleanInvert:
    """
    Inverts a boolean value. True becomes False, False becomes True.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("inverted",)
    FUNCTION = "invert"
    CATEGORY = "MachinePaintingNodes"

    def invert(self, value):
        return (not value,)


class BooleanSwitchValueOutput:
    """
    Output different values based on boolean input.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": ("BOOLEAN", {"default": False}),
                "value_if_true": ("FLOAT", {"default": 1.0, "min": -1000.0, "max": 1000.0, "step": 0.01}),
                "value_if_false": ("FLOAT", {"default": 0.0, "min": -1000.0, "max": 1000.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("float_value", "int_value")
    FUNCTION = "switch"
    CATEGORY = "MachinePaintingNodes"

    def switch(self, boolean, value_if_true, value_if_false):
        result = value_if_true if boolean else value_if_false
        return (result, int(result))


class BooleanInputValueSwitch:
    """
    Route different inputs based on boolean.
    Supports multiple input types.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "image_if_true": ("IMAGE",),
                "image_if_false": ("IMAGE",),
                "mask_if_true": ("MASK",),
                "mask_if_false": ("MASK",),
                "latent_if_true": ("LATENT",),
                "latent_if_false": ("LATENT",),
                "float_if_true": ("FLOAT", {"default": 1.0, "min": -1000.0, "max": 1000.0, "step": 0.01}),
                "float_if_false": ("FLOAT", {"default": 0.0, "min": -1000.0, "max": 1000.0, "step": 0.01}),
                "int_if_true": ("INT", {"default": 1, "min": -1000, "max": 1000, "step": 1}),
                "int_if_false": ("INT", {"default": 0, "min": -1000, "max": 1000, "step": 1}),
                "string_if_true": ("STRING", {"default": "", "multiline": True}),
                "string_if_false": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "LATENT", "FLOAT", "INT", "STRING")
    RETURN_NAMES = ("image", "mask", "latent", "float", "int", "string")
    FUNCTION = "switch"
    CATEGORY = "MachinePaintingNodes"

    def switch(self, boolean, 
               image_if_true=None, image_if_false=None,
               mask_if_true=None, mask_if_false=None,
               latent_if_true=None, latent_if_false=None,
               float_if_true=1.0, float_if_false=0.0,
               int_if_true=1, int_if_false=0,
               string_if_true="", string_if_false=""):
        
        image = image_if_true if boolean else image_if_false
        mask = mask_if_true if boolean else mask_if_false
        latent = latent_if_true if boolean else latent_if_false
        float_val = float_if_true if boolean else float_if_false
        int_val = int_if_true if boolean else int_if_false
        string_val = string_if_true if boolean else string_if_false
        
        return (image, mask, latent, float_val, int_val, string_val)


class BooleanMasterSwitch:
    """
    Master control for multiple boolean outputs.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "master": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("out_1", "out_2", "out_3", "out_4")
    FUNCTION = "switch"
    CATEGORY = "MachinePaintingNodes"

    def switch(self, master):
        return (master, master, master, master)
