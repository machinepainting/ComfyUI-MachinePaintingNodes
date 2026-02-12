class TextNotes:
    """
    Simple text notes node for adding comments and documentation to your workflow.
    Does not affect the pipeline - just for organization.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "notes": ("STRING", {
                    "default": "Add your notes here...",
                    "multiline": True,
                }),
            },
            "optional": {
                "title": ("STRING", {"default": "Notes"}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "do_nothing"
    CATEGORY = "MachinePaintingNodes/Util"
    OUTPUT_NODE = True

    def do_nothing(self, notes, title="Notes"):
        # This node does nothing - it's just for notes
        return ()
