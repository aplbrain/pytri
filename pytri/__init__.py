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
from typing import List, Union
import uuid
from IPython.display import Javascript, HTML, display, clear_output
import networkx as nx
from networkx.readwrite import json_graph
import numpy as np
import requests

from . import version

__version__ = version.__version__


class pytri:
    """
    The global class for Pytri visualization.

    .
    """

    def __init__(self, **kwargs):
        """
        Create a new visualizer frame.

        Arguments:
            figsize (int, int): A 2-tuple of pixel sizes. Either may be None
                to auto-rescale in that axis.
            width (int): The width to set the figure
            height (int): The height to set the figure

        """
        self.debug = kwargs.get('debug', False)
        scripts = [
            # None listed.
            # Include all remote JS downloads here.
        ]
        # Construct a large JS file of all remote scripts:
        js = ""
        for script in scripts:
            js += requests.get(script).text.strip()

        # Execute substrate in the global namespace.
        s_path, _ = split(__file__)
        s_file = join(s_path, "js", "substrate.min.js")
        with open(s_file, "r") as fh:
            js += ";\n\n" + fh.read().strip()

        # Add GPU script to the global namespace.
        # TODO: Do not add this unless the system is needed.
        gpu_file = join(s_path, "js", "GPUParticleSystem.js")
        gpu_js = ""
        with open(gpu_file, "r") as fh:
            gpu_js += ";\n\n" + fh.read().strip()

        # Save JS files to self.
        self.js = js
        self.gpu_js = gpu_js

        # Generate a random ID for this pytri instance.
        self.uid = str(uuid.uuid4())

        # A set of all layer types that have been added (so that we don't
        # repeatedly download the same file)
        self.layer_types = set()

        # The list of layers added to this instance. Corresponds 1-to-1 with
        # the JS dictionary of renderLayers in the underlying substrate.
        self.layers = set()

        # Inject the JS into the scene.
        # Then add a pytri target, which is the substrate renderTarget attr.
        # Finally, create the Visualizer as a unique UUID keyvalue in the
        # global "V" object, and render it.
        width = kwargs.get("width", None)
        height = kwargs.get("height", 400)
        width, height = kwargs.get("figsize", (None, 400))
        self.width = width
        self.height = height
        if not width:
            width = "undefined"
        width = str(width)
        if not height:
            height = "undefined"
        height = str(height)
        self._display_exists = False
        display(HTML(
            "<script>{}</script>".format(self.js) +
            "<script>{}</script>".format(self.gpu_js) +
            """
            <script>
            window.V = window.V || {}
            </script>
            <style>
            .pytri-not-shown-yet {
                position: fixed;
                right: 150vw;
            }
            </style>
            <div id='pytri-target-"""+self.uid+"""' class="pytri-not-shown-yet"></div>"""  +
            """
            <script>
            V['"""+self.uid+"""'] = new window.substrate.Visualizer({
                targetElement: "pytri-target-"""+self.uid+"""",
                backgroundColor: new window.THREE.Color(0xffffff),
                renderLayers: {
                    // None yet!
                }
            });
            V['"""+self.uid+"""'].triggerRender();
            V['"""+self.uid+"""'].resize(""" + width + """, """ + height + """)
            </script>
            """
        ))

    def _execute_js(self, js, update=None):

        if self.debug:
            print(js)
        if self._display_exists and update is not False:
            display(Javascript(js), update=True, display_id="pytri-target-" + self.uid)
        else:
            display(Javascript(js), display_id="pytri-target-" + self.uid)
            self._display_exists = True

    def show(self):
        """
        Render the frame to the Jupyter notebook.

        Arguments:
            None

        """
        display(HTML("<div></div>"))
        if self.debug:
            _catch_code = "/* Visualizer DNE. */"
        else:
            _catch_code = ""
        self._execute_js(
            """
            try {
                document.querySelectorAll('.running')[0]
                    .querySelectorAll('.output .output_html')[0]
                        .appendChild(
                            document.getElementById('pytri-target-"""+self.uid+"""')
                        );
            } catch {""" + _catch_code + """}""",
            update=False
        )
        self._execute_js(
            "document.getElementById('pytri-target-"+self.uid+"').classList.remove('pytri-not-shown-yet')",
            update=False
        )
        self.resize(self.width, self.height)

    def resize(self, width="undefined", height="undefined") -> None:
        if not width:
            width = "undefined"
        width = str(width)
        if not height:
            height = "undefined"
        height = str(height)
        self._execute_js(
            """
            V['"""+self.uid+"""'].resize(""" + width + """, """ + height + """)
            """
        )

    def background(self, color: str) -> None:
        """
        Set the background color.

        Arguments:
            color (str): A hex-like string, like "0xff0000"

        """
        self._execute_js(
            """
            V['"""+self.uid+"""'].backgroundColor.set(""" + color + """)
            """
        )

    def remove_layer(self, name: str):
        """
        Remove a layer by name.

        Arguments:
            name (str)

        Returns:
            None

        """
        self._execute_js("""
            V['"""+self.uid+"""'].removeLayer('{}')
        """.format(name))
        self.layers.remove(name)

    def toggle_layer(self, name):
        """
        Toggle layer visibility by name.

        Arguments:
            name (str)

        Returns:
            None

        """
        self._execute_js("""
            V['"""+self.uid+"""'].renderLayers['"""+name+"""'].children.forEach(
                c => {
                    let shouldBeVisible = !c.visible;
                    c.visible = shouldBeVisible;
                })
        """)

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
        with open(file, "r") as fh:
            _js = fh.read().strip()
        return _js

    def _fetch_layer_github(self, fname: str) -> str:
        """
        Fetch a layer file from the aplbrain/substrate-layers repo.

        Arguments:
            fname (str)

        Returns:
            str JS
        """
        # Substrate-Layers repo, layers dir:
        fetch_url = "https://raw.githubusercontent.com/aplbrain/substrate-layers/layers/"
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

        if name is None:
            name = str(uuid.uuid4())

        if params is None:
            params = {}

        try:
            # Test that the file containers a `class Foo extends Layer`:
            layer_types = re.match(
                r"[\s\S]*class (\w+) extends .*Layer[\s\S]*",
                layer_js
            )
            if layer_types:
                layer_type = layer_types[1]
            # Overwrite window.layer_type
            inject_fmt = "window.{layer_type} = window.{layer_type} || {layer_js};"
            self._execute_js(inject_fmt.format(
                layer_type=layer_type,
                layer_js=layer_js))
            self.layer_types.add(layer_type)
        except TypeError as _:
            raise ValueError(
                "layer_js must include a class that extends Layer."
            )
        # Interpolate: V[id].addLayer(name, new Layer(params));
        _js = "V['{}'].addLayer('{}', new window.{}({}))".format(
            self.uid, name, layer_type, json.dumps(params)
        )
        self._execute_js(_js)

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
        name = str(uuid.uuid4())
        _js = "V['{}'].addLayer('{}', new window.substrate.layers.AxisLayer())".format(
            self.uid, name
        )
        self._execute_js(_js)
        self.layers.add(name)
        return name

    def imshow(
            self,
            data,
            position=None,
            rotation=None,
            scale=(10.,),
            name=None
    ) -> str:
        """
        Add an image plane to the scene.

        Arguments:
            data (np.ndarray)
            position (dict: x,y,z)
            scale (tuple of floats: (10,))

        Returns:
            str: Name, as inserted

        """
        from PIL import Image

        # use io object to hold data as png
        data_io = BytesIO()
        data_image = Image.fromarray(data).convert("RGB")
        data_image.save(data_io, format="PNG")

        # create a data URI using the io object
        data_io.seek(0, 0)
        data_uri = "data:image/png;base64,{}".format(b64encode(data_io.read()).decode("utf-8"))

        # send data to ImageLayer
        # 400 comes from the height in the show method
        _js = self._fetch_layer_file("ImageLayer.js")

        if len(scale) == 1:
            width = data.shape[1]
            height = data.shape[0]
            width = scale[0]*width/height
            height = scale[0]
        elif len(scale) == 2:
            width = scale[1]
            height = scale[0]
        else:
            raise ValueError("The scale tuple must have length one or two.")

        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}

        return self.add_layer(_js, {
            "dataURI": data_uri,
            "width": width,
            "height": height,
            "position": position,
            "rotation": rotation
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

        # TODO: Use particle system
        # TODO: Arrays of radii

        """
        if isinstance(data, np.ndarray):
            data = data.tolist()

        _js = self._fetch_layer_file("ScatterLayer.js")
        return self.add_layer(_js, {
            "data": data,
            "radius": r,
            "colors": c
        }, name=name)

    def graph(self, data, radius: Union[float, List[float]] = 0.15,
              node_color: Union[float, List[float]] = 0xbabe00,
              link_color: Union[float, List[float]] = 0x00babe,
              mesh_nodes: bool = False,
              name: str = None,) -> str:
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
            data = nx.relabel_nodes(data, lambda x: str(x))
            data = json_graph.node_link_data(data)
        _js = self._fetch_layer_file("GraphLayer.js")

        node_dict = {n['id']: n for n in data['nodes']}

        PARTICLE_RADIUS_SCALE = 50
        mult_radius: Union[float, List[float]]
        if isinstance(radius, (float, int)):
            if mesh_nodes:
                mult_radius = radius
            else:
                mult_radius = radius * PARTICLE_RADIUS_SCALE
        else:
            if mesh_nodes:
                mult_radius = radius
            else:
                mult_radius = [r * PARTICLE_RADIUS_SCALE for r in radius]

        return self.add_layer(_js, {
            "nodeDict": node_dict,
            "graph": data,
            "radius": mult_radius,
            "nodeColor": node_color,
            "linkColor": link_color,
            "meshNodes": mesh_nodes
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
        return self.add_layer(_js, {
            "data": data,
            "colors": c,
            "alpha": alpha
        }, name=name)

    def mesh(
            self,
            data,
            opacity=None,
            origin=None,
            scale=None,
            name=None) -> str:
        """
        Add a mesh to the scene. Currently only supports OBJ.

        Arguments:
            data (List[str]): OBJ file

        Returns:
            str: Name, as inserted

        """
        props = dict()
        if "\n" in data:
            props["data"] = data
        else:
            props["path"] = data

        if opacity:
            props["opacity"] = opacity
        if origin:
            props["origin"] = json.dumps(origin)
        if scale:
            props["scale"] = json.dumps(scale)

        if name is None:
            name = str(uuid.uuid4())
        _js = "V['{}'].addLayer('{}', new window.substrate.layers.MeshLayer({}))".format(
            self.uid, name, json.dumps(props)
        )
        self._execute_js(_js)
        self.layers.add(name)
        return name
