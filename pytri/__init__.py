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
from warnings import warn
from pytri.layers import Layer

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
    Picker,
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



_DEFAULT_FIGURE_WIDTH = 600
_DEFAULT_FIGURE_HEIGHT = 400


class Figure:
    """
    Generic class for a new Pytri figure.

    """

    def __init__(self, 
        figsize: Tuple[int, int]=None, 
        background: Union[str, Tuple[float, float, float]]=None,
        **kwargs):
        """
        Create a new figure.

        All arguments are optional.

        Arguments:
            figsize (Tuple[float, float]): The size to make the visualization

        """
        if figsize is None:
            figsize = (_DEFAULT_FIGURE_WIDTH, _DEFAULT_FIGURE_HEIGHT)
        self._figsize = figsize

        self._layer_lookup = dict()

        self._camera = PerspectiveCamera(
            position=tuple(np.array([0, 0, 5])),
            up=(0, 1, 0),
            far=1e6,
            aspect=self._figsize[0] / self._figsize[1],
            children=[
                DirectionalLight(
                    color="#ffffff",
                    position=tuple(np.array([3, 5, 1])),
                    intensity=0.6,
                ),
            ],
        )
        self._scene = Scene(
            background=background,
            children=[
                self._camera,
                AmbientLight(color="#cccccc"),
            ],
        )
        self.controls = [OrbitControls(controlling=self._camera)]
        

    @staticmethod
    def _new_id():
        return str(uuid.uuid4())
    def _layer_decorator(self, cls):
        def fn(*args, **kwargs):
            inst = cls(*args, **kwargs)
            _id = self._add_layer(inst.group)
            inst._id = _id
            return inst
        return fn
    def register_layer(self, layer, cls):
        self.__dict__[layer] = self._layer_decorator(cls)

    def _add_layer(self, object_set: Union[List, Any]) -> str:
        if not isinstance(object_set, list):
            object_set = [object_set]
        _id = self._new_id()
        self._layer_lookup[_id] = object_set
        for obj in object_set:
            self._scene.add(obj)
        return _id

    def recenter_camera(self, target:Union[Layer, Tuple[float, float, float], None]=None):
        """
        Re-orient the camera to view everything in the scene.
        Arguments:

            target: Either a Layer, a vector, or None. If none, tries its best
                to give the viewpoint of everything in the scene.

                If a layer, views the layer based on preferred camera view

                If a vector, points the camera at the vector.

        """
        
        if target is None:
            try:
                pcv = [l.get_preferred_camera_view() for l in self._layer_lookup.values()]
                average_center = np.mean(pcv, axis=0)
            except ValueError:
                warn("No objects to center around")
                target = target or np.array(self.controls[0].target)
            if target is None:
                target = average_center
        elif isinstance(target, Iterable):
            target = tuple(target.astype(np.float32))
        elif isinstance(target, Layer):
            target = tuple(target.get_preferred_camera_view())
        self.controls.target = target
    def remove(self, layer: Union[Layer, Iterable[Layer]]) -> bool:
        """
        Remove a single layer from the scene.

        Use the UUID you get back from the layer-addition methods
        to identify which items to remove.

        Arguments:
            layer: Layer or iterable of layers to remove.

        Returns:
            True, if successful

        """
        if not isinstance(layer, list):
            layer = [layer]
        for l in layer:
            for obj in l._objects:
                self._scene.remove(obj)
        return True

    def clear(self):
        """
        Clear all layers from the scene.

        Arguments:
            None

        Returns:
            None

        """
        for layer in self._layer_lookup.values():
            self.remove(layer)

    def show(self):
        """
        Render the scene for the viewer.

        This method can be called serveral times in order to generate several
        visualizations which are "yoked" together.

        """
        self._renderer = Renderer(
            width=self._figsize[0],
            height=self._figsize[1],
            camera=self._camera,
            scene=self._scene,
            alpha=True,
            clearOpacity=0,
            controls=self.controls,
        )
        display(self._renderer)
