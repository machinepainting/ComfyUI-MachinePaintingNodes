# seed_boolean_lock.py

class SeedBooleanLock:
    """
    Seed Boolean Lock
    • Number appears big and clean directly on the node
    • lock_seed_boolean = true → freezes the current seed value
    """

    def __init__(self):
        self.displayed_seed = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"forceInput": True}), 
                "lock_seed_boolean": ("BOOLEAN", {
                    "default": False,
                    "label_on": "true",
                    "label_off": "false"
                }),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)
    FUNCTION = "run"
    OUTPUT_NODE = True                       
    CATEGORY = "MachinePaintingNodes/utils"

    def run(self, seed, lock_seed_boolean):
        seed = int(seed)

        if not lock_seed_boolean:
            self.displayed_seed = seed
            
        return {
            "ui": {"text": str(self.displayed_seed)},
            "result": (self.displayed_seed,)
        }


NODE_CLASS_MAPPINGS = {"SeedBooleanLock": SeedBooleanLock}
NODE_DISPLAY_NAME_MAPPINGS = {"SeedBooleanLock": "Seed Boolean Lock"}