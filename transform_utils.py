import cv2
import numpy as np

"""
Shared geometric transform helpers.

Used by ImageTransformPro and RemoveBackgroundPro so both nodes run identical
rotate / zoom / offset math and stay registered to each other.

Conventions:
  angle       degrees. Positive = clockwise (slider right), negative =
              counter-clockwise (slider left).
  zoom        -100..100, centred on 0. Exponential, see zoom_to_scale().
  offset_x/y  percent (-100..100) of the destination canvas. Positive x moves
              right, positive y moves UP, so both sliders read the same way:
              drag right for right/up, drag left for left/down. Note this is
              the opposite sign to a raw pixel Y, which grows downward.
"""

# Snap increment used by the "fixed" rotation method
FIXED_SNAP_DEGREES = 45.0


def snap_angle(angle, method):
    """Snap to FIXED_SNAP_DEGREES increments when method is 'fixed'."""
    if method == "fixed":
        return round(float(angle) / FIXED_SNAP_DEGREES) * FIXED_SNAP_DEGREES
    return float(angle)


def zoom_to_scale(zoom):
    """
    Map the -100..100 zoom slider to a scale multiplier.

    -100 -> 0.25x, -50 -> 0.5x, 0 -> 1.0x, +50 -> 2.0x, +100 -> 4.0x
    Exponential so a drag left shrinks as much as the same drag right grows.
    """
    return float(2.0 ** (float(zoom) / 50.0))


def fit_scale(src_shape, dst_shape):
    """Scale that fits the source fully inside the canvas, aspect preserved."""
    src_h, src_w = src_shape[:2]
    dst_h, dst_w = dst_shape[:2]
    return min(dst_w / float(src_w), dst_h / float(src_h))


def build_matrix(src_shape, dst_shape, angle, scale, offset_x=0.0, offset_y=0.0):
    """Build the 2x3 affine mapping the source image into the destination canvas."""
    src_h, src_w = src_shape[:2]
    dst_h, dst_w = dst_shape[:2]

    src_cx, src_cy = (src_w - 1) * 0.5, (src_h - 1) * 0.5
    dst_cx, dst_cy = (dst_w - 1) * 0.5, (dst_h - 1) * 0.5

    # cv2 treats positive angles as counter-clockwise, so negate to put CCW on
    # the left of the slider and CW on the right.
    M = cv2.getRotationMatrix2D((src_cx, src_cy), -float(angle), float(scale))

    # Re-centre on the canvas, then apply the percent offsets. offset_y is
    # negated so a positive value moves the image UP: canvas Y grows downward,
    # so subtracting shifts toward the top.
    M[0, 2] += (dst_cx - src_cx) + (float(offset_x) / 100.0) * dst_w
    M[1, 2] += (dst_cy - src_cy) - (float(offset_y) / 100.0) * dst_h

    return M


def warp_image(img, M, dst_shape):
    """Warp a float32 HxWx3 image. Anything outside the source becomes 0."""
    dst_h, dst_w = dst_shape[:2]
    out = cv2.warpAffine(
        img, M, (dst_w, dst_h),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    # Lanczos can overshoot slightly at high-contrast edges
    return np.clip(out, 0.0, 1.0)


def warp_single(data, M, dst_shape):
    """Warp a float32 HxW plane (mask or coverage) with the same matrix."""
    dst_h, dst_w = dst_shape[:2]
    out = cv2.warpAffine(
        data, M, (dst_w, dst_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    return np.clip(out, 0.0, 1.0)


def coverage_mask(src_shape, M, dst_shape):
    """1.0 where source pixels landed on the canvas, 0.0 in the empty corners."""
    src_h, src_w = src_shape[:2]
    ones = np.ones((src_h, src_w), dtype=np.float32)
    return warp_single(ones, M, dst_shape)


def transparency_grid(shape, check_size=16, light=160.0, dark=140.0):
    """Soft checkerboard used to preview transparent areas in-node."""
    h, w = shape[:2]
    ys = (np.arange(h) // check_size)[:, None]
    xs = (np.arange(w) // check_size)[None, :]
    grid = np.where((ys + xs) % 2 == 0, light, dark).astype(np.float32)
    return np.stack([grid, grid, grid], axis=2)


def normalize_mask(mask_tensor, target_shape):
    """MASK tensor -> float32 HxW in 0..1, resized to target_shape."""
    if len(mask_tensor.shape) == 3:
        mask_np = mask_tensor[0].cpu().numpy()
    else:
        mask_np = mask_tensor.cpu().numpy()

    mask_np = mask_np.astype(np.float32)
    if mask_np.max() > 1.0:
        mask_np = mask_np / 255.0

    h, w = target_shape[:2]
    if mask_np.shape[:2] != (h, w):
        mask_np = cv2.resize(mask_np, (w, h), interpolation=cv2.INTER_LINEAR)

    return mask_np
