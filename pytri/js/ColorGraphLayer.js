class ColorGraphLayer extends Layer {
    constructor(opts) {
        super(opts);
        this.graph = {
            nodes: opts.graph.nodes,
            edges: opts.graph.links,
        };

        this.nodeColor = opts.nodeColor;
        this.radius = opts.radius;

        this.linkColor = opts.linkColor;
        
        if (Array.isArray(opts.minMaxVals)) {
            this.minMaxVals = opts.minMaxVals;
            this._calculateShift(this.minMaxVals);
        }
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

    _calculateShift(vals) {
        this.maxX = vals[0];
        this.minX = vals[1];
        this.maxY = vals[2];
        this.minY = vals[3];
        this.maxZ = vals[4];
        this.minZ = vals[5];

        this.xSubtract = this.minX + ((this.maxX - this.minX) / 2.0);
        this.ySubtract = this.minY + ((this.maxY - this.minY) / 2.0);
        this.zSubtract = this.minZ + ((this.maxZ - this.minZ) / 2.0);
    }

    _scaledPos(nodeData) {
        let xPos = nodeData.x - this.xSubtract;
        let yPos = nodeData.y - this.ySubtract;
        let zPos = nodeData.z - this.zSubtract;

        xPos = -20 * (xPos - this.minX) / (this.maxX - this.minX) + -10;
        yPos = -20 * (yPos - this.minY) / (this.maxY - this.minY) + -10;
        zPos = -20 * (zPos - this.minZ) / (this.maxZ - this.minZ) + -10;
        return { x: xPos, y: yPos, z: zPos };
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

        if (!this.minMaxVals) { // Lazyily calculate minMaxVals if not passed as an argument.
            let [ minX, minY, minZ ] = [ Number.MAX_VALUE, Number.MAX_VALUE, Number.MAX_VALUE ];
            let [ maxX, maxY, maxZ ] = [ Number.MIN_VALUE, Number.MIN_VALUE, Number.MIN_VALUE ];
            for (let node of this.graph.nodes) {
                let pos = this._getNodePosition(node);
                if (pos.x < minX) minX = pos.x;
                if (pos.x > maxX) maxX = pos.x;
                if (pos.y < minY) minY = pos.y;
                if (pos.y > maxY) maxY = pos.y;
                if (pos.z < minZ) minZ = pos.z;
                if (pos.z > maxZ) maxZ = pos.z;
            }
            this._calculateShift([ maxX, minX, maxY, minY, maxZ, minZ ]);
        }

        if(this.nodeColor.constructor === Array) {
            this.graph.nodes.forEach((node, i) => {
                let pos = this._scaledPos(this._getNodePosition(node));
                let color = this.nodeColor[i];
                particleSystem.spawnParticle({
                    position: pos,
                    size: this.radius,
                    color: color
                });
            });
        } else {
            let color = this.nodeColor;
            this.graph.nodes.forEach((node, i) => {
                let pos = this._scaledPos(this._getNodePosition(node));
                particleSystem.spawnParticle({
                    position: pos,
                    size: this.radius,
                    color: color
                });
            });
        }
        self.children.push(particleSystem);

        let edgeGeometry = new THREE.Geometry();



        this.graph.edges.forEach((edge, i) => {
            let start = graph.nodes[edge["source"]];
            let startPos = this._scaledPos(this._getNodePosition(start));
            let stop = graph.nodes[edge["target"]];
            let stopPos = this._scaledPos(this._getNodePosition(stop));
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
