from abc import ABC, abstractmethod,abstractproperty
from typing import Tuple,Iterable,Union
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
    Group,
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

class Layer(ABC):
    
    def __init__(self, *args, **kwargs) -> None:
        self._id = None
        self._objects = []
        self._group = None
    def on_click(self, MouseEvent) -> any:
        ...
    
    def on_keyup(self, KeyboardEvent) -> any:
        ...
    @abstractmethod
    def get_bounding_box(self) -> Tuple[Tuple, Tuple]:
        ...
    @abstractmethod
    def get_preferred_camera_view(self) -> Tuple[Tuple]:
        return None
    @property
    def group(self) -> Group:
        if self._group is None:
            self._group = Group()
            for obj in self._objects:
                self._group.add(obj)

        return self._group
    def affine(self) -> np.ndarray:
        return self.group.matrix
        
    def set_affine(self, a: np.ndarray):
        self._affine = a
        sc = self.group
        sc.matrix = self._affine
    def rotate(self, x,y,z,order="XYZ"):
        sc = self.group
        sc.rotation = (x,y,z,order)
    def translate(self, x,y,z):
        sc = self.group
        xyz = np.array(sc.position)
        sc.position = tuple(xyz + [x,y,z])
    

class AxesLayer(Layer):
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
        if not (hasattr(self, '_mean_coords')):
            self._calc_coord_metrics()
        return self._mean_coords
class LinesLayer(CoordinateLayer):

    def __init__(self,lines, colors=None, width=10, *args, **kwargs):
        """
        Plots a series of line segments.

        Arguments:
            lines: list of lists of 2-tuples of 3coords
            colors: Either list of list of 2-tuples of 3coords, 
            a list of lists of 3coords, or a single 3 tuple (RGB) applied to all lines

        Returns:
            UUID

        """
        super().__init__(*args, **kwargs)
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
    def __init__(self, graph : nx.Graph, **kwargs):
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
        super().__init__(scatter_points,lines=lines, size=kwargs.get("node_size", 5),width=kwargs.get("edge_width", 5))
        
class ImshowLayer(Layer):
    def __init__(
        self, 
        image: Union[str, np.ndarray],
        center_pos: Tuple[float, float, float] = (0, 0, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
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
            center_pos (Tuple[float, float, float]: (0,0,0)): Center pos
            rotation (Tuple[float, float, float]: (0,0,0)): Rotation of the img
                plane, in radians
            width (float: 10): The width of the final rendered plane
            height (float: 10): The height of the final rendered plane

        Returns:
            UUID

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
    def __init__(
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
    def __init__(self,mesh=None,obj=None, normalize=False,color="#00bbee", alpha=1.,*args, **kwargs):
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
       
        if hasattr(mesh, "vertices") and hasattr(mesh, "faces"):
            mesh = mesh
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
        
        self._objects.append(mesh)
