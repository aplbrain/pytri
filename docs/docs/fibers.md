---
layout: docpage
title: pytri#scatter
---

<h1 class="display-2">pytri — <code>fibers</code></h1>



## Using the `fibers` layer
This layer adds 3D fibers to the scene.

```python
pytri.fibers(data, [colors], [alpha])
```

You can use a numpy.array of shape (n, m, 3), or a Python list of lists:
```python
pytri.scatter([
    [[1, 2, 3], [4, 5, 6]],
    [[11, 12, 13], [14, 15, 16], [17, 18, 19]],
])
```

If you specify a `colors` as a scalar, it will be applied to all nodes. If you specify it as a list, `len(colors)` must be the same as `data.shape[0]`; each color will apply to one fiber in the plot.


### Arguments
* `data`: A numpy array of shape (n, m, 3), in xyz order. In other words, a list of fibers, where each fiber is a list of [x,y,z]s.
* `colors` (Optional): Colors of fibers in the visualization.
* `alpha` (Optional): Transparency of fibers in the visualization.

