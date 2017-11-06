<p align="center">
 <img align="center" alt="substrate" src="./logo.svg" width="50%" />
 <h1 align="center" fontsize="3em">pytri</h1>
</p>

<p align="center">
    <span>A python wrapper for <a href="https://github.com/jhuapl-boss/substrate">substrate</a>.</span><br />
    <a href="https://circleci.com/gh/iscoe/pytri"><img alt="CircleCI" src="https://circleci.com/gh/iscoe/pytri.svg?style=svg" /></a>
    <a href="https://badge.fury.io/py/pytri"><img src="https://badge.fury.io/py/pytri.svg" alt="PyPI version" height="18"></a>
</p>

## Installation and Configuration

### New Hotness:
```shell
pip install -U pytri
```

### Old and Busted:

- Clone the repository.
```shell
git clone https://github.com/iscoe/pytri.git
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
