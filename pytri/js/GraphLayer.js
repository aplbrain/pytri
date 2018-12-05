class GraphLayer extends window.substrate.Layer {
    constructor(opts) {
        super(opts);
        this.graph = {
            nodes: opts.graph.nodes,
            edges: opts.graph.links,
        };
        this.nodeDict = opts.nodeDict;
        this.nodeColor = opts.nodeColor;
        this.nodeSize = opts.radius;

        this.linkColor = opts.linkColor;
        this.meshNodes = opts.meshNodes;
    }

    _getNodePosition(node) {
        let pos = {};
        if (node.hasOwnProperty('pos')) {
            if (Array.isArray(node.pos)) {
                pos = {
                    x: node.pos[0],
                    y: node.pos[1],
                    z: node.pos[2]
                };
            } else {
                pos = node.pos;
            }
        } else if ('x' in node && 'y' in node && 'z' in node) {
            pos = {
                x: node.x,
                y: node.y,
                z: node.z
            };
        }
        // TODO: add error handling for no position in node
        return pos;
    }


    requestInit(scene) {
        let self = this;

        if(this.meshNodes) {
            self.graph.nodes.forEach((node, i) => {
                let sph = new window.THREE.Mesh(
                    new window.THREE.SphereGeometry(
                        Array.isArray(this.nodeSize) ? this.nodeSize[i] : this.nodeSize, 6, 6
                    ),
                    new window.THREE.MeshBasicMaterial({
                        color: Array.isArray(this.nodeColor) ? this.nodeColor[i] : this.nodeColor
                    })
                );

                let pos = this._getNodePosition(node);
                sph.position.set(pos.x, pos.y, pos.z);

                this.children.push(sph);
                scene.add(sph);
            });
        } else {
            let particleSystem = new window.THREE.GPUParticleSystem({
                maxParticles: self.graph.nodes.length
            });

            scene.add(particleSystem);

            self.graph.nodes.forEach((node, i) => {
                let pos = this._getNodePosition(node);
                particleSystem.spawnParticle({
                    position: pos,
                    size: Array.isArray(this.nodeSize) ? this.nodeSize[i] : this.nodeSize,
                    color: Array.isArray(this.nodeColor) ? this.nodeColor[i] : this.nodeColor
                });
            });
            self.children.push(particleSystem);
        }

        let edgeGeometry = new THREE.Geometry();
        self.graph.edges.forEach(edge => {
            let start = this.nodeDict[edge["source"]];
            let startPos = this._getNodePosition(start);
            let stop = this.nodeDict[edge["target"]];
            let stopPos = this._getNodePosition(stop);
            edgeGeometry.vertices.push(
                new THREE.Vector3(startPos.x, startPos.y, startPos.z)
            );
            edgeGeometry.vertices.push(
                new THREE.Vector3(stopPos.x, stopPos.y, stopPos.z)
            );
        });

        let edges = new THREE.LineSegments(
            edgeGeometry,
            new THREE.LineBasicMaterial({
                color: this.linkColor,
            })
        );
        self.children.push(edges);
        scene.add(edges);
    }
}
