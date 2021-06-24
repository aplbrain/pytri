# pytri v2

> A Pytri redux, using the latest available THREE.js bindings and GPU-offloaded rendering of large scenes.

WARNING: `pytri` is currently untested. Use at your own risk.

## Installation

```shell
pip install pytri
# or:
# pip3 install git+https://github.com/aplbrain/pytri
```

## Getting Started

Let's plot some scatterplot data in 3D. In your favorite Jupyter notebook or binder application, import pytri:

```python
from pytri import Figure
```

We can now generate some sample data:

```python
import numpy as np

fig = Figure()

xs = np.random(0, 100)
ys = np.random(0, 100)
zs = np.random(0, 100)

fig.scatter(xs, ys, zs)

fig.show()
```

<img width="371" alt="image" src="https://user-images.githubusercontent.com/693511/108643342-34765580-7478-11eb-939c-34ead3337a76.png">

## Examples

### Render a NetworkX Graph

Here's a crazy dense randomly-arranged graph with over a million edges. (You'll find the slowest part of this process is just generating that graph!)

This graph renders in realtime (60FPS) in Pytri.

```python
import networkx as nx
g = nx.fast_gnp_random_graph(50_000, 0.001)
pos = {k: [vv * 500 for vv in v] for k, v in nx.random_layout(g, dim=3).items()}

f = Figure()
f.axes()
f.graph(g, pos=pos, edge_width=1, node_size=10)

f.show()
```

<img width="376" alt="image" src="https://user-images.githubusercontent.com/693511/108643454-ad75ad00-7478-11eb-80cf-6e38b829636d.png">

### Random color-changing edges

These edges are a different color on the left edge than on the right edge:

```python
f = Figure()
f.axes()
f.lines(
    # 100 lines on the interval 0-100
    np.random.random((100, 2, 3)) * 100,
    # 200 colors, start/stop for each line
    colors=np.random.random((100, 2, 3)),
    width=4
)
f.show()
```

<img width="358" alt="image" src="https://user-images.githubusercontent.com/693511/108643657-7bb11600-7479-11eb-9b71-c406f5f8dadb.png">

### Lines and an image pulled from the internet

```python
f.imshow(
    "https://i.imgur.com/VK8Tp5q.jpeg",
    width=100, height=100,
    rotation=(0, 3.14/2, 0)
)
f.show()
```

<img width="383" alt="image" src="https://user-images.githubusercontent.com/693511/108643859-6092d600-747a-11eb-9e7d-b75544a74fc9.png">

### Rendering numpy arrays in RGB or Greyscale

```python
f.scatter(np.random.randint(-50, 50, (1_00_000,3)))
f.imshow(
    # 3 dimensions, interpreted as RGB
    np.random.random((1000, 1000, 3)),
    width=200, height=200,
    rotation=(0, 3.14/2, 0)
)
f.imshow(
    # 2 dimensions, interpreted as grayscale
    np.random.random((1000, 1000)),
    width=200, height=200,
    # omitting rotation, the plane faces "up" along Z
)
```

<img width="500" alt="image" src="https://user-images.githubusercontent.com/693511/108643926-b5365100-747a-11eb-8619-c6686a510f6a.png">

### One way to (cheat) render a volume

```python
from pytri import Figure
import intern

morgan2020 = intern.array("bossdb://morgan2020/lgn/em", resolution=2)

em_excerpt = morgan2020[1000:1050, 25000:25000+300, 25000:25000+300]

coords = []
for z in range(em_excerpt.shape[0]):
    for y in range(em_excerpt.shape[1]):
        for x in range(em_excerpt.shape[2]):
            coords.append((x, y, z*10))

f = Figure()
f.scatter(coords, color=[[i,i,i] for i in em_excerpt.ravel()], attenuate_size=True, size=5)
f.show()
```

<img width="410" alt="image" src="https://user-images.githubusercontent.com/693511/108712486-d6338c00-74e4-11eb-945f-4ea2982ddac8.png">
