class GraphLayer extends Layer {
    constructor(opts) {
        super(opts);

        this.graph = opts.graph;
        this.nodeSize = opts.radius || 0.15;
        this.nodeColor = opts.nodeColor || 0xbabe00;
        this.linkColor = opts.linkColor || 0x00babe;

        this.nodeSizeIsArray = Array.isArray(this.nodeSize);
        this.nodeColorIsArray = Array.isArray(this.nodeColor);
        this.linkColorIsArray = Array.isArray(this.linkColor);
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

            let snPos = this._getNodePosition(sn);
            let tnPos = this._getNodePosition(tn);

            let v1 = new window.THREE.Vector3(snPos.x, snPos.y, snPos.z);
            let v2 = new window.THREE.Vector3(tnPos.x, tnPos.y, tnPos.z);

            edgeGeometry.vertices.push(v1, v2);

            let line = new window.THREE.Line(edgeGeometry, edgeMaterial);
            this.children.push(line);
            scene.add(line);
        });
    }
}
