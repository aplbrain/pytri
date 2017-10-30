---
layout: docpage
title: pytri
---

<h1 class="display-2">pytri</h1>

<br />

## `show(self)`
Render the frame to the Jupyter notebook. Takes no arguments.

---

## `remove_layer(self, name)`
Remove a layer by name.
### Arguments:
* name (`str`)

### Returns:
* None

---

## `clear(self)`
Remove all layers from scene.

### Arguments:
* None

### Returns:
* None

---

## `add_layer(self, layer_js, params, name)`
Add a custom JS layer to the visualization.

### Arguments:
* layer_js (`str`): The contents of a JS file
* params (`dict`:`None`): The data to pass into the layer constructor
* name (`str`:`None`): Optional name for the layer

### Returns:
* `str`: Name, as inserted into the scene

---
