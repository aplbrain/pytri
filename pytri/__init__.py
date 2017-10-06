#!/usr/bin/env python3

"""
Copyright 2017 The Johns Hopkins University Applied Physics Laboratory.

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

from IPython.core.display import display, HTML
from typing import abstractmethod, TypeVar
from uuid import uuid4

__version__ = "0.0.1"


class Layer:
    """
    The base (abstract) class for a Pytri/Substrate Layer.

    Must be implemented; this doesn't do anything.
    """

    @abstractmethod
    def export_data(self, **kwargs) -> dict:
        """
        Export the data to a JSON-like dict to be inlined in JavaScript.

        Arguments:
            Any

        Returns:
            dict: The data that a layer will require in JS.

        """
        pass


VisualizerType = TypeVar('VisualizerType', bound='Visualizer')
class Visualizer:
    """
    Base class for a Pytri Visualizer to interface with Substrate.

    This closely, but not identically, mirrors the substrate.js Visualizer.
    """

    def __init__(
            self,
            renderLayers=dict(),
            targetElement='viz',
            width=500,
            height=500):
        self.renderLayers = renderLayers
        self.targetElement = targetElement
        self.width = width
        self.height = height

    def add_layer(self, layer: Layer, name: str = None) -> Layer:
        """
        Add a layer to the scene.

        Arguments:
            layer (substrate.Layer): layer to add
            name (str: None): optional name. If not provided, a name will be
                generated randomly.

        Returns:
            Layer: A pointer to the inserted substrate layer

        """
        if not name:
            name = uuid4().hex
        self.renderLayers[name] = layer
        return layer

    def remove_layer(self, name: str) -> Layer:
        """
        Remove a layer to the scene.

        Arguments:
            name (str: None): name of layer

        Returns:
            Layer: A pointer to the removed substrate layer

        """
        pass

    def save(self, filename: str) -> VisualizerType:
        """
        Render the current scene down to disk.

        Arguments:
            filename (str): The file to save

        Returns:
            Visualizer: self

        """
        pass

    def show(self) -> VisualizerType:
        """
        Render the Visualizer element in the Jupyter notebook.

        Arguments:
            None

        Returns:
            Visualizer: self

        """
        display(HTML(self._to_html()))
        return self

    def _to_html(self) -> str:
        html_str = """
	    <html>
	    <body>
		<div id="render-target"></div>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/87/three.min.js"></script>
                <script src="./js/TrackballControls.js"></script>
                <script src="./js/Layer.js"></script>
                <script src="./js/Visualizer.js"></script>
                <script src="./js/bundle.js"></script>
            </body>
	    </html>
        """
        return html_str
