import numpy as np
from pythreejs import DataTexture


def _circle_mask(h, w):
    # https://stackoverflow.com/a/44874588/979255

    c = (int(w / 2), int(h / 2))
    radius = min(c[0], c[1], w - c[0], h - c[1])

    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((X - c[0]) ** 2 + (Y - c[1]) ** 2)

    mask = dist <= radius
    return mask


CIRCLE_MAP = DataTexture(
    data=np.array([_circle_mask(64, 64).astype("float32")] * 4).T.astype("float32"),
    type="FloatType",
    format="RGBAFormat",
)


def _normalize_shift(x):
    """
    Normalize a vector between -1,1, attempting to center on 0.

    Arguments:
        x (np.ndarray)

    Returns:
        np.ndarray

    """
    return (x - np.mean(x)) / np.max(x)
