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

import uuid
import json
from os.path import join, split
import requests
import numpy as np
from IPython.display import Javascript, HTML, display
import networkx as nx
from networkx.readwrite import json_graph


__version__ = "0.0.2"


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

        self.js = js
        self.uid = str(uuid.uuid4())
        self.layers = set()

        display(HTML(
            "<div id='pytri-target-decoy'></div>" +
            "<script>{}</script>".format(self.js) +
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
        store_layers = {name for name in self.layers}
        for name in store_layers:
            self.remove_layer(name)

    def axes(self):
        """
        Add axes to the visualization.

        Arguments:
            None

        Returns:
            None

        """
        display(Javascript("""
            class AxisLayer extends Layer {
                requestInit(scene) {
                    let axes = new window.THREE.AxisHelper(5);
                    this.children.push(axes)
                    scene.add(axes)
                }
            }
            V['"""+self.uid+"""'].addLayer('axes', new AxisLayer())
        """))
        self.layers.add('axes')

    def scatter(self, data, r=0.15, c=0x00babe):
        """
        Add a 3D scatter to the scene.

        Arguments:
            data (np.ndarray)
            r (float | list)
            c (hex | list)

        Returns:
            None

        """
        d = data.tolist()
        _js = ""
        scatter_path, _ = split(__file__)
        scatter_file = join(scatter_path, "js", "ScatterLayer.js")
        with open(scatter_file, 'r') as fh:
            _js += ";\n\n" + fh.read().strip()
        _js += ("""
        console.log("butts")
        V['"""+self.uid+"""'].addLayer('scatter', new ScatterLayer({{
            data: {},
            radius: {},
            colors: {}
        }}))
        """.format(
            json.dumps(d),
            r,
            c
        ))
        display(Javascript(_js))
        self.layers.add('scatter')


    def graph(self, data, r=0.15, c=0xbabe00):
        """
        Add a graph to the visualizer.

        Arguments:
            data (networkx.graph)
            r (float | list)
            c (float | list)

        Returns:
            None

        """
        if isinstance(data, nx.Graph):
            data = json_graph.node_link_data(data)

        _js = ""
        graph_path, _ = split(__file__)
        graph_file = join(graph_path, "js", "GraphLayer.js")
        with open(graph_file, 'r') as fh:
            _js += ";\n\n" + fh.read().strip()
        _js += ("""
        V['"""+self.uid+"""'].addLayer('graph', new GraphLayer({{
            data: {},
            radius: {},
            colors: {}
        }}))
        """.format(
            json.dumps(data),
            r,
            c
        ))
        display(Javascript(_js))

    def fibers(self, data, c=0xbabe00, alpha=0.5):
        """
        Add a fiber group to the visualizer.

        Arguments:
            data (List[][])
            c (hex)
            alpha (0..1)

        Returns:
            None

        """
        if isinstance(data, np.ndarray):
            data = data.tolist()

        _js = ""
        fibers_path, _ = split(__file__)
        fibers_file = join(fibers_path, "js", "FibersLayer.js")
        with open(fibers_file, 'r') as fh:
            _js += ";\n\n" + fh.read().strip()

        _js += """
        V['"""+self.uid+"""'].addLayer('fibers', new FibersLayer({{
            data: {},
            colors: {},
            alpha: {},
        }}))
        """.format(
            json.dumps(data),
            c,
            alpha
        )
        display(Javascript(_js))
        self.layers.add('graph')
