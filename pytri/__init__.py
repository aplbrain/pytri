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

from base64 import b64encode
from io import BytesIO
import json
from os.path import join, split
import re
from typing import Sequence, Union
import uuid
from IPython.display import Javascript, HTML, display
import networkx as nx
from networkx.readwrite import json_graph
import numpy as np
import requests


__version__ = "0.2.0"


class pytri:
    """
    The global class for Pytri visualization.

    .
    """

    def __init__(self):
        """
        Create a new visualizer frame.

        Arguments:
            None

        """
        scripts = [
            "https://threejs.org/examples/js/controls/TrackballControls.js",
        ]

        threesrc = requests.get("https://threejs.org/build/three.js").text.split('\n')
        threesrc = threesrc[6:-2]

        js = "exports = window.THREE || {}; " + "\n".join(threesrc) + "window.THREE = exports;"

        for script in scripts:
            js += requests.get(script).text.strip()

        s_path, _ = split(__file__)
        s_file = join(s_path, "js", "substrate.min.js")
        with open(s_file, 'r') as fh:
            js += ";\n\n" + fh.read().strip()

        gpu_file = join(s_path, "js", "GPUParticleSystem.js")
        js2 = ""
        with open(gpu_file, 'r') as fh:
            js2 += ";\n\n" + fh.read().strip()

        self.js = js
        self.gpu_js = js2
        self.uid = str(uuid.uuid4())
        self.layers = set()

        display(HTML(
            "<div id='pytri-target-decoy'></div>" +
            "<script>{}</script>".format(self.js) +
            "<script>{}</script>".format(self.gpu_js) +
            """
            <script>
            window.V = window.V || {}
            V['"""+self.uid+"""'] = new Visualizer({
                targetElement: "pytri-target-decoy",
                backgroundColor: new window.THREE.Color(0xffffff),
                renderLayers: {
                    // None yet!
                }
            });
            V['"""+self.uid+"""'].init();
            let dd = document.getElementById("pytri-target-decoy");
            dd.remove();
            </script>
            """
        ))

    def show(self):
        """
        Render the frame to the Jupyter notebook.

        Arguments:
            None

        """
        display(HTML(
            """<div id='pytri-target-"""+self.uid+"""'></div>"""  +
            """
            <script>
            V['"""+self.uid+"""'].props.targetElement = "pytri-target-"""+self.uid+"""";
            V['"""+self.uid+"""'].triggerRender();
            V['"""+self.uid+"""'].resize(undefined, 400)
            </script>
            """
        ))

    def remove_layer(self, name):
        """
        Remove a layer by name.

        Arguments:
            name (str)

        Returns:
            None

        """
        display(Javascript("""
            V['"""+self.uid+"""'].removeLayer('{}')
        """.format(name)))
        self.layers.remove(name)

    def clear(self):
        """
        Remove all layers from scene.

        Arguments:
            None

        Returns:
            None

        """
        store_layers = {name for name in self.layers}
        for name in store_layers:
            self.remove_layer(name)

    def _fetch_layer_file(self, fname: str) -> str:
        """
        Fetch a layer file from local package resources.

        Arguments:
            fname (str)

        Returns:
            str JS

        """
        _js = ""
        path, _ = split(__file__)
        file = join(path, "js", fname)
        with open(file, 'r') as fh:
            _js = fh.read().strip()
        return _js

    def _fetch_layer_github(self, fname: str) -> str:
        """
        Fetch a layer file from the iscoe/substrate-layers repo.

        Arguments:
            fname (str)

        Returns:
            str JS
        """
        # Substrate-Layers repo, layers dir:
        fetch_url = "https://raw.githubusercontent.com/iscoe/substrate-layers/layers/"
        full_url = fetch_url + fname
        _js = requests.get(full_url).text
        return _js

    def add_layer(self, layer_js: str, params: dict = None, name: str = None) -> str:
        """
        Add a custom JS layer to the visualization.

        Arguments:
            layer_js (str): The contents of a JS file
            params (dict): The data to pass into the layer constructor
            name (str): Optional name for the layer

        Returns:
            str: Name, as inserted

        """
        if layer_js.startswith("http"):
            fetch_url = layer_js
            layer_js = requests.get(fetch_url).text

        _js = layer_js

        if name is None:
            name = str(uuid.uuid4())

        if params is None:
            params = {}

        try:
            # Test that the file containers a `class Foo extends Layer`:
            _js_layer_name = re.match(
                r"[\s\S]*class (\w+) extends .*Layer[\s\S]*", _js
            )[1]
        except TypeError as _:
            raise ValueError(
                "layer_js must include a class that extends Layer."
            )
        # Interpolate: V[id].addLayer(name, new Layer(params));
        _js += "V['{}'].addLayer('{}', new {}({}))".format(
            self.uid, name, _js_layer_name, json.dumps(params)
        )
        display(Javascript(_js))

        self.layers.add(name)
        return name

    def axes(self) -> str:
        """
        Add axes to the visualization.

        Arguments:
            None

        Returns:
            str: Name, as inserted

        """
        _js = """
            class AxisLayer extends Layer {
                requestInit(scene) {
                    let axes = new window.THREE.AxisHelper(5);
                    this.children.push(axes)
                    scene.add(axes)
                }
            }
        """
        return self.add_layer(_js, name='axes')

    def imshow(
            self,
            data,
            position={"x": 0, "y": 0, "z": 0},
            scale=10.,
            name=None
    ) -> str:
        """
        Add an image plane to the scene.

        Arguments:
            data (np.ndarray)
            position (dict: x,y,z)
            scale (float: 10)

        Returns:
            str: Name, as inserted

        """
        from PIL import Image

        # handle different input types
        mode_map = {
            2: "L",
            3: "RGB",
            4: "RGBA"}
        mode = mode_map[len(data.shape)]
        if mode == "L":
            data = np.uint8(data)

        # use io object to hold data as png
        data_io = BytesIO()
        data_image = Image.fromarray(data, mode)
        data_image.save(data_io, format="PNG")

        # create a data URI using the io object
        data_io.seek(0, 0)
        data_uri = "data:image/png;base64,{}".format(b64encode(data_io.read()).decode("utf-8"))

        # send data to ImageLayer
        # 400 comes from the height in the show method
        _js = self._fetch_layer_file("ImageLayer.js")

        width = data.shape[1]
        height = data.shape[0]

        return self.add_layer(_js, {
            "dataURI": data_uri,
            "width": scale*width/height,
            "height": scale,
            "position": position,
        }, name=name)

    def scatter(self, data, r=0.15, c=0x00babe, name=None) -> str:
        """
        Add a 3D scatter to the scene.

        Arguments:
            data (np.ndarray)
            r (float | list)
            c (hex | list)

        Returns:
            str: Name, as inserted

        """
        if isinstance(data, np.ndarray):
            data = data.tolist()

        _js = self._fetch_layer_file("ScatterLayer.js")
        #_js = self._fetch_layer_github("ScatterLayer.js")
        return self.add_layer(_js, {
            "data": data,
            "radius": r,
            "colors": c
        }, name=name)

    def graph(self, data, radius: Union[float, Sequence[float]] = 0.15,
              node_color: Union[float, Sequence[float]] = 0xbabe00,
              link_color: Union[float, Sequence[float]] = 0x00babe, name: str = None) -> str:
        """
        Add a graph to the visualizer.

        Arguments:
            data (networkx.Graph)
            radius (float | list)
            node_color (float | list)
            link_color (float | list)
            name (str)

        Returns:
            str: name of the layer

        """
        if isinstance(data, nx.Graph):
            data = json_graph.node_link_data(data)

        _js = self._fetch_layer_file("GraphLayer.js")
        return self.add_layer(_js, {
            "graph": data,
            "radius": radius,
            "nodeColor": node_color,
            "linkColor": link_color,
        }, name=name)


    def large_graph(self, data, radius: Union[float, Sequence[float]] = 2,
                    node_color: Union[float, Sequence[float]] = 0xbabe00,
                    link_color: Union[float, Sequence[float]] = 0x00babe,
                    name: str = None) -> str:
        """
        Add a large graph to the visualizer using the GPU particle system.

        Arguments:
            data (networkx.graph)
            radius (float | list)
            node_color (float | list)
            link_color (float | list)
            name (str)

        Returns:
            str: name of the layer.
        """
        if isinstance(data, nx.Graph):
            data = json_graph.node_link_data(data)

        _js = self._fetch_layer_file("LargeGraphLayer.js")
        return self.add_layer(_js, {
            "graph": data,
            "nodeSize": radius,
            "nodeColor": node_color,
            "linkColor": link_color,
        }, name=name)


    def fibers(self, data, c=0xbabe00, alpha=0.5, name=None) -> str:
        """
        Add a fiber group to the visualizer.

        Arguments:
            data (List[][])
            c (hex)
            alpha (0..1)

        Returns:
            str: Name, as inserted

        """
        if isinstance(data, np.ndarray):
            data = data.tolist()

        _js = self._fetch_layer_file("FibersLayer.js")
        #_js = self._fetch_layer_github("FibersLayer.js")
        return self.add_layer(_js, {
            "data": data,
            "colors": c,
            "alpha": alpha
        }, name=name)

    def mesh(self, data, name=None) -> str:
        """
        Add a mesh to the scene. Currently only supports OBJ.

        Arguments:
            data (List[str]): OBJ file

        Returns:
            str: Name, as inserted

        """
        display(Javascript(
            url="https://raw.githubusercontent.com/mrdoob/three.js" +
            "/master/examples/js/loaders/OBJLoader.js"
        ))

        _js = self._fetch_layer_file("MeshLayer.js")
        return self.add_layer(_js, {
            "data": data
        }, name=name)
