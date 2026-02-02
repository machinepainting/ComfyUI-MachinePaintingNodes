# boolean_utils.py
# Combined boolean utility nodes for MachinePaintingNodes

import random


class Boolean:
    """
    Simple standalone Boolean toggle
    MachinePaintingNodes - For use with boolean toggle inputs on nodes. 
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": ("BOOLEAN", {
                    "default": True,
                    "label_on": "true",
                    "label_off": "false"
                }),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("boolean",)
    FUNCTION = "execute"
    CATEGORY = "MachinePaintingNodes"

    def execute(self, boolean=True):
        return (boolean,)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")


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
    CATEGORY = "MachinePaintingNodes"

    def switch(self, true_value=1.00, false_value=0.00, boolean=None):
        value = boolean if boolean is not None else True
        result = true_value if value else false_value
        return (int(result), float(result))


class BooleanInputValueSwitch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "FLOAT_input": ("FLOAT", {
                    "forceInput": True,
                }),
                "true_min": ("FLOAT", {
                    "default": 0.51,
                    "min": -9999.0,
                    "max": 9999.0,
                    "step": 0.01,
                    "display": "number"
                }),
                "true_max": ("FLOAT", {
                    "default": 1.00,
                    "min": -9999.0,
                    "max": 9999.0,
                    "step": 0.01,
                    "display": "number"
                }),
                "false_min": ("FLOAT", {
                    "default": 0.00,
                    "min": -9999.0,
                    "max": 9999.0,
                    "step": 0.01,
                    "display": "number"
                }),
                "false_max": ("FLOAT", {
                    "default": 0.50,
                    "min": -9999.0,
                    "max": 9999.0,
                    "step": 0.01,
                    "display": "number"
                }),
                "overlap_behavior": ([
                    "randomize",
                    "force_true",
                    "force_false"
                ], {
                    "default": "randomize",
                    "tooltip": "What to do when value falls in both ranges"
                }),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("boolean",)
    FUNCTION = "evaluate"
    CATEGORY = "MachinePaintingNodes"

    @classmethod
    def IS_CHANGED(cls, FLOAT_input, true_min, true_max, false_min, false_max, overlap_behavior, **kwargs):
        if overlap_behavior == "randomize":
            return float("nan")
        return float("inf")

    def evaluate(self, FLOAT_input,
                 true_min=0.51, true_max=1.00,
                 false_min=0.00, false_max=0.50,
                 overlap_behavior="randomize"):

        value = FLOAT_input

        in_true = true_min <= value <= true_max
        in_false = false_min <= value <= false_max

        if in_true and in_false:
            if overlap_behavior == "randomize":
                return (random.choice([True, False]),)
            elif overlap_behavior == "force_true":
                return (True,)
            else:
                return (False,)
        elif in_true:
            return (True,)
        elif in_false:
            return (False,)
        else:
            return (False,)


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
    CATEGORY = "MachinePaintingNodes"

    OUTPUT_IS_LIST = (True,)
    OUTPUT_MAX_LIST_LENGTH = 25

    def execute(self, master: bool):
        return ([master],)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")
