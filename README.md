# MachinePaintingNodes for ComfyUI - By MachinePainting

**Professional color & blending tools for AI artists.**

A collection of Professional Color Match, Color Adjust, and Image Blending Tools.

---

## Nodes

| Node | Category | Purpose |
|------|--------|--------|
| **ColorAdjustBlend** | Color | Per-channel tonal adjustments + blend modes |
| **ColorMatchBlend** | Color | Match reference image color + saturation |
| **ImageBlendPro** | Image | Advanced layer blending with 15+ Photoshop modes |

---

## Node Details

### **ColorAdjustBlend**
Fine-tune **shadows, midtones, highlights** per RGB channel.

| Parameter | Range | Effect |
|--------|-------|--------|
| `r/g/b_shadows` | -100 to +100 | Lift dark areas |
| `r/g/b_midtones` | -100 to +100 | Balance middle tones |
| `r/g/b_highlights` | -100 to +100 | Control bright areas |

**Optional Overlay:**
- `enable_color_overlay`: Toggle color layer
- `color_input`: Image to blend
- `color_blend_mode`: `overlay`, `multiply`, `screen`, etc.
- `color_input_opacity`: 0.0–1.0

---

### **ColorMatchBlend**
Match **hue & saturation** from a reference image.

| Parameter | Range | Effect |
|--------|-------|--------|
| `target_image` | — | Image to adjust |
| `reference_image` | — | Color source |
| `strength` | 0.0–1.0 | Blend intensity |
| `saturation` | -100 to +100 | Boost/reduce vibrance |

---

### **ImageBlendPro**
Blend two images with **Photoshop-grade modes**.

| Blend Mode | Effect |
|-----------|--------|
| `normal` | Standard overlay |
| `multiply` | Darken |
| `screen` | Lighten |
| `overlay` | Contrast boost |
| `soft_light` | Gentle contrast |
| `color` | Hue + saturation only |
| `luminosity` | Brightness only |

`blend_amount`: 0.0 (image1) → 1.0 (image2)

---


