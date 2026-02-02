# ComfyUI-MachinePaintingNodes

![MachinePaintingNodes](images/MachinePaintingNodes.png)

**Professional color grading, mask tools, and utilities for ComfyUI**

A comprehensive node suite for professional level image processing, color correction, and advanced workflow enhancement utilities. 

## Installation

### ComfyUI Manager (Recommended)
Search for "MachinePaintingNodes" in ComfyUI Manager and install.

### Manual Installation
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/machinepainting/ComfyUI-MachinePaintingNodes.git
```

### Dependencies
```bash
pip install -r requirements.txt
```

---

## Nodes (21 Total)

### Color Adjustment

| Node | Description |
|------|-------------|
| **Curves Adjust Pro** | Interactive Photoshop-style curves with RGB/R/G/B channels, 17 presets, mask support, channel-mask support |
| **Levels Adjust** | Black point, white point, gamma, output levels |
| **Auto Levels** | Automatic levels correction |
| **Selective Color Pro** | CMYK adjustments for specific color ranges and fine tuned color adjustments (reds, yellows, greens, cyans, blues, magentas, whites, neutrals, blacks) |
| **Brightness Contrast Adjust** | Simple brightness and contrast controls with simple slider controls |
| **Color Match Blend** | Match colors from one image to another with adjustments |
| **Color Adjust Blend** | Adjust Color range for Shadows, Mid-Range, and Highlights. Optional Color Match Blend Color |
| **LUT Apply** | Apply .cube/.3dl LUT files for cinematic color grading (includes 5 bundled LUTs) |

### Blending

| Node | Description |
|------|-------------|
| **Image Blend Pro** | Blend images with 15 blend modes (normal, overlay, multiply, screen, soft light, hard light, etc.) |

### Mask and Background

| Node | Description |
|------|-------------|
| **Remove Background Pro** | Advanced AI-powered background removal with 8 rembg models, mask editing tools, multiple preview modes |
| **Mask Editor** | Stand alone Mask Tools. Refine masks with grow/shrink/blur/fill |
| **Apply Mask** | Composite image with mask and background options |
| **Channel Mask Pro** | Extract R/G/B/A channels as separate masks with levels/contrast adjustments and input mask support for advanced Channel Masking|

### Analysis

| Node | Description |
|------|-------------|
| **Histogram View** | Display RGB/luminance histogram in-node for advanced image setting color display|
| **Color Wheel View** | Display vectorscope color distribution in-node for advanced image setting color display |

### Utilities

| Node | Description |
|------|-------------|
| **Boolean** | Output a true/false value |
| **Boolean Invert** | Flip boolean value (true to false, false to true) for advanced workflow pipline and settings switching |
| **Boolean Switch Value Output** | Output different values based on boolean for advanced workflow pipline and settings switching |
| **Boolean Input Value Switch** | Route inputs based on boolean for advanced workflow pipline and settings switching |
| **Boolean Master Switch** | Control multiple booleans from one switch for controlling multiple switches with one master switch node |
| **Seed Lock** | Lock/unlock seed values with a toggle to lock the current seed vaule, opposed to the standard where the following run seed value is locked |

---

## Features

### Curves Adjust Pro
- Interactive curve editor with click-to-add, drag-to-move, shift-click-to-remove points
- Separate RGB, Red, Green, Blue channels
- 17 built-in presets (S-Curve Contrast, Fade, Cross Process, Cinematic, etc.)
- Visual display of all channel curves in RGB mode
- Mask support with invert option
- Catmull-Rom spline interpolation for smooth curves

### LUT Apply
- Supports .cube and .3dl LUT formats
- 5 bundled LUTs included (auto-installed to `ComfyUI/input/luts/`):
  - Cinematic_Teal_Orange
  - Warm_Tone
  - Cool_Tone
  - Vintage_Fade
  - High_Contrast
- Intensity slider to blend effect
- Add your own LUTs to `ComfyUI/input/luts/`

### Remove Background Pro
- 8 AI models: u2net, u2netp, u2net_human_seg, u2net_cloth_seg, silueta, isnet-general-use, isnet-anime, sam
- Built-in mask refinement (grow/shrink, blur, threshold)
- Preview modes: masked, mask only, side-by-side, overlay
- Edge feathering for smooth composites

### Channel Mask Pro
- Separates image into R, G, B, Alpha channel masks
- Levels adjustments (black point, white point, gamma)
- Contrast and brightness controls
- Input mask support with invert option
- B&W preview with R/G/B/L labels

### Selective Color Pro
- Target specific colors: reds, yellows, greens, cyans, blues, magentas, whites, neutrals, blacks
- CMYK adjustment sliders (-100 to +100)
- Reset All button
- Mask support

---

## Changelog

### v2.0.0
- **New Nodes:** LUT Apply, Channel Mask Pro, Selective Color Pro, Boolean Invert
- **Bundled LUTs:** 5 color grading LUTs included with auto-install
- **Curves Adjust Pro:** Added mask support, improved curve display showing all channels in RGB mode
- **Channel Mask Pro:** Added input mask support, levels/contrast adjustments, improved B&W preview
- **Unified Category:** All nodes now appear under single "MachinePaintingNodes" folder
- **Selective Color Pro:** Added Reset All button
- **Analysis Nodes:** Improved auto-scaling for Histogram and Color Wheel views
- **Code Cleanup:** Removed deprecated nodes, standardized categories

### v1.0.0
- Initial release with color adjustment, blending, and boolean utility nodes

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Want to Auto Send your ComfyUI files from output folder to your Google Drive or Dropbox Account? 

Check out these new Nodes to advance your Ai workflows. Super helpful tools to protect your creations and streamline your process. DriveSend and DropSend node with optional file Encryption.

- [ComfyUI_DriveSendNode](https://github.com/machinepainting/ComfyUI_DriveSendNode)
- [ComfyUI_DropSendNode](https://github.com/machinepainting/ComfyUI_DropSendNode)

---

## Tags

`comfyui` `comfyui-nodes` `custom-nodes` `color-grading` `color-correction` `curves` `levels` `lut` `lookup-table` `photoshop` `image-processing` `image-editing` `background-removal` `rembg` `masking` `mask-editor` `channel-mixer` `histogram` `vectorscope` `blend-modes` `compositing` `stable-diffusion` `ai-art` `generative-art` `film-emulation` `cinematic` `color-matching` `hsl` `cmyk` `selective-color` `boolean-logic` `workflow` `utilities`
