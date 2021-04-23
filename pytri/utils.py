"""
Copyright 2021 The Johns Hopkins University Applied Physics Laboratory.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
