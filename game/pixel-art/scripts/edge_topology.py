"""Array-only Sobel/NMS and topology operations; no raster output."""
import numpy as np
SOBEL_X = np.array([[-1,0,1],[-2,0,2],[-1,0,1]],dtype=float)
SOBEL_Y = SOBEL_X.T

def nms(mag: np.ndarray, angle: np.ndarray, threshold: float) -> np.ndarray:
    """Canny-style non-maximum suppression -> 1px edge candidates."""
    h, w = mag.shape
    keep = np.zeros_like(mag, dtype=bool)
    bins = np.round(angle / 45.0).astype(int) % 4  # 0:H, 1:45, 2:V, 3:135
    offsets = {0: ((0, -1), (0, 1)), 1: ((-1, -1), (1, 1)),
               2: ((-1, 0), (1, 0)), 3: ((1, -1), (-1, 1))}
    ys, xs = np.where(mag > threshold)
    for y, x in zip(ys, xs):
        a, b = offsets[bins[y, x]]
        va = mag[y + a[0], x + a[1]] if 0 <= y + a[0] < h and 0 <= x + a[1] < w else 0.0
        vb = mag[y + b[0], x + b[1]] if 0 <= y + b[0] < h and 0 <= x + b[1] < w else 0.0
        if mag[y, x] >= va and mag[y, x] >= vb:
            keep[y, x] = True
    return keep

def thinning(mask: np.ndarray, max_iter: int = 100) -> np.ndarray:
    """Zhang-Suen skeletonisation -> 1px lines."""
    m = mask.astype(np.uint8)
    h, w = m.shape
    for _ in range(max_iter):
        changed = False
        for step in (0, 1):
            remove = []
            ys, xs = np.where(m == 1)
            for y, x in zip(ys, xs):
                if y == 0 or y == h - 1 or x == 0 or x == w - 1:
                    continue
                p2, p3, p4 = m[y - 1, x], m[y - 1, x + 1], m[y, x + 1]
                p5, p6, p7 = m[y + 1, x + 1], m[y + 1, x], m[y + 1, x - 1]
                p8, p9 = m[y, x - 1], m[y - 1, x - 1]
                ring = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
                b = sum(ring[:8])
                a = sum(1 for i in range(8) if ring[i] == 0 and ring[i + 1] == 1)
                if not (2 <= b <= 6 and a == 1):
                    continue
                if step == 0:
                    if p2 * p4 * p6 == 0 and p4 * p6 * p8 == 0:
                        remove.append((y, x))
                else:
                    if p2 * p4 * p8 == 0 and p2 * p6 * p8 == 0:
                        remove.append((y, x))
            if remove:
                changed = True
                for y, x in remove:
                    m[y, x] = 0
        if not changed:
            break
    return m.astype(bool)

def neighbours(mask: np.ndarray, x: int, y: int) -> list[tuple[int, int]]:
    h, w = mask.shape
    out = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and mask[ny, nx]:
                out.append((nx, ny))
    return out

def solid_2x2(mask: np.ndarray, x: int, y: int) -> bool:
    h, w = mask.shape
    for ox, oy in ((-1, -1), (0, -1), (-1, 0), (0, 0)):
        if (0 <= x + ox and x + ox + 1 < w and 0 <= y + oy and y + oy + 1 < h
                and mask[y + oy:y + oy + 2, x + ox:x + ox + 2].all()):
            return True
    return False

def perfect_pixel(mask: np.ndarray, max_iter: int = 50) -> tuple[np.ndarray, int]:
    """Remove the middle pixel of L-shaped 1px turns while keeping 8-connectivity."""
    m = mask.copy()
    removed_total = 0
    for _ in range(max_iter):
        snap = m.copy()
        remove: list[tuple[int, int]] = []
        ys, xs = np.where(snap)
        for y, x in zip(ys, xs):
            nn = neighbours(snap, x, y)
            if len(nn) != 2:
                continue
            (x1, y1), (x2, y2) = nn
            if solid_2x2(snap, x, y):
                continue
            ortho = ((x1 == x and y2 == y) or (x2 == x and y1 == y))
            if not ortho:
                continue
            # the two arms must be diagonal to each other after removal
            if abs(x1 - x2) == 1 and abs(y1 - y2) == 1:
                remove.append((x, y))
        if not remove:
            break
        for x, y in remove:
            m[y, x] = False
        removed_total += len(remove)
    return m, removed_total
