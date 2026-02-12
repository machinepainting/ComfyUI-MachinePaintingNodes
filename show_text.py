class ShowText:
    """
    Display text output from other nodes.
    Useful for debugging and viewing string outputs in your workflow.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "show_text"
    CATEGORY = "MachinePaintingNodes/Util"
    OUTPUT_NODE = True

    def show_text(self, text):
        # Pass through the text and display it
        print(f"[ShowText] {text}")
        return (text,)
