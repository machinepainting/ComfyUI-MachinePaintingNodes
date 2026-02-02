import torch
import numpy as np
import os
import shutil
import folder_paths

class LUTApply:
    """
    Apply LUT (Look-Up Table) color grading files to images.
    Supports .cube and .3dl formats.
    LUT files should be placed in ComfyUI/input/luts/
    Bundled LUTs are automatically copied on first use.
    """
    
    LUT_FOLDER = os.path.join(folder_paths.get_input_directory(), "luts")
    BUNDLED_LUTS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "luts")
    
    @classmethod
    def INPUT_TYPES(cls):
        # Create luts folder if it doesn't exist
        if not os.path.exists(cls.LUT_FOLDER):
            os.makedirs(cls.LUT_FOLDER)
            print(f"[MachinePaintingNodes] Created LUT folder: {cls.LUT_FOLDER}")
        
        # Copy bundled LUTs if they exist and haven't been copied yet
        if os.path.exists(cls.BUNDLED_LUTS):
            for f in os.listdir(cls.BUNDLED_LUTS):
                if f.lower().endswith(('.cube', '.3dl')):
                    src = os.path.join(cls.BUNDLED_LUTS, f)
                    dst = os.path.join(cls.LUT_FOLDER, f)
                    if not os.path.exists(dst):
                        try:
                            shutil.copy2(src, dst)
                            print(f"[MachinePaintingNodes] Installed LUT: {f}")
                        except Exception as e:
                            print(f"[MachinePaintingNodes] Failed to copy LUT {f}: {e}")
        
        # Scan for LUT files
        lut_files = ["none"]
        if os.path.exists(cls.LUT_FOLDER):
            for f in os.listdir(cls.LUT_FOLDER):
                if f.lower().endswith(('.cube', '.3dl')):
                    lut_files.append(f)
        
        lut_files.sort()
        
        return {
            "required": {
                "image": ("IMAGE",),
                "lut_file": (lut_files, {"default": "none"}),
            },
            "optional": {
                "intensity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05, "display": "slider"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "apply_lut"
    CATEGORY = "MachinePaintingNodes"

    def apply_lut(self, image, lut_file, intensity=1.0):
        if lut_file == "none":
            return (image,)
        
        lut_path = os.path.join(self.LUT_FOLDER, lut_file)
        
        if not os.path.exists(lut_path):
            print(f"LUT file not found: {lut_path}")
            return (image,)
        
        # Load LUT
        if lut_file.lower().endswith('.cube'):
            lut, lut_size = self.load_cube(lut_path)
        elif lut_file.lower().endswith('.3dl'):
            lut, lut_size = self.load_3dl(lut_path)
        else:
            return (image,)
        
        if lut is None:
            return (image,)
        
        # Apply LUT to image
        img = image[0].cpu().numpy()
        original = img.copy()
        
        result = self.apply_3d_lut(img, lut, lut_size)
        
        # Blend with intensity
        if intensity < 1.0:
            result = original * (1 - intensity) + result * intensity
        
        result = np.clip(result, 0, 1).astype(np.float32)
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        
        return (result_tensor,)

    def load_cube(self, filepath):
        """Load a .cube LUT file."""
        try:
            lut_size = 0
            lut_data = []
            
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse LUT size
                    if line.startswith('LUT_3D_SIZE'):
                        lut_size = int(line.split()[-1])
                        continue
                    
                    # Skip other metadata
                    if line.startswith(('TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX', 'LUT_1D_SIZE')):
                        continue
                    
                    # Parse color values
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
                            lut_data.append([r, g, b])
                        except ValueError:
                            continue
            
            if lut_size == 0 or len(lut_data) == 0:
                print(f"Invalid .cube file: {filepath}")
                return None, 0
            
            # Reshape to 3D LUT
            lut = np.array(lut_data, dtype=np.float32).reshape((lut_size, lut_size, lut_size, 3))
            
            return lut, lut_size
            
        except Exception as e:
            print(f"Error loading .cube file: {e}")
            return None, 0

    def load_3dl(self, filepath):
        """Load a .3dl LUT file."""
        try:
            lut_data = []
            
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            # Find data start (skip headers)
            data_start = 0
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            float(parts[0])
                            data_start = i
                            break
                        except ValueError:
                            continue
            
            # Parse data
            for line in lines[data_start:]:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
                        # .3dl typically uses 0-4095 or 0-1023 range
                        max_val = max(r, g, b)
                        if max_val > 1:
                            if max_val > 1023:
                                r, g, b = r / 4095, g / 4095, b / 4095
                            else:
                                r, g, b = r / 1023, g / 1023, b / 1023
                        lut_data.append([r, g, b])
                    except ValueError:
                        continue
            
            if len(lut_data) == 0:
                return None, 0
            
            # Determine LUT size (cube root of data length)
            lut_size = int(round(len(lut_data) ** (1/3)))
            
            if lut_size ** 3 != len(lut_data):
                print(f"Invalid .3dl file size: {len(lut_data)} entries")
                return None, 0
            
            lut = np.array(lut_data, dtype=np.float32).reshape((lut_size, lut_size, lut_size, 3))
            
            return lut, lut_size
            
        except Exception as e:
            print(f"Error loading .3dl file: {e}")
            return None, 0

    def apply_3d_lut(self, image, lut, lut_size):
        """Apply 3D LUT to image using trilinear interpolation."""
        h, w, c = image.shape
        
        # Scale image values to LUT indices
        img_scaled = image * (lut_size - 1)
        
        # Get integer and fractional parts
        img_floor = np.floor(img_scaled).astype(np.int32)
        img_ceil = np.ceil(img_scaled).astype(np.int32)
        frac = img_scaled - img_floor
        
        # Clamp indices
        img_floor = np.clip(img_floor, 0, lut_size - 1)
        img_ceil = np.clip(img_ceil, 0, lut_size - 1)
        
        # Get corner values for trilinear interpolation
        r0, g0, b0 = img_floor[:,:,0], img_floor[:,:,1], img_floor[:,:,2]
        r1, g1, b1 = img_ceil[:,:,0], img_ceil[:,:,1], img_ceil[:,:,2]
        fr, fg, fb = frac[:,:,0:1], frac[:,:,1:2], frac[:,:,2:3]
        
        # Trilinear interpolation
        c000 = lut[r0, g0, b0]
        c001 = lut[r0, g0, b1]
        c010 = lut[r0, g1, b0]
        c011 = lut[r0, g1, b1]
        c100 = lut[r1, g0, b0]
        c101 = lut[r1, g0, b1]
        c110 = lut[r1, g1, b0]
        c111 = lut[r1, g1, b1]
        
        c00 = c000 * (1 - fb) + c001 * fb
        c01 = c010 * (1 - fb) + c011 * fb
        c10 = c100 * (1 - fb) + c101 * fb
        c11 = c110 * (1 - fb) + c111 * fb
        
        c0 = c00 * (1 - fg) + c01 * fg
        c1 = c10 * (1 - fg) + c11 * fg
        
        result = c0 * (1 - fr) + c1 * fr
        
        return result
