import random
import time

class DynamicValueRange:
    """
    Automatically cycles through a range of values on each run.
    Use to create diversity in settings across multiple generations.
    """
    
    # Class variable to track current values per node instance
    _state = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "min_value": ("FLOAT", {"default": 0.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "max_value": ("FLOAT", {"default": 1.0, "min": -10000.0, "max": 10000.0, "step": 0.1}),
                "step": ("FLOAT", {"default": 0.1, "min": 0.001, "max": 1000.0, "step": 0.01}),
                "mode": (["increment", "decrement", "random"], {"default": "increment"}),
                "on_cycle_complete": (["reverse", "jump"], {"default": "reverse"}),
                "output_int": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }
    
    RETURN_TYPES = ("FLOAT", "INT", "STRING")
    RETURN_NAMES = ("value", "value_int", "value_str")
    FUNCTION = "get_value"
    CATEGORY = "MachinePaintingNodes/Util"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always return a different value to force re-execution
        return float("nan")
    
    def get_value(self, min_value, max_value, step, mode, on_cycle_complete, output_int, unique_id=None):
        # Use unique_id to track state per node instance
        node_id = str(unique_id) if unique_id else "default"
        
        # Initialize state if not exists
        if node_id not in DynamicValueRange._state:
            DynamicValueRange._state[node_id] = {
                "current": min_value,
                "direction": 1,  # 1 = forward, -1 = backward
            }
        
        state = DynamicValueRange._state[node_id]
        
        # Handle random mode
        if mode == "random":
            # Calculate number of steps
            num_steps = int((max_value - min_value) / step) + 1
            random_step = random.randint(0, num_steps - 1)
            value = min_value + (random_step * step)
            value = min(max_value, max(min_value, value))
        else:
            # Get current value
            value = state["current"]
            
            # Ensure value is within range (in case settings changed)
            value = min(max_value, max(min_value, value))
            
            # Calculate next value for next run
            if mode == "increment":
                direction = state.get("direction", 1)
            else:  # decrement
                direction = state.get("direction", -1)
                if state.get("direction") is None or state.get("direction") == 1:
                    state["direction"] = -1
                    direction = -1
            
            next_value = value + (step * direction)
            
            # Check if we've hit the bounds
            if next_value > max_value:
                if on_cycle_complete == "reverse":
                    state["direction"] = -1
                    next_value = value - step
                else:  # jump
                    next_value = min_value
            elif next_value < min_value:
                if on_cycle_complete == "reverse":
                    state["direction"] = 1
                    next_value = value + step
                else:  # jump
                    next_value = max_value
            
            # Clamp next value
            next_value = min(max_value, max(min_value, next_value))
            
            # Store for next run
            state["current"] = next_value
        
        # Round to avoid floating point errors
        value = round(value, 6)
        
        # Convert outputs
        value_int = int(round(value))
        value_str = str(value_int if output_int else value)
        
        if output_int:
            value = float(value_int)
        
        return (value, value_int, value_str)
