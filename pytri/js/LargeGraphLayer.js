class GraphLayer extends Layer {
    constructor(opts) {
        super(opts);
        this.graph = opts.graph;
        this.nodeColor = opts.nodeColor || 0x00babe;
        this.linkColor = opts.linkColor || 0xbabe00;
        this.nodeSize = opts.nodeSize || 2;

        this.nodeColorIsArray = Array.isArray(this.nodeColor);
        this.linkColorIsArray = Array.isArray(this.linkColor);
        this.nodeSizeIsArray = Array.isArray(this.nodeSize);

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
        let maxX = vals[0];
        let minX = vals[1];
        let maxY = vals[2];
        let minY = vals[3];
        let maxZ = vals[4];
        let minZ = vals[5];

        this.xSubtract = minX + ((maxX - minX) / 2);
        this.ySubtract = minY + ((maxY - minY) / 2);
        this.zSubtract = minZ + ((maxZ - minZ) / 2);
    }

    _scaledPos(nodeData) {
        let xPos = nodeData.x - this.xSubtract
        let yPos = nodeData.y - this.ySubtract
        let zPos = nodeData.z - this.zSubtract
        return { x: xPos, y: yPos, z: zPos };
    }
    
    requestInit(scene) {
        let particleSystem = new window.THREE.GPUParticleSystem({
            maxParticles: this.graph.nodes.length,
        });

        this.pSys = particleSystem;
        scene.add(particleSystem);
        this.children.push(particleSystem);

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

        this.graph.nodes.forEach((node, i) => {
            let pos = this._scaledPos(node);
            particleSystem.spawnParticle({
                position: pos,
                size: this.nodeSizeIsArray ? this.nodeSize[i] : this.nodeSize,
                color: this.nodeColorIsArray ? this.nodeColor[i] : this.nodeColor
            });
        });

        this.graph.links.forEach((link, i) => {
            let edgeGeometry = new window.THREE.Geometry();
            let edgeMaterial = new window.THREE.LineBasicMaterial({
                color: this.linkColorIsArray ? this.linkColor[i] : this.linkColor,
                transparent: true,
                opacity: link.weight || 1,
                linewidth: link.weight || 1,
            });

            let sn = this.graph.nodes[link.source];
            let tn = this.graph.nodes[link.target];

            let snPos = this._scaledPos(
                this._getNodePosition(sn)
            );
            let tnPos = this._scaledPos(
                this._getNodePosition(tn)
            );

            let v1 = new window.THREE.Vector3(snPos.x, snPos.y, snPos.z);
            let v2 = new window.THREE.Vector3(tnPos.x, tnPos.y, tnPos.z);

            edgeGeometry.vertices.push(v1, v2);

            let line = new window.THREE.Line(edgeGeometry, edgeMaterial);
            this.children.push(line);
            scene.add(line); 
        });   
    }
}
