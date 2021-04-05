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

from typing import Any, Union, List, Iterable, Tuple
from IPython.display import display
import uuid
import numpy as np
import networkx as nx

import trimesh

from pythreejs import (
    # Cinematography:
    AmbientLight,
    DirectionalLight,
    Scene,
    PerspectiveCamera,
    Renderer,
    BufferAttribute,
    OrbitControls,
    DataTexture,
    ImageTexture,
    AxesHelper,
    Points,
    BufferGeometry,
    PointsMaterial,
    PlaneGeometry,
    # for meshes:
    Mesh,
    MeshBasicMaterial,
    MeshNormalMaterial,
    MeshLambertMaterial,
    # for lines:
    LineSegmentsGeometry,
    LineMaterial,
    LineSegments2,
)

from .utils import CIRCLE_MAP, _normalize_shift

_DEFAULT_FIGURE_WIDTH = 600
_DEFAULT_FIGURE_HEIGHT = 400


class Figure:
    """
    Generic class for a new Pytri figure.

    """

    def __init__(self, **kwargs):
        """
        Create a new figure.

        All arguments are optional.

        Arguments:
            figsize (Tuple[float, float]): The size to make the visualization

        """
        self._figsize = kwargs.get(
            "figsize", (_DEFAULT_FIGURE_WIDTH, _DEFAULT_FIGURE_HEIGHT)
        )

        self._layer_lookup = dict()
        imscale = kwargs.get("imscale", 1)

        self._object_centers = []
        self._object_bounding_box_maxes = []

        self._camera = PerspectiveCamera(
            position=tuple(np.array([0, 0, 5]) * imscale),
            up=(0, 1, 0),
            far=1e6,
            aspect=self._figsize[0] / self._figsize[1],
            children=[
                DirectionalLight(
                    color="#ffffff",
                    position=tuple(np.array([3, 5, 1]) * imscale),
                    intensity=0.6,
                ),
            ],
        )
        self._scene = Scene(
            background=kwargs.get("background", None),
            children=[
                self._camera,
                AmbientLight(color="#cccccc"),
            ],
        )
        self._renderer = Renderer(
            width=self._figsize[0],
            height=self._figsize[1],
            camera=self._camera,
            scene=self._scene,
            alpha=True,
            clearOpacity=0,
            controls=[OrbitControls(controlling=self._camera)],
        )

    @staticmethod
    def _new_id():
        return str(uuid.uuid4())

    def _add_layer(self, object_set: Union[List, Any]) -> str:
        if not isinstance(object_set, list):
            object_set = [object_set]
        _id = self._new_id()
        self._layer_lookup[_id] = object_set
        for obj in object_set:
            self._scene.add(obj)
        return _id

    def _reposition_camera_on_bbs(self):
        """
        Re-orient the camera to view everything in the scene.
        """
        max_vector = np.max(self._object_bounding_box_maxes, axis=0)
        min_vector = np.min(self._object_bounding_box_maxes, axis=0)
        range_vector = max_vector - min_vector
        average_center = np.mean(self._object_centers, axis=0)
        # This seems to give a good representation of the vector, might change in the future
        self._camera.position = tuple(average_center + range_vector * 2)
        self._camera.lookAt(tuple(average_center))

    def remove(self, object_set: Union[List[str], str]) -> bool:
        """
        Remove a single layer from the scene.

        Use the UUID you get back from the layer-addition methods
        to identify which items to remove.

        Arguments:
            object_set (Union[List[str], str]): The object(s) to remove

        Returns:
            True, if successful

        """
        if not isinstance(object_set, list):
            object_set = [object_set]
        for obj in object_set:
            self._scene.remove(self._layer_lookup[obj])
        return True

    def clear(self):
        """
        Clear all layers from the scene.

        Arguments:
            None

        Returns:
            None

        """
        for key in self._layer_lookup.keys():
            self.remove(key)

    def show(self):
        """
        Render the scene for the viewer.

        This method can be called serveral times in order to generate several
        visualizations which are "yoked" together.

        """
        display(self._renderer)

    def axes(self, size: float = 20):
        """
        Add a set of axes to the origin.

        Arguments:
            size (float: 20): The length of each axis into the positive values.

        Returns:
            UUID

        """
        axes = AxesHelper(size=size)
        return self._add_layer(axes)

    def graph(self, graph: nx.Graph, **kwargs):
        """
        Plot a networkx graph.

        Arguments:
            pos (List[3coords], Dict[Hashable, 3coords]): positions to
                assign to each node.
            pos_attribute (str): The node attribute to use as a 3coord.
            edge_width (int: 5): The line width to pass to Figure#lines

        Returns:
            UUID

        """
        # This is the same as adding a scatter and a lines layer.
        if "pos_attribute" in kwargs:
            attr = kwargs.get("pos_attribute")
            pos = {n: a[attr] for n, a in graph.nodes(data=True)}
        elif "pos" in kwargs:
            pos = kwargs.get("pos")
            if isinstance(pos, list):
                pos = {n: p for n, p in zip(graph.nodes(), pos)}
        else:
            try:
                pos = {n: p["pos"] for n, p in graph.nodes(data=True)}
            except Exception as e:
                raise ValueError("You must pass a valid position argument.") from e

        scatter_points = [i for i in pos.values()]

        lines = [[pos[u], pos[v]] for u, v in graph.edges()]

        self.lines(lines, width=kwargs.get("edge_width", 5))
        self.scatter(scatter_points, size=kwargs.get("node_size", 5))

    def lines(self, lines, colors=None, width=10):
        """
        Plots a series of line segments.

        Arguments:
            lines: list of lists of 2-tuples of 3coords
            colors: Either list of list of 2-tuples of 3coords,
                or a list of lists of 3coords

        Returns:
            UUID

        """
        colors = colors if (not colors is None) else [[0, 0, 0] for _ in lines]

        colors = np.array([c if len(c) == 2 else [c, c] for c in colors])

        geo = LineSegmentsGeometry(
            positions=lines,
            colors=colors,
        )
        mat = LineMaterial(linewidth=width, vertexColors="VertexColors")
        return self._add_layer(LineSegments2(geo, mat))

    def matshow(self):
        raise NotImplementedError()

    def imshow(
        self,
        image: Union[str, np.ndarray],
        center_pos: Tuple[float, float, float] = (0, 0, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        width: float = 10,
        height: float = 10,
    ):
        """
        Plot an image as a plane.

        Arguments:
            image (Union[str, np.ndarray]): The image to plot. This can be a
                URL, a blob, or a numpy array. If it is a numpy array, it must
                be either 2D (greyscale), 3D (RGB), or 4D (RGBA).
            center_pos (Tuple[float, float, float]: (0,0,0)): Center pos
            rotation (Tuple[float, float, float]: (0,0,0)): Rotation of the img
                plane, in radians
            width (float: 10): The width of the final rendered plane
            height (float: 10): The height of the final rendered plane

        Returns:
            UUID

        """
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

            tex = DataTexture(data=image, type="FloatType")
        else:
            raise ValueError(f"Expected string or array, but got {type(image)}")
        plane = PlaneGeometry(width=width, height=height)
        mat = MeshBasicMaterial(map=tex)
        mesh = Mesh(geometry=plane, material=mat)
        mesh.rotation = rotation if len(rotation) == 4 else [*rotation, "XYZ"]
        self._add_layer(mesh)

    def grid(
        self,
        plane: str = "xz",
        radius: int = 10000,
        grid_size: int = 500,
        color: Tuple[float, float, float] = (0.74, 0.74, 0.74),
    ):
        """
        Add a grid to the scene to help with orienting the viewer.

        Arguments:
            plane (str: "xz"): Which axes to add grid lines along
            radius (float: 10000): The distance in + and - to stretch
            grid_size (float: 500): The distance between grid marks
            color (Tuple[float, float, float]): The color of the grid

        Returns:
            UUID

        """
        all_children = []
        if "z" in plane:
            all_children.append(
                self.lines(
                    [
                        [[-radius, 0, z], [radius, 0, z]]
                        for z in range(-radius, radius, grid_size)
                    ],
                    colors=[color for _ in range(-radius, radius, grid_size)],
                    width=0.5,
                )
            )

        # if "y" in plane:
        #     all_children.append(
        #         self.lines(
        #             [
        #                 [[0, y, -radius], [0, y, radius]]
        #                 for y in range(-radius, radius, grid_size)
        #             ],
        #             colors=[color for _ in range(-radius, radius, grid_size)],
        #             width=0.5,
        #         )
        #     )
        if "x" in plane:
            all_children.append(
                self.lines(
                    [
                        [[x, 0, -radius], [x, 0, radius]]
                        for x in range(-radius, radius, grid_size)
                    ],
                    colors=[color for _ in range(-radius, radius, grid_size)],
                    width=0.5,
                )
            )
        return all_children

    def scatter(self, *args, **kwargs):
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

        pts = None

        if len(args) == 1:
            if isinstance(args[0], (np.ndarray, Iterable)):
                pts = np.asarray(args[0])

        if len(args) == 3 and isinstance(args[0], (list, np.ndarray)):
            pts = np.asarray([i for i in zip(args[0], args[1], args[2])])

        if pts is None:
            raise ValueError("Unsupported arguments to scatter.")

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
        return self._add_layer(p)

    def mesh(self, *args, **kwargs):
        """
        Add a mesh to the scene.

        There are several supported types of argument.

            Figure#mesh(obj=Union[List[List], np.ndarray])

            Figure#mesh(str)

        Arguments:
            normalize (bool: False): Normalize the coordinates of the vertices
                to be between -1 and 1

        Returns:
            UUID

        """
        mesh = None
        if len(args) > 0 and isinstance(args[0], str):
            # perhaps this is a filename?
            try:
                mesh = trimesh.load(args[0])
            except Exception as e:
                raise ValueError(
                    "Did not understand arguments to method Figure#mesh"
                ) from e

        if "obj" in kwargs:
            if isinstance(kwargs["obj"], np.ndarray):
                obj_data = kwargs["obj"]
            elif isinstance(kwargs["obj"], list):
                obj_data = np.asarray(kwargs["obj"])
                # Do something with this obj_data?
            elif isinstance(kwargs["obj"], str):
                if "\n" in kwargs["obj"]:
                    # this is the file contents.
                    raise NotImplementedError()
                else:
                    try:
                        # open the mesh file
                        mesh = trimesh.load(kwargs["obj"])

                    except Exception as e:
                        raise ValueError("Could not read file as OBJ") from e
        if "mesh" in kwargs:
            if hasattr(kwargs["mesh"], "vertices") and hasattr(kwargs["mesh"], "faces"):
                mesh = kwargs["mesh"]
        if mesh is None:
            raise ValueError("Could not understand how to parse mesh.")

        _transform = kwargs.get("transform", lambda x: x)

        verts = _transform(mesh.vertices)
        faces = mesh.faces

        if kwargs.get("normalize", False):
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

        self._object_bounding_box_maxes.append(np.max(verts, axis=0))
        self._object_centers.append(np.mean(verts, axis=0))

        geo.exec_three_obj_method("computeVertexNormals")
        color = kwargs.get("color", "#00bbee")

        mesh = Mesh(geometry=geo, material=MeshLambertMaterial(color=color))
        return self._add_layer(mesh)
