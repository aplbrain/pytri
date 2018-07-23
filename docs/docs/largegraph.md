---
layout: docpage
title: pytri#largegraph
---

<h1 class="display-2">pytri — <code>Large Graph</code></h1>

<br />

## Using the `large_graph` layer
<br />
`large_graph` uses a [GPU particle system](https://threejs.org/examples/webgl_gpu_particle_system.html) to render large graphs.
We recommend using `large_graph` when the number of nodes to render exceeds 1000, or when `graph` takes too long to load for your graph.

```python
pytri.large_graph(data, [radii], [colors])
```

### Arguments
* `data`: A [Networkx](https://networkx.github.io/documentation/networkx-1.10/overview.html) graph, passed in as [JSON](https://networkx.github.io/documentation/networkx-1.10/reference/readwrite.json_graph.html) or as a Networkx graph object.
    * Graph must have nodes with positions as attributes. These positions may be specified as a tuple or a dictionary:
        * `graph.add_node(id, pos=(x_pos, y_pos, z_pos))`
        * `graph.add_node(id, pos ={'x': x_pos, 'y': y_pos, 'z': z_pos})`
* `radii` (Optional): Radius of nodes in the visualization. Visualiation will render as cubes, with default size of 2pts.
* In progress: `colors` (Optional) Colors of nodes in the visualization, defaults to black.

