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
        <script src="./js/bundle.js"></script>
        <script>
            class Axes extends Layer {
                requestInit(scene) {
                    scene.add(new window.THREE.AxisHelper(5));
                }
            }

            class GraphLayer extends Layer {

                constructor(props) {
                    super(props);
                    this.getData = props.getData;  // get data = function that returns dict with nodes and edges
                }

                requestInit(scene) {
                    let self = this;
                    self.needsUpdate = true;

                    let data = self.getData();
                    self.children = [];

                    var nodesGeometry = new THREE.Geometry();
                    // var nodesGeometry = new THREE.Geometry();
                    var nodeGeometry = new THREE.SphereGeometry(0.5, 8, 8);
                    for (var n in data.nodes) {
                        var sphere = new THREE.Mesh(
                            nodeGeometry,
                            new THREE.MeshBasicMaterial({
                                color: 0xff0022,
                                transparent: true,
                                opacity: 1
                            })
                        );
                        sphere._id = n;
                        sphere.position.set(
                            data.nodes[n].x, data.nodes[n].y, data.nodes[n].z);
                        self.children.push(sphere);
                        scene.add(sphere);
                    }

                    for (var i = 0; i < data.edges.length; i++) {
                        var edgeGeometry = new THREE.Geometry();
                        var edgeMaterial = new THREE.LineBasicMaterial({
                            color: 0xbabe00 * data.edges[i].weight,
                            transparent: true,
                            opacity: data.edges[i].weight,
                            linewidth: data.edges[i].weight,
                        });
                        edgeGeometry.vertices.push(
                            new THREE.Vector3(...data.edges[i].start),
                            new THREE.Vector3(...data.edges[i].end)
                        );

                        var line = new THREE.Line(edgeGeometry, edgeMaterial);
                        line._weight = data.edges[i].weight / data.max_weight;
                        self.children.push(line);
                        scene.add(line);
                    }
                }
            }

            V.addLayer('axes', new Axes())
            V.addLayer('graph', new GraphLayer({
                getData: () => {
                    return """ + self.renderLayers['graph'].export_data() + """
                }
            }));

            V.resize(undefined, 300)
                </script>
            </body>
	    </html>
        """
        return html_str
