---
layout: docpage
title: pytri#scatter
---

<h1 class="display-2">pytri — <code>scatter</code></h1>



## Using the `scatter` layer
This layer adds a 3D scatter to the scene.

```python
pytri.scatter(data, [radii], [colors])
```

You can use a numpy.array of shape (n, 3), or a Python list of lists:
```python
pytri.scatter([[1, 2, 3], [4, 5, 6]])
```

If you specify a `radius` as a scalar, it will be applied to all nodes. If you specify it as a list, `len(radius)` must be the same as `data.shape[0]`; each radius will apply to one node in the scatter.


### Arguments
* `data`: A numpy array of shape (n, 3), in xyz order. For example, `[[1, 2, 3], [4, 5, 6]]`
* `radii` (Optional): Radius of nodes in the visualization.
* `colors` (Optional): Colors of nodes in the visualization.

