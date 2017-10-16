#!/usr/bin/env python3

from IPython.display import Javascript, HTML, display
import requests


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

		self.js = js

	def show(self):
		display(HTML("<script>{}</script>".format(self.js) + """
			<div id="target"></div>
			<script>
			
			V = new Visualizer({
				targetElement: "target",
			    backgroundColor: new window.THREE.Color(0xffffff),
				renderLayers: {
					// None yet!
				}
			});

			V.triggerRender();
			V.resize(undefined, 400)
			</script>
		"""))

	def remove_layer(self, name):
		display(Javascript("""
			V.removeLayer('{}')
		""".format(name)))

	def axes(self):
		display(Javascript("""
			class AxisLayer extends Layer {
				requestRender(scene) {
			        let axes = new window.THREE.AxisHelper(5);
			        this.children.push(axes)
					scene.add(axes)
				}
			}
			V.addLayer('axes', new AxisLayer())
		"""))


