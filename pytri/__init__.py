#!/usr/bin/env python3

from IPython.display import Javascript, HTML, display
import requests
import uuid
import json
import dicom
import os
import gzip
import matplotlib.pyplot as plt

import numpy as np

import networkx as nx
from networkx.readwrite import json_graph

print("welp")

__version__ = "0.0.1"

class pytri:

    def __init__(self):
        scripts = [
            "https://threejs.org/examples/js/controls/TrackballControls.js",
        ]

        threesrc = requests.get("https://threejs.org/build/three.js").text.split('\n')
        threesrc = threesrc[6:-2]

        js = "exports = window.THREE || {}; " + "\n".join(threesrc) + "window.THREE = exports;"

        for script in scripts:
            js += requests.get(script).text.strip()

        with open("./substrate.min.js", 'r') as fh:
            js += ";\n\n" + fh.read().strip()
        
        js2 = ""
        with open("./StableGPUParticleSystem.js", 'r') as fh:
            js2 += ";\n\n" + fh.read().strip()

        self.js = js
        self.gpups = js2
        self.uid = str(uuid.uuid4())

    def show(self, background=0xffffff):
        display(HTML("<script>{}</script>".format(self.js) + 
            "<script>{}</script>".format(self.gpups) +
            "<div id='pytri-target-{}'></div>".format(self.uid) + """
            <script>
            V = {}
            V['"""+self.uid+"""'] = new Visualizer({
                targetElement: "pytri-target-"""+self.uid+"""",
                backgroundColor: new window.THREE.Color({}),""".format(background)+"""
                renderLayers: {
                    // None yet!
                }
            });
            V['"""+self.uid+"""'].triggerRender();
            V['"""+self.uid+"""'].resize(undefined, 400)
            </script>
        """))

    def remove_layer(self, name):
        display(Javascript("""
            V['"""+self.uid+"""'].removeLayer('{}')
        """.format(name)))

    def axes(self):
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

    def scatter(self, data, r=0.15, c=0x00babe):
        d = data.tolist()
        _js = ("""
        class ScatterLayer extends Layer {
            constructor(opts) {
                super(opts);

                this.setData = this.setData.bind(this);
                this.radius = opts.radius || 0.15;
                this.colors = opts.colors || 0x00babe;
                if (typeof(this.colors) == "number") {
                    this.c_array = false;
                } else {
                    this.c_array = true;
                }
                this.setData(opts.data);
            }

            setData(data) {
                this.data = data;
                this.requestInit;
            }

            requestInit(scene) {
                for (let i = 0; i < this.data.length; i++) {
                    let sph = new window.THREE.Mesh(
                        new window.THREE.SphereGeometry(this.radius, 6, 6),
                        new window.THREE.MeshBasicMaterial({
                            color: this.c_array ? this.colors[i] : this.colors
                        })
                    );
                    sph.position.set(...this.data[i]);
                    this.children.push(sph)
                    scene.add(sph)
                    
                }
            }
        }
        """ + """
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


    def graph(self, data, r=0.15, c=0xbabe00):
        if isinstance(data, nx.Graph):
            data = json_graph.node_link_data(data)
        _js = ("""
        class GraphLayer extends Layer {
            constructor(opts) {
                super(opts);

                this.setData = this.setData.bind(this);
                this.radius = opts.radius || 0.15;
                this.colors = opts.colors || 0x00babe;
                if (typeof(this.colors) == "number") {
                    this.c_array = false;
                } else {
                    this.c_array = true;
                }
                this.setData(opts.data);
            }

            setData(data) {
                this.data = data;
                this.requestInit;
            }

            requestInit(scene) {
                for (let i = 0; i < this.data.nodes.length; i++) {
                    let sph = new window.THREE.Mesh(
                        new window.THREE.SphereGeometry(this.radius, 6, 6),
                        new window.THREE.MeshBasicMaterial({
                            color: this.c_array ? this.colors[i] : this.colors
                        })
                        );
                    sph.position.set(...this.data.nodes[i].pos);
                    this.children.push(sph)
                    scene.add(sph)
                }

                for (var i = 0; i < this.data.links.length; i++) {
                    var edgeGeometry = new window.THREE.Geometry();
                    var edgeMaterial = new window.THREE.LineBasicMaterial({
                        color: 0xbabe00 * (this.data.links[i].weight || 1),
                        transparent: true,
                        opacity: this.data.links[i].weight || 1,
                        linewidth: this.data.links[i].weight || 1,
                    });
                    edgeGeometry.vertices.push(
                        new window.THREE.Vector3(...this.data.nodes[this.data.links[i].source].pos),
                        new window.THREE.Vector3(...this.data.nodes[this.data.links[i].target].pos)
                        );

                    var line = new window.THREE.Line(edgeGeometry, edgeMaterial);
                    this.children.push(line);
                    scene.add(line);
                }
            }
        }
        """ + """
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
    
    def dicom(self, d_path, r = 0.05, cm=0xffffff):
        # TODO: handle compressed files, entire folders.
        # if df_path.endswith(".dcm") == False:
        #     raise TypeError('Invalid file path')
        fnames = []
        for dirName, subdirList, fileList in os.walk(d_path):
            for filename in fileList:
                if filename.endswith(".dcm"):
                    fnames.append(os.path.join(dirName, filename))

        ref_file = dicom.read_file(fnames[0])  # if this were a directory, would also have to get z axis info
        pixel_dims = (int(ref_file.Rows), int(ref_file.Columns), len(fnames))
        pixel_spacing = (float(ref_file.PixelSpacing[0]), float(ref_file.PixelSpacing[1]), float(ref_file.SliceThickness))

        dicom_to_numpy = np.zeros(pixel_dims, dtype=ref_file.pixel_array.dtype)

        for fname in fnames:
            ds = dicom.read_file(fname)
            dicom_to_numpy[:, :, fnames.index(fname)] = ds.pixel_array
        dicom_to_list = dicom_to_numpy.tolist()
        print(np.shape(dicom_to_numpy))
        sample = [[[-1, 0, 1], [1, 0, -1]], [[-4, -1, -2], [4, 2, 5]]]
        _js = ("""
        class DICOMLayer extends Layer {
            constructor(opts) {
                super(opts);
                this.data = opts.data;
                this.shape = opts.shape;
                console.log(this.data)
                this.colormap = opts.colormap || (_ => 0xffffff);
            }

            reload(data) {
                this.scene.remove(this.pSys);
                this.requestInit(this.scene);
            }

            rescale(pt) {
                return [
                    pt[0] * 2,
                    pt[1] * 2,
                    pt[2] * 2
                ];
                // let rescaler : number = 10;
                // return pt * rescaler;
            }

            getAt(i, j, k) {
                return this.data[
                    i + this.shape[0] * (j + this.shape[1] * k)
                ]
            }

            requestInit(scene) {
                let self = this;
                this.scene = scene;
                let data = this.data;
                let shape = this.shape;
                //self.data = data;
                console.log(self.data)
                //self.shape = shape.reverse();
                console.log(self.shape)


                let particleSystem = new window.THREE.GPUParticleSystem({
                    maxParticles: self.shape[0] * self.shape[1] * self.shape[2]
                });

                this.pSys = particleSystem;
                scene.add(particleSystem);

                for (var i = 0; i < self.shape[0]; i++) {
                    for (var j = 0; j < self.shape[1]; j++) {
                        for (var k = 0; k < self.shape[2]; k++) {
                            let vec = new window.THREE.Vector3(
                                ...self.rescale(
                                    [(i - self.shape[0]/2),
                                    (j - self.shape[1]/2),
                                    (k - self.shape[2]/2)]
                                )
                            );
                            let val = self.getAt(i, j, k);
                            if (val > 60) {
                                particleSystem.spawnParticle({
                                    position: vec,
                                    color: self.colormap(val / 10),
                                    colorRandomness: 0,
                                    size: val / 20,
                                });
                            }
                        }
                    }
                };
                particleSystem.scale.set(1.1, 1.1, 1.1);
            }
        }
        """ + """
        V['"""+self.uid+"""'].addLayer('dicom', new DICOMLayer({{
            data: {},
            shape: {},
            radius: {},
            colormap: {}
        }}))
        """.format(
            json.dumps(sample),
            (3, 2, 2),
            r,
            cm
        ))
        display(Javascript(_js))

    


