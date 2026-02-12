class SeedLock:
    """
    Lock/unlock seed value with a toggle.
    When locked, outputs the locked_seed value.
    When unlocked, outputs the input seed value.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "locked_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "lock": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)
    FUNCTION = "execute"
    CATEGORY = "MachinePaintingNodes/Util"

    def execute(self, seed, locked_seed, lock):
        if lock:
            return (locked_seed,)
        return (seed,)
