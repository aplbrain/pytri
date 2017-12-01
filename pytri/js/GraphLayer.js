class GraphLayer extends Layer {
    constructor(opts) {
        super(opts);

        this.setData = this.setData.bind(this);
        this.radius = opts.radius || 0.15;
        this.nodeColors = opts.nodeColors || 0xbabe00;
        this.linkColors = opts.linkColors || 0x00babe;

        this.nodeColorsIsArray = Array.isArray(this.nodeColors);
        this.linkColorsIsArray = Array.isArray(this.linkColors);

        this.setData(opts.data);
    }

    setData(data) {
        this.data = data;
    }

    requestInit(scene) {
        for (let i = 0; i < this.data.nodes.length; i++) {
            let sph = new window.THREE.Mesh(
                new window.THREE.SphereGeometry(this.radius, 6, 6),
                new window.THREE.MeshBasicMaterial({
                    color: this.nodeColorsIsArray ? this.nodeColors[i] : this.nodeColors
                })
            );

            let node = this.data.nodes[i];

            if ('pos' in node) {
                if (Array.isArray(node.pos)) {
                    sph.position.set(...node.pos);
                } else {
                    sph.position.set(node.pos.x, node.pos.y, node.pos.z);
                }
            } else if ('x' in node && 'y' in node && 'z' in node) {
                sph.position.set(node.x, node.y, node.z);
            } else {
                throw Error('missing coordinates in node');
            }

            this.children.push(sph);
            scene.add(sph);
        }

        for (let i = 0; i < this.data.links.length; i++) {
            let edgeGeometry = new window.THREE.Geometry();
            let edgeMaterial = new window.THREE.LineBasicMaterial({
                color: this.linkColorsIsArray ? this.linkColors[i] : this.linkColors,
                transparent: true,
                opacity: this.data.links[i].weight || 1,
                linewidth: this.data.links[i].weight || 1,
            });

            let sn = this.data.nodes[this.data.links[i].source];
            let tn = this.data.nodes[this.data.links[i].target];

            let v1, v2;

            if ('pos' in sn) {
                if (Array.isArray(sn.pos)) {
                    v1 = new window.THREE.Vector3(...sn.pos)
                } else {
                    v1 = new window.THREE.Vector3(sn.pos.x, sn.pos.y, sn.pos.z);
                }
            } else if ('x' in sn && 'y' in sn && 'z' in sn) {
                v1 = new window.THREE.Vector3(sn.x, sn.y, sn.z);
            } else {
                throw Error('missing coordinates in node');
            }

            if ('pos' in tn) {
                if (Array.isArray(tn.pos)) {
                    v2 = new window.THREE.Vector3(...tn.pos)
                } else {
                    v2 = new window.THREE.Vector3(tn.pos.x, tn.pos.y, tn.pos.z);
                }
            } else if ('x' in tn && 'y' in tn && 'z' in tn) {
                v2 = new window.THREE.Vector3(tn.x, tn.y, tn.z);
            } else {
                throw Error('missing coordinates in node');
            }

            edgeGeometry.vertices.push(v1, v2);

            let line = new window.THREE.Line(edgeGeometry, edgeMaterial);
            this.children.push(line);
            scene.add(line);
        }
    }
}
