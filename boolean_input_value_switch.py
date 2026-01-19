# boolean_input_value_switch.py

import random

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
    CATEGORY = "MachinePainting/Utils"

    # This forces the node to re-run every time when randomize is selected
    @classmethod
    def IS_CHANGED(cls, FLOAT_input, true_min, true_max, false_min, false_max, overlap_behavior, **kwargs):
        if overlap_behavior == "randomize":
            return float("nan")   # forces re-execution every single time
        return float("inf")       # normal caching when not randomizing

    def evaluate(self, FLOAT_input,
                 true_min=0.51, true_max=1.00,
                 false_min=0.00, false_max=0.50,
                 overlap_behavior="randomize"):

        value = FLOAT_input

        in_true  = true_min  <= value <= true_max
        in_false = false_min <= value <= false_max

        if in_true and in_false:
            if overlap_behavior == "randomize":
                return (random.choice([True, False]),)
            elif overlap_behavior == "force_true":
                return (True,)
            else:  # force_false
                return (False,)
        elif in_true:
            return (True,)
        elif in_false:
            return (False,)
        else:
            return (False,)