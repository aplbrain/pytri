class ColorGraphLayer extends Layer {
    constructor(opts) {
        super(opts);
        this.graph = {
            nodes: opts.graph.nodes,
            edges: opts.graph.links,
        };

        this.nodeColor = opts.nodeColor;
        this.nodeSize = opts.radius;

        this.linkColor = opts.linkColor;

        this.meshNodes = opts.meshNodes;
    }

    _getNodePosition(node) {
        let pos = {};
        if ('pos' in node) {
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
        if (typeof pos.x != 'number' || typeof pos.y != 'number' || typeof pos.z != 'number') {
            throw Error('missing coordinates in node');
        }

        return pos;
    }

    requestInit(scene) {
        let self = this;
        let graph = {
            nodes: this.graph.nodes,
            edges: this.graph.edges,
        };
        window.graph = this.graph;

        let particleSystem = new window.THREE.GPUParticleSystem({
            maxParticles: graph.nodes.length
        });

        this.pSys = particleSystem;
        scene.add(particleSystem);


        if(this.meshNodes) {
            this.graph.nodes.forEach((node, i) => {
                let sph = new window.THREE.Mesh(
                    new window.THREE.SphereGeometry(
                        this.nodeSizeIsArray ? this.nodeSize[i] : this.nodeSize, 6, 6
                    ),
                    new window.THREE.MeshBasicMaterial({
                        color: this.nodeColorIsArray ? this.nodeColor[i] : this.nodeColor
                    })
                );
                let pos = this._getNodePosition(node);
                sph.position.set(pos.x, pos.y, pos.z);
                this.children.push(sph);
                scene.add(sph);
            });
        } else {
            if(this.nodeColor.constructor === Array) {
                this.graph.nodes.forEach((node, i) => {
                    let pos = this._getNodePosition(node)
                    let color = this.nodeColor[i]
                    particleSystem.spawnParticle({
                        position: pos,
                        size: this.nodeSize,
                        color: color
                    });
                })
            } else {
                let color = this.nodeColor
                this.graph.nodes.forEach((node, i) => {
                    let pos = this._getNodePosition(node)
                    particleSystem.spawnParticle({
                        position: pos,
                        size: this.nodeSize,
                        color: color
                    });
                });
            }
            self.children.push(particleSystem)
        }

        let edgeGeometry = new THREE.Geometry();

        this.graph.edges.forEach((edge, i) => {
            let start = graph.nodes[edge["source"]];
            let startPos = this._getNodePosition(start)
            let stop = graph.nodes[edge["target"]];
            let stopPos = this._getNodePosition(stop)
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
