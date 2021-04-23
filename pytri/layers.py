"""
Copyright 2021 The Johns Hopkins University Applied Physics Laboratory.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from abc import ABC, abstractmethod
from typing import Callable, Dict, Hashable, Iterable, Tuple, Union
from warnings import warn
import networkx as nx
import numpy as np
import trimesh
from pythreejs import (
    AxesHelper, BufferAttribute, BufferGeometry, DataTexture,
    Group, ImageTexture, LineMaterial, LineSegments2,
    LineSegmentsGeometry, Mesh, MeshBasicMaterial, MeshLambertMaterial,
    PlaneGeometry,
    Points, PointsMaterial)

from .utils import CIRCLE_MAP, _normalize_shift
# pylint: disable=keyword-arg-before-vararg,attribute-defined-outside-init
Coord3 = Tuple[float, float, float]
ColorRGB = Tuple[float,float,float]
Edge = Tuple[Coord3, Coord3]
class Layer(ABC):
    """
    Abstract Layer class. Not meant to be used on its own.
    """
    _LAYER_NAME = "layer"
    def __init__(self,*args, **kwargs) -> None:
        """
        Abstract Layer class. Not meant to be used on its own.
        """
        if len(args) > 0:
            warn(f'Unused args : {args}')
        if len(kwargs) > 0:
            warn(f'Unused kwargs : {kwargs}')
        self._id = None
        self._objects = []
        self._group = None
    @abstractmethod
    def get_bounding_box(self) -> Tuple[Coord3, Coord3]:
        """
        Gets the bounding box as two coordinates representing opposite corners.
        """
        ...
    @abstractmethod
    def get_preferred_camera_view(self) -> Coord3:
        """
        Gets preferred camera view, as a target tuple to orbit around
        """
        return None
    @property
    def group(self) -> Group:
        """
        The pythreejs Group for all the objects in the layer
        """
        if self._group is None:
            self._group = Group()
            for obj in self._objects:
                self._group.add(obj)

        return self._group
    @property
    def affine(self) -> np.ndarray:
        """
        The affine transform of the entire layer
        """
        return self.group.matrix

    def set_affine(self, a: np.ndarray):
        """
        Set affine transform for the entire layer
        """
        self._affine = a
        sc = self.group
        sc.matrix = self._affine
    def rotate(self,
        x:float,
        y:float,
        z:float,
        order:str="XYZ"
        ):
        """
        Sets the rotation of the entire layer.
        x,y,z: the rotation around each axes, in degrees.
        order: the order of rotation
        """
        sc = self.group
        sc.rotation = (x,y,z,order)
    def translate(self, x,y,z):
        """
        Sets the translation of the entire layer.
        x,y,z: translation along each axis
        """
        sc = self.group
        xyz = np.array(sc.position)
        sc.position = tuple(xyz + [x,y,z])
    def on_click(self, picker):
        """
        Click callback. See
        https://pythreejs.readthedocs.io/en/stable/api/controls/Picker_autogen.html#
        for docs on picker
        args:
            picker: Picker instance
        """
        s = f"""
            layer: {self._LAYER_NAME}
            point clicked: {picker.point}
            """

        return s
    def _on_click(self, picker):
        return self.on_click(picker)

class AxesLayer(Layer):
    """
    Add a set of axes to the origin.

    Arguments:
        size (float: 20): The length of each axis into the positive values.
    """
    _LAYER_NAME = 'axes'
    def __init__(self, size: float = 20, *args, **kwargs):
        """
        Add a set of axes to the origin.

        Arguments:
            size (float: 20): The length of each axis into the positive values.



        """
        super().__init__(*args, **kwargs)
        self._objects.append(AxesHelper(size=size))
        self._size = size
    def get_bounding_box(self):
        return ((0,0,0), (self._size, self._size, self._size))
    def get_preferred_camera_view(self):
        return (0,0,0)
class CoordinateLayer(Layer):
    """
    Subclass for layers that depends on coordinates or sets of points for viewing.
    Not meant to be used directly.
    """
    _LAYER_NAME = 'coordinate'
    #pylint: disable=attribute-defined-outside-init
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self._coords = [[0,0,0]]

    def _calc_coord_metrics(self):
        coords = self._coords
        self._coord_max = np.max(coords,axis=0)
        self._coord_min = np.min(coords,axis=0)
        self._mean_coords = np.mean(coords, axis=0)
    def get_bounding_box(self):
        if not (hasattr(self, '_coord_min') and hasattr(self, '_coord_max')):
            self._calc_coord_metrics()
        return (self._coord_min, self._coord_max)
    def get_preferred_camera_view(self):
        if not hasattr(self, '_mean_coords'):
            self._calc_coord_metrics()
        return self._mean_coords
class LinesLayer(CoordinateLayer):
    """
    Plots a series of line segments.

    Arguments:
        lines: Iterable of (u,v), where u,v are 3 tuples of float coordinates.
            Lines are drawn between each u and v.
        colors: Either
            * An iterable of (u,c), where u is a coordinate, and c is a color.
            * a list of c (3coord, RGB), the same length as lines
            * single 3 tuple (RGB) applied to all lines


    """
    _LAYER_NAME = 'lines'
    def __init__(self,
        lines: Iterable[Edge],
        colors: Union[Iterable[Tuple[Coord3, ColorRGB]], Iterable[ColorRGB], ColorRGB, None] = None,
        width:int = 10,
        *args,
        **kwargs):
        """
        Plots a series of line segments.

        Arguments:
            lines: Iterable of (u,v), where u,v are 3 tuples of float coordinates.
            Lines are drawn between each u and v.
            colors: Either
                * An iterable of (u,c), where u is a coordinate, and c is a color.
                * a list of c (3coord, RGB), the same length as lines
                * single 3 tuple (RGB) applied to all lines


        """
        super().__init__(layer_name='lines',*args, **kwargs)
        if isinstance(colors, tuple):
            color = colors
            colors = None
        else:
            color = [0,0,0]
        colors = colors if (not colors is None) else [color for _ in lines]

        colors = np.array([c if len(c) == 2 else [c, c] for c in colors],dtype=np.float32)
        coords = []
        for uv in lines:
            coords.extend(uv)
        self._coords = np.array(coords)
        geo = LineSegmentsGeometry(
            positions=np.array(lines,dtype=np.float32),
            colors=colors,
        )
        mat = LineMaterial(linewidth=width, vertexColors="VertexColors")
        self._objects.append(LineSegments2(geo, mat))

class ScatterLayer(CoordinateLayer):
    """
    There are several options for arguments this this function.

    One positional array-like
        Figure#scatter(np.random.randint(0, 10, (10, 3)))

    Three positional list-likes
        Figure#scatter(xs, ys, zs)

    Three named list-likes
        Figure#scatter(xs=[1, 2], ys=[2, 3], zs=[10, 20])

    Three positional column names and a dataframe
        Figure#scatter("x", "y", "depth", my_dataframe)

    Arguments:
        attenuate_size (False): Whether items further from
            the camera should appear smaller

    """
    _LAYER_NAME = 'scatter'
    def __init__(self,*args, **kwargs):
        """
        There are several options for arguments this this function.

        One positional array-like
            Figure#scatter(np.random.randint(0, 10, (10, 3)))

        Three positional list-likes
            Figure#scatter(xs, ys, zs)

        Three named list-likes
            Figure#scatter(xs=[1, 2], ys=[2, 3], zs=[10, 20])

        Three positional column names and a dataframe
            Figure#scatter("x", "y", "depth", my_dataframe)

        Arguments:
            attenuate_size (False): Whether items further from
                the camera should appear smaller

        """
        super().__init__(**kwargs)
        pts = None
        if len(args) == 1:
            if isinstance(args[0], (np.ndarray, Iterable)):
                pts = np.asarray(args[0], dtype=np.float32)

        if len(args) == 3 and isinstance(args[0], (list, np.ndarray)):
            pts = np.asarray([i for i in zip(args[0], args[1], args[2])],dtype=np.float32)

        if pts is None:
            raise ValueError("Unsupported arguments to scatter.")
        self._coords = pts
        color = kwargs.get("c") if "c" in kwargs else None
        if color is None:
            color = kwargs.get("color", None)
        if color is None:
            color = pts / pts.max()
        if len(color) != len(pts):
            color = [color for _ in pts]

        colors = (
            BufferAttribute(array=color, dtype=np.float32)
            if color is not None
            else BufferAttribute(array=np.asarray(pts / pts.max(), dtype=np.float32))
        )
        geometry = BufferGeometry(
            attributes={
                "position": BufferAttribute(array=np.asarray(pts, dtype=np.float32)),
                "color": colors,
            }
        )

        tex = CIRCLE_MAP
        if kwargs.get("marker") in [".", "o", "circle"]:
            tex = CIRCLE_MAP
        elif kwargs.get("marker") in ["[]", "r", "q", "square"]:
            tex = None
        elif "map" in kwargs:
            tex = kwargs.get("map")

        material = PointsMaterial(
            vertexColors="VertexColors",
            size=kwargs.get("size", 5),
            sizeAttenuation=kwargs.get("attenuate_size", False),
            **({"map": tex} if tex else {}),
        )
        p = Points(geometry=geometry, material=material)
        self._objects.append(p)

class GraphLayer(ScatterLayer,LinesLayer):
    """
    Plot a networkx graph.

    Arguments:
        graph: NetworkX graph
        pos: positions to assign to each node.
        pos_attribute: The node attribute to use as a 3coord.
        edge_width: The line width to pass to layers#LineLayers
    """
    _LAYER_NAME = 'graph'
    def __init__(self,
        graph : nx.Graph,
        pos_attribute:str = None,
        pos:Union[Iterable[Coord3], Dict[Hashable, Coord3]] = None,
        node_size: float = 5.,
        edge_width: float = 5,
        **kwargs):
        """
        Plot a networkx graph.

        Arguments:
            graph: NetworkX graph
            pos: positions to assign to each node.
            pos_attribute: The node attribute to use as a 3coord.
            edge_width: The line width to pass to layers#LineLayers
        """
        if pos_attribute is not None:
            attr = pos_attribute
            pos = {n: a[attr] for n, a in graph.nodes(data=True)}
        elif pos is not None:
            if isinstance(pos, Iterable):
                pos = {n: p for n, p in zip(graph.nodes(), pos)}
        else:
            try:
                pos = {n: p["pos"] for n, p in graph.nodes(data=True)}
            except Exception as e:
                raise ValueError("You must pass a valid position argument.") from e

        scatter_points = [i for i in pos.values()]
        lines = [[pos[u], pos[v]] for u, v in graph.edges()]
        super().__init__(scatter_points,lines=lines, size=node_size,width=edge_width)
class ImshowLayer(Layer):
    """
    Plot an image as a plane.

    Arguments:
        image (Union[str, np.ndarray]): The image to plot. This can be a
            URL, a blob, or a numpy array. If it is a numpy array, it must
            be either 2D (greyscale), 3D (RGB), or 4D (RGBA).
        center_pos: Center pos
        rotation: Rotation of the img
            plane, in radians
        width (float: 10): The width of the final rendered plane
        height (float: 10): The height of the final rendered plane
    """
    _LAYER_NAME = 'imshow'
    def __init__(
        self,
        image: Union[str, np.ndarray],
        center_pos: Coord3 = (0, 0, 0),
        rotation: Coord3 = (0, 0, 0),
        width: float = 10,
        height: float = 10,
        *args,
        **kwargs
        ):
        """
        Plot an image as a plane.

        Arguments:
            image (Union[str, np.ndarray]): The image to plot. This can be a
                URL, a blob, or a numpy array. If it is a numpy array, it must
                be either 2D (greyscale), 3D (RGB), or 4D (RGBA).
            center_pos: Center pos
            rotation: Rotation of the img
                plane, in radians
            width (float: 10): The width of the final rendered plane
            height (float: 10): The height of the final rendered plane

        """
        super().__init__(*args, **kwargs)
        if isinstance(image, str):
            tex = ImageTexture(imageUri=image)
        elif isinstance(image, (list, np.ndarray)):
            if len(image.shape) == 2:
                # handle 2D (grayscale).
                # broadcast to rgba channels:
                image = np.array([image, image, image, np.ones(image.shape)]).T
            elif image.shape[-1] == 3:
                # handle RGB:
                image = np.dstack([image, np.ones(image.shape)])

            tex = DataTexture(data=image.astype(np.float32), type="FloatType")
        else:
            raise ValueError(f"Expected string or array, but got {type(image)}")
        plane = PlaneGeometry(width=width, height=height)
        mat = MeshBasicMaterial(map=tex)
        mesh = Mesh(geometry=plane, material=mat, position=center_pos)
        mesh.rotation = rotation if len(rotation) == 4 else [*rotation, "XYZ"]
        self.center = center_pos
        self.size = (width,height)
        self._objects.append(mesh)
    def get_bounding_box(self):
        x,y,z = self.center
        h,w = self.size
        return ((x-w/2.,y-h/2.,z),(x+w/2.,y+h/2.,z))
    def get_preferred_camera_view(self):
        return self.center


class GridLayer(LinesLayer):
    """
    Add a grid to the scene to help with orienting the viewer.

    Arguments:
        plane: Which axes to add grid lines along
        radius: The distance in + and - to stretch
        grid_size: The distance between grid marks
        color: The color of the grid

    """
    _LAYER_NAME = 'grid'
    def __init__(
        self,
        plane: str = "xz",
        radius: int = 10000,
        grid_size: int = 500,
        color: ColorRGB = (0.74, 0.74, 0.74),
    ):
        """
        Add a grid to the scene to help with orienting the viewer.

        Arguments:
            plane: Which axes to add grid lines along
            radius: The distance in + and - to stretch
            grid_size: The distance between grid marks
            color: The color of the grid

        """
        all_children = []
        if "z" in plane:
            all_children.extend(
                    [
                        [[-radius, 0, z], [radius, 0, z]]
                        for z in range(-radius, radius, grid_size)
                    ]
                )
        if "y" in plane:
            all_children.extend(
                    [
                        [[0, y, -radius], [0, y, radius]]
                        for y in range(-radius, radius, grid_size)
                    ]
                )
        if "x" in plane:
            all_children.extend(
                    [
                        [[x, 0, -radius], [x, 0, radius]]
                        for x in range(-radius, radius, grid_size)
                    ],
                )
        super().__init__(all_children, colors=color, width=0.5,)
class MeshLayer(CoordinateLayer):
    """
    Add a mesh to the scene.

    Arguments:
        mesh: Mesh object, with attributes verticies, faces
        obj: object filename
        normalize : Normalize the coordinates of the vertices
            to be between -1 and 1
        color: Color for the mesh
        alpha: transparency of the mesh

    """
    _LAYER_NAME = 'mesh'
    # pylint: disable=unused-variable,too-many-locals,too-many-branches
    def __init__(self,
        mesh: trimesh.Trimesh = None,
        obj: str = None,
        normalize: bool =False,
        color: Union[str,ColorRGB] ="#00bbee",
        alpha: float=1.,
        transform: Union[Callable, None] = None,
        *args,
        **kwargs
        ):
        """
        Add a mesh to the scene.

        Arguments:
            mesh: Mesh object, with attributes verticies, faces
            obj: object filename
            normalize : Normalize the coordinates of the vertices
                to be between -1 and 1
            color: Color for the mesh
            alpha: transparency of the mesh
            transform: a function to transform the vertices

        """
        if mesh is not None and obj is not None:
            raise ValueError('Received both mesh and obj')
        if isinstance(mesh, str):
            # perhaps this is a filename?
            try:
                mesh = trimesh.load(args[0])
            except Exception as e:
                raise ValueError(
                    "Did not understand arguments to method Figure#mesh"
                ) from e
        if isinstance(obj, np.ndarray):
            obj_data = obj
        elif isinstance(obj, list):
            obj_data = np.asarray(obj)
            # Do something with this obj_data?
        elif isinstance(obj, str):
            if "\n" in obj:
                # this is the file contents.
                raise NotImplementedError()
            else:
                try:
                    # open the mesh file
                    mesh = trimesh.load(obj)

                except Exception as e:
                    raise ValueError("Could not read file as OBJ") from e
        assert hasattr(mesh, "vertices") and hasattr(mesh, "faces"), "Invalid mesh object"
        if mesh is None:
            raise ValueError("Could not understand how to parse mesh.")

        if transform is None:
            transform = lambda x: x

        verts = transform(mesh.vertices)
        faces = mesh.faces

        if normalize:
            # Normalize the vertex indices to be between -1,1
            # Shifting these does change the coordinate system,
            # so visualizing multiple meshes won't work
            verts[:, 0] = _normalize_shift(verts[:, 0])
            verts[:, 1] = _normalize_shift(verts[:, 1])
            verts[:, 2] = _normalize_shift(verts[:, 2])

        geo = BufferGeometry(
            attributes={
                "position": BufferAttribute(
                    array=verts.astype("float32"),
                    normalized=False,
                    # dtype=np.float64
                ),
                "index": BufferAttribute(
                    array=faces.astype("uint64").ravel(),
                    normalized=False,
                    # dtype=np.float64,
                ),
            }
        )
        self._coords = verts
        transparent = alpha != 1.
        mat = MeshLambertMaterial(color=color, opacity=alpha, transparent=transparent)
        mesh = Mesh(geometry=geo, material=mat)
        geo.exec_three_obj_method("computeVertexNormals")
        super().__init__(*args, **kwargs)
        self._objects.append(mesh)
