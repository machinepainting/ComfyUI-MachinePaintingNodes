# boolean.py

class Boolean:
    """
    Simple standalone Boolean toggle
    MachinePaintingNodes – clean and minimal
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": ("BOOLEAN", {
                    "default": True,
                    "label_on": "TRUE",
                    "label_off": "FALSE"
                }),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("boolean",)
    FUNCTION = "execute"
    CATEGORY = "MachinePainting/Utils"

    def execute(self, boolean=True):
        return (boolean,)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")