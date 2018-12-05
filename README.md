<p align="center">
 <img align="center" alt="substrate" src="./logo.svg" width="50%" />
 <h1 align="center" fontsize="3em">pytri</h1>
</p>

<p align="center">
    <span>A python wrapper for <a href="https://github.com/aplbrain/substrate">substrate</a>.</span><br />
    <a href="https://circleci.com/gh/aplbrain/pytri"><img alt="CircleCI" src="https://circleci.com/gh/aplbrain/pytri.svg?style=svg" /></a>
    <a href="https://badge.fury.io/py/pytri"><img src="https://badge.fury.io/py/pytri.svg" alt="PyPI version" height="18"></a>
    <a href="https://github.com/aplbrain/substrate"><img src="https://img.shields.io/badge/substrate-v.1.1.0-cd1642.svg" height="18"></a>
    <a href="https://codeclimate.com/github/aplbrain/pytri/maintainability"><img src="https://api.codeclimate.com/v1/badges/898780feddf32135447b/maintainability" /></a>
</p>

## What is Pytri?

Pytri is a data visualization library for 3D rendering in a Jupyter notebook.

### Why not use...?

- **Matplotlib**: 3D support is a second-class citizen; matplotlib's strengths are in 2D.
- **Plotly**: Plotly is a great, powerful library, but it has a complex, non-ideomatic API.
- **threejs Python libraries**: These are great, but support basic geometry operations better than high-level data visualization.

Under the hood, pytri uses [substrate](https://github.com/aplbrain/substrate), a fast, layer-based visualization framework built upon threejs. And importantly, **pytri visualizations persist when you export a jupyter notebook to HTML!**

## Installation and Configuration

### New Hotness:

```shell
pip install -U pytri
```

### Old and Busted:

- Clone the repository.
```shell
git clone https://github.com/aplbrain/pytri.git
```
- Install all dependencies.
```shell
pip3 install -r requirements.txt
pip3 install -U .
```

## Usage

```python
from pytri import pytri

p = pytri()

p.axes()
p.scatter([[1, 2, 3], [4, 5, 6]])
p.show()
```
