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

import uuid
from typing import Any, Iterable, List, Tuple, Union
from warnings import warn

import networkx as nx
import numpy as np
from IPython.display import display
from ipywidgets import HTML
from pythreejs import (
    AmbientLight, AxesHelper, BufferAttribute, BufferGeometry, DataTexture,
    DirectionalLight, Group, ImageTexture, LineMaterial, LineSegments2,
    LineSegmentsGeometry, Mesh, MeshBasicMaterial, MeshLambertMaterial,
    MeshNormalMaterial, OrbitControls, PerspectiveCamera, Picker,
    PlaneGeometry, Points, PointsMaterial, Renderer, Scene)

from pytri.layers import (AxesLayer, GraphLayer, GridLayer, ImshowLayer, Layer,
                          LinesLayer, MeshLayer, ScatterLayer)

_DEFAULT_FIGURE_WIDTH = 600
_DEFAULT_FIGURE_HEIGHT = 400

__version__ = "2.0.1"

class Figure:
    """
    Generic class for a new Pytri figure.

    """
    # pylint: disable=protected-access,attribute-defined-outside-init
    def __init__(self,
        figsize: Tuple[int, int]=None,
        background: Union[str, Tuple[float, float, float]]=None,
        register_default:bool=True,
        ):
        """
        Create a new figure.

        All arguments are optional.

        Arguments:
            figsize: The size to make the visualization
            background: color to make background
            register_default: register the default layers
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
        self._click_callbacks = dict()
        self.controls = [OrbitControls(controlling=self._camera)]
        self._controllable_layers = []
        self.background = background
        if register_default:
            for layer in [MeshLayer,
                    ScatterLayer,
                    LinesLayer,
                    AxesLayer,
                    GraphLayer,
                    ImshowLayer,
                    GridLayer,]:
                self.register_layer(layer)
    @staticmethod
    def _new_id():
        return str(uuid.uuid4())
    def _layer_decorator(self, cls):
        def fn(*args, **kwargs):
            inst = cls(*args, **kwargs)
            _id = self._add_layer(inst)
            inst._id = _id
            return inst
        return fn
    def register_layer(self, cls:Layer, layername:str=None):
        """
        Registers the Layer class cls with the name layername such that
        calling fig.layername instantiates the class.
        """
        layer = cls._LAYER_NAME if layername is None else layername
        self.__dict__[layer] = self._layer_decorator(cls)

    def _add_layer(self, layer: Layer) -> str:
        object_set = layer.group
        _id = self._new_id()
        for c in object_set.children:
            c.name = _id
        self._click_callbacks[_id] = layer._on_click
        self._layer_lookup[_id] = object_set
        return _id

    def recenter_camera(self, target:Union[Layer, Tuple[float, float, float], None]=None):
        """
        Re-orient the camera to view everything in the scene or a particular layer.
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
            self._scene.remove(l.group)
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
    def _interact_callback(self, change):
        layer_id = change["owner"].object.name

        self.html.value = str(self._click_callbacks[layer_id](change["owner"]))
    def show(self):
        """
        Render the scene for the viewer.

        This method can be called serveral times in order to generate several
        visualizations which are "yoked" together.

        """
        scene = Scene(
            background=self.background,
            children=[
                self._camera,
                AmbientLight(color="#cccccc"),
            ],
        )
        g = Group()
        for _,v in self._layer_lookup.items():
            g.add(v)

        p = Picker(controlling=g,event='click')
        p.observe(self._interact_callback, names=["point"])
        self.html = HTML("")
        scene.add(g)
        self.controls.append(p)

        self._renderer = Renderer(
            width=self._figsize[0],
            height=self._figsize[1],
            camera=self._camera,
            scene=scene,
            alpha=True,
            clearOpacity=0,
            controls=self.controls,
        )
        self._scene = scene
        display(self.html, self._renderer)
