---
layout: docpage
title: pytri#mesh
---

<h1 class="display-2">pytri — <code>mesh</code></h1>



## Using the `mesh` layer
This layer adds a 3D mesh to the scene.

```python
pytri.mesh(data)
```

Pass a single string in OBJ-formatting:

```python
pytri.mesh("""
v 1 1 0
v 0 0 1
v 1 0 1
f 1 2 3
""")
```

```python
pytri.mesh(open("./teapot.obj", 'r').read())
```


### Arguments
* `data`: A `obj`-formatted string
