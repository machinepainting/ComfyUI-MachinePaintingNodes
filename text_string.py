class TextString:
    """
    Provide a text string to your workflow.
    Simple text input node for passing strings to other nodes.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "output_text"
    CATEGORY = "MachinePaintingNodes/Util"
    
    def output_text(self, text):
        return (text,)
