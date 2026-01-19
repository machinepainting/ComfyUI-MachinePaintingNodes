# boolean_switch_value_output.py

class BooleanSwitchValueOutput:    
    TITLE = "Boolean Switch Value - (INT/FLOAT)"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "true_value": ("FLOAT", {
                    "default": 1.00,
                    "min": -9999.0,
                    "max": 9999.0,
                    "step": 0.01,
                    "display": "number"
                }),
                "false_value": ("FLOAT", {
                    "default": 0.00,
                    "min": -9999.0,
                    "max": 9999.0,
                    "step": 0.01,
                    "display": "number"
                }),
            },
            "optional": {
                "boolean": ("BOOLEAN", {"label": "boolean"}),
            }
        }

    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("INT", "FLOAT")
    FUNCTION = "switch"
    CATEGORY = "MachinePainting/Utils"

    def switch(self, true_value=1.00, false_value=0.00, boolean=None):
        value = boolean if boolean is not None else True
        result = true_value if value else false_value
        return (int(result), float(result))