import json

# Custom any type that accepts any input
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")

class ShowValue:
    """Display any data type in the node."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source": (any_type, {}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }
    
    INPUT_IS_LIST = True
    RETURN_TYPES = ()
    FUNCTION = "main"
    OUTPUT_NODE = True
    CATEGORY = "MachinePaintingNodes/Util"
    
    def main(self, source=None, unique_id=None, extra_pnginfo=None):
        value = 'None'
        
        # Handle list input
        if isinstance(source, list) and len(source) > 0:
            source = source[0]
        
        if isinstance(source, str):
            value = source
        elif isinstance(source, (int, float, bool)):
            value = str(source)
        elif source is not None:
            try:
                value = json.dumps(source)
            except Exception:
                try:
                    value = str(source)
                except Exception:
                    value = 'source exists, but could not be serialized.'
        
        # Make it a list like ShowText does
        text = [value]
        
        if unique_id is not None and extra_pnginfo is not None:
            if isinstance(extra_pnginfo, list) and len(extra_pnginfo) > 0:
                if isinstance(extra_pnginfo[0], dict) and "workflow" in extra_pnginfo[0]:
                    workflow = extra_pnginfo[0]["workflow"]
                    uid = unique_id[0] if isinstance(unique_id, list) else unique_id
                    node = next(
                        (x for x in workflow["nodes"] if str(x["id"]) == str(uid)),
                        None,
                    )
                    if node:
                        node["widgets_values"] = text
        
        return {"ui": {"text": text}}
