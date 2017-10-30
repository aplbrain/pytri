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
        let n = this.data.nodes[0].pos;
        let usexyz = ('x' in n);
        for (let i = 0; i < this.data.nodes.length; i++) {
            let sph = new window.THREE.Mesh(
                new window.THREE.SphereGeometry(this.radius, 6, 6),
                new window.THREE.MeshBasicMaterial({
                    color: this.c_array ? this.colors[i] : this.colors
                })
            );

            let n = this.data.nodes[i].pos;
            if (usexyz) {
                sph.position.set(n.x, n.y, n.z);
            } else {
                sph.position.set(...n);
            }
            this.children.push(sph);
            scene.add(sph);
        }

        for (let i = 0; i < this.data.links.length; i++) {
            let edgeGeometry = new window.THREE.Geometry();
            let edgeMaterial = new window.THREE.LineBasicMaterial({
                color: 0xbabe00 * (this.data.links[i].weight || 1),
                transparent: true,
                opacity: this.data.links[i].weight || 1,
                linewidth: this.data.links[i].weight || 1,
            });
            let sn = this.data.nodes[this.data.links[i].source].pos;
            let tn = this.data.nodes[this.data.links[i].target].pos;

            if (usexyz) {
                edgeGeometry.vertices.push(
                    new window.THREE.Vector3(sn.x, sn.y, sn.z),
                    new window.THREE.Vector3(tn.x, tn.y, tn.z)
                );
            } else {
                edgeGeometry.vertices.push(
                    new window.THREE.Vector3(...sn),
                    new window.THREE.Vector3(...tn)
                );
            }

            let line = new window.THREE.Line(edgeGeometry, edgeMaterial);
            this.children.push(line);
            scene.add(line);
        }
    }
}
