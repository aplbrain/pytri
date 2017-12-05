---
layout: docpage
title: pytri#graph
---

<h1 class="display-2">pytri — <code>graph</code></h1>

<br />

## Using the `graph` layer
<br />

```python
pytri.graph(data, [r], [nc], [lc])
```

### Arguments
* `data`: A [Networkx](https://networkx.github.io/documentation/networkx-1.10/overview.html) graph, passed in as [JSON](https://networkx.github.io/documentation/networkx-1.10/reference/readwrite.json_graph.html) or as a Networkx graph object.
    * Graph must have nodes with positions as attributes. These positions may be specified as a tuple, a dictionary, or directly on the node object:
        * `graph.add_node(id, pos=(x_pos, y_pos, z_pos))`
        * `graph.add_node(id, pos ={'x': x_pos, 'y': y_pos, 'z': z_pos})`
        * `graph.add_node(id, x=x_pos, y=y_pos, z=z_pos)`
* `r` (Optional): Radius of nodes in the visualization.
* `nc` (Optional): Colors of nodes in the visualization.
* `lc` (Optional): Colors of the links in the visualization.
