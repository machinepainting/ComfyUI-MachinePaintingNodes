# boolean_master_switch.py

class BooleanMasterSwitch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "master": ("BOOLEAN", {
                    "default": True,
                    "label_on": "TRUE",  
                    "label_off": "FALSE"  
                }),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("out_1",)
    FUNCTION = "execute"
    CATEGORY = "MachinePainting/Utils"

    OUTPUT_IS_LIST = (True,)
    OUTPUT_MAX_LIST_LENGTH = 25

    def execute(self, master: bool):
        return ([master],)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")