## *Class* `Figure`


Generic class for a new Pytri figure.



## *Function* `__init__(self, **kwargs)`


Create a new figure.

All arguments are optional.

### Arguments
> - **float])** (`None`: `None`): The size to make the visualization



## *Function* `remove(self, object_set: Union[List[str], str]) -> bool`


Remove a single layer from the scene.

Use the UUID you get back from the layer-addition methods to identify which items to remove.

### Arguments
> - **str])** (`None`: `None`): The object(s) to remove

### Returns
    True, if successful



## *Function* `clear(self)`


Clear all layers from the scene.

### Arguments
    None

### Returns
    None



## *Function* `show(self)`


Render the scene for the viewer.

This method can be called serveral times in order to generate several visualizations which are "yoked" together.



## *Function* `axes(self, size: float = 20)`


Add a set of axes to the origin.

### Arguments
> - **size** (`float`: `20`): The length of each axis into the positive values.

### Returns
    UUID



## *Function* `graph(self, graph: nx.Graph, **kwargs)`


Plot a networkx graph.

### Arguments
> - **3coords])** (`None`: `None`): positions to
        assign to each node.
> - **pos_attribute** (`str`: `None`): The node attribute to use as a 3coord.
> - **edge_width** (`int`: `5`): The line width to pass to Figure#lines

### Returns
    UUID



## *Function* `lines(self, lines, colors=None, width=10)`


Plots a series of line segments.

### Arguments
> - **lines** (`None`: `None`): list of lists of 2-tuples of 3coords
> - **colors** (`None`: `None`): Either list of list of 2-tuples of 3coords,
        or a list of lists of 3coords

### Returns
    UUID



## *Function* `scatter(self, *args, **kwargs)`


There are several options for arguments this this function.

One positional array-like
    Figure#scatter(np.random.randint(0, 10, (10, 3)))

Three positional list-likes
    Figure#scatter(xs, ys, zs)

Three named list-likes
    Figure#scatter(xs=[1, 2], ys=[2, 3], zs=[10, 20])

Three positional column names and a dataframe
    Figure#scatter("x", "y", "depth", my_dataframe)

### Arguments
> - **attenuate_size** (`False`: `None`): Whether items further from
        the camera should appear smaller



## *Function* `mesh(self, *args, **kwargs)`


Add a mesh to the scene.

There are several supported types of argument.

    Figure#mesh(obj=Union[List[List], np.ndarray])

    Figure#mesh(str)

### Returns
    UUID

