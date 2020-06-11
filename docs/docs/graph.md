---
layout: docpage
title: pytri#graph
---

<h1 class="display-2">pytri — <code>graph</code></h1>

<br />

## About
A GPU-enabled 3-dimensional graph visualization layer.

<br />

## Using the `graph` layer

```python
pytri.graph(data, [radius], [node_color], [link_color], [name])
```
<br />

### Arguments

* `data`: A [Networkx](https://networkx.github.io/documentation/networkx-1.10/overview.html) graph, passed in as [JSON](https://networkx.github.io/documentation/networkx-1.10/reference/readwrite.json_graph.html) or as a Networkx graph object.
    * Graph must have nodes with positions as attributes. These positions may be specified as a tuple, a dictionary, or directly on the node object:
        * `graph.add_node(id, pos=(x_pos, y_pos, z_pos))`
        * `graph.add_node(id, pos ={'x': x_pos, 'y': y_pos, 'z': z_pos})`
        * `graph.add_node(id, x=x_pos, y=y_pos, z=z_pos)`
* `radius` (Optional): Radius of nodes in the visualization. This can either be a float or a list of floats (one for each node). By default, a radius of 0.15 is used.
* `node_color` (Optional): Colors of nodes in the visualization as a single float or list of floats (one for each node). The colors in this list will be mapped directly onto the list of nodes in the graph (ie: the color at index 0 of the color list will be the color of the node at index 0 of the nodes list).
* `link_color` (Optional): Color of all the links in the visualization as a single float.
* `name` (Optional): Name of the layer.
