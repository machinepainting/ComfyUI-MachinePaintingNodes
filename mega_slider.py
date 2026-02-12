class MegaSliderX1:
    """
    Single universal slider with float/int output toggle.
    Use right-click > Properties to set slider_1_min, slider_1_max, slider_1_step.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_int": ("BOOLEAN", {"default": False}),
                "slider_1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
            }
        }
    
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "output_values"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_values(self, output_int, slider_1):
        value = slider_1
        if output_int:
            value = int(value)
        return (value,)


class MegaSliderX3:
    """
    3 universal sliders with float/int output toggle.
    Use right-click > Properties to set per-slider min/max/step.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_int": ("BOOLEAN", {"default": False}),
                "slider_1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_2": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_3": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
            }
        }
    
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("value_1", "value_2", "value_3")
    FUNCTION = "output_values"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_values(self, output_int, slider_1, slider_2, slider_3):
        values = [slider_1, slider_2, slider_3]
        if output_int:
            values = [int(v) for v in values]
        return tuple(values)


class MegaSliderX6:
    """
    6 universal sliders with float/int output toggle.
    Use right-click > Properties to set per-slider min/max/step.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_int": ("BOOLEAN", {"default": False}),
                "slider_1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_2": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_3": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_4": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_5": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_6": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
            }
        }
    
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("value_1", "value_2", "value_3", "value_4", "value_5", "value_6")
    FUNCTION = "output_values"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_values(self, output_int, slider_1, slider_2, slider_3, slider_4, slider_5, slider_6):
        values = [slider_1, slider_2, slider_3, slider_4, slider_5, slider_6]
        if output_int:
            values = [int(v) for v in values]
        return tuple(values)


class MegaSliderX12:
    """
    12 universal sliders with float/int output toggle.
    Use right-click > Properties to set per-slider min/max/step.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_int": ("BOOLEAN", {"default": False}),
                "slider_1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_2": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_3": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_4": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_5": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_6": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_7": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_8": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_9": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_10": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_11": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_12": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
            }
        }
    
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", 
                    "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("value_1", "value_2", "value_3", "value_4", "value_5", "value_6",
                    "value_7", "value_8", "value_9", "value_10", "value_11", "value_12")
    FUNCTION = "output_values"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_values(self, output_int, slider_1, slider_2, slider_3, slider_4, slider_5, slider_6,
                      slider_7, slider_8, slider_9, slider_10, slider_11, slider_12):
        values = [slider_1, slider_2, slider_3, slider_4, slider_5, slider_6,
                  slider_7, slider_8, slider_9, slider_10, slider_11, slider_12]
        if output_int:
            values = [int(v) for v in values]
        return tuple(values)
