<p align="center">
 <img align="center" alt="substrate" src="./logo.svg" width="50%" />
 <h1 align="center" fontsize="3em">pytri</h1>
</p>

<p align="center">
    <span>A python wrapper for <a href="https://github.com/jhuapl-boss/substrate">substrate</a>.</span><br />
    <a href="https://circleci.com/gh/j6k4m8/pytri"><img alt="CircleCI" src="https://circleci.com/gh/j6k4m8/pytri.svg?style=svg" /></a>
</p>

## Installation and Configuration
- Clone the repository.
```shell
git clone https://github.com/j6k4m8/pytri.git
```
- Install all dependencies.
```shell
pip3 install -r requirements.txt
```

## Usage

```python
from pytri import pytri

p = pytri()

p.axes()
p.scatter([[1, 2, 3], [4, 5, 6]])
p.show()
```
