class MegaSliderMasterValue:
    """
    Master settings for Mega Sliders.
    Connect to Mega Slider nodes to control min/max/step for all sliders.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "min_value": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "max_value": ("FLOAT", {"default": 1.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "step": ("FLOAT", {"default": 0.01, "min": 0.001, "max": 1000.0, "step": 0.01}),
            }
        }
    
    RETURN_TYPES = ("MEGA_SLIDER_MASTER",)
    RETURN_NAMES = ("master",)
    FUNCTION = "output_settings"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_settings(self, min_value, max_value, step):
        return ({"min": min_value, "max": max_value, "step": step},)


class MegaSliderX1:
    """
    Single universal slider with float/int output toggle.
    Connect Mega Slider Master Value for settings, or use right-click > Properties for overrides.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_int": ("BOOLEAN", {"default": False}),
                "slider_1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
            },
            "optional": {
                "master": ("MEGA_SLIDER_MASTER",),
            }
        }
    
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "output_values"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_values(self, output_int, slider_1, master=None):
        value = slider_1
        
        if master:
            min_val = master["min"]
            max_val = master["max"]
            step_val = master["step"]
            
            def round_to_step(val, step_size):
                return round(val / step_size) * step_size
            
            value = max(min_val, min(max_val, round_to_step(value, step_val)))
        
        if output_int:
            value = int(value)
        
        return (value,)


class MegaSliderX3:
    """
    3 universal sliders with float/int output toggle.
    Connect Mega Slider Master Value for settings, or use right-click > Properties for per-slider overrides.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_int": ("BOOLEAN", {"default": False}),
                "slider_1": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_2": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
                "slider_3": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.01, "display": "slider"}),
            },
            "optional": {
                "master": ("MEGA_SLIDER_MASTER",),
            }
        }
    
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("value_1", "value_2", "value_3")
    FUNCTION = "output_values"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_values(self, output_int, slider_1, slider_2, slider_3, master=None):
        values = [slider_1, slider_2, slider_3]
        
        if master:
            min_val = master["min"]
            max_val = master["max"]
            step_val = master["step"]
            
            def round_to_step(val, step_size):
                return round(val / step_size) * step_size
            
            values = [max(min_val, min(max_val, round_to_step(v, step_val))) for v in values]
        
        if output_int:
            values = [int(v) for v in values]
        
        return tuple(values)


class MegaSliderX6:
    """
    6 universal sliders with float/int output toggle.
    Connect Mega Slider Master Value for settings, or use right-click > Properties for per-slider overrides.
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
            },
            "optional": {
                "master": ("MEGA_SLIDER_MASTER",),
            }
        }
    
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("value_1", "value_2", "value_3", "value_4", "value_5", "value_6")
    FUNCTION = "output_values"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_values(self, output_int, slider_1, slider_2, slider_3, slider_4, slider_5, slider_6, master=None):
        values = [slider_1, slider_2, slider_3, slider_4, slider_5, slider_6]
        
        if master:
            min_val = master["min"]
            max_val = master["max"]
            step_val = master["step"]
            
            def round_to_step(val, step_size):
                return round(val / step_size) * step_size
            
            values = [max(min_val, min(max_val, round_to_step(v, step_val))) for v in values]
        
        if output_int:
            values = [int(v) for v in values]
        
        return tuple(values)


class MegaSliderX12:
    """
    12 universal sliders with float/int output toggle.
    Connect Mega Slider Master Value for settings, or use right-click > Properties for per-slider overrides.
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
            },
            "optional": {
                "master": ("MEGA_SLIDER_MASTER",),
            }
        }
    
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", 
                    "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("value_1", "value_2", "value_3", "value_4", "value_5", "value_6",
                    "value_7", "value_8", "value_9", "value_10", "value_11", "value_12")
    FUNCTION = "output_values"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_values(self, output_int, slider_1, slider_2, slider_3, slider_4, slider_5, slider_6,
                      slider_7, slider_8, slider_9, slider_10, slider_11, slider_12, master=None):
        values = [slider_1, slider_2, slider_3, slider_4, slider_5, slider_6,
                  slider_7, slider_8, slider_9, slider_10, slider_11, slider_12]
        
        if master:
            min_val = master["min"]
            max_val = master["max"]
            step_val = master["step"]
            
            def round_to_step(val, step_size):
                return round(val / step_size) * step_size
            
            values = [max(min_val, min(max_val, round_to_step(v, step_val))) for v in values]
        
        if output_int:
            values = [int(v) for v in values]
        
        return tuple(values)
