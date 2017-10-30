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
            console.log(this.data.nodes[i])
            let sph = new window.THREE.Mesh(
                new window.THREE.SphereGeometry(this.radius, 6, 6),
                new window.THREE.MeshBasicMaterial({
                    color: this.c_array ? this.colors[i] : this.colors
                })
                );
            let n = this.data.nodes[i].pos
            sph.position.set(n.x, n.y, n.z);
            this.children.push(sph)
            scene.add(sph)
        }

        for (var i = 0; i < this.data.links.length; i++) {
            console.log(this.data.links[i].source)
            console.log(this.data.links[i].target)
            var edgeGeometry = new window.THREE.Geometry();
            var edgeMaterial = new window.THREE.LineBasicMaterial({
                color: 0xbabe00 * (this.data.links[i].weight || 1),
                transparent: true,
                opacity: this.data.links[i].weight || 1,
                linewidth: this.data.links[i].weight || 1,
            });
            let sn = this.data.nodes[this.data.links[i].source].pos
            let tn = this.data.nodes[this.data.links[i].target].pos
            edgeGeometry.vertices.push(
                new window.THREE.Vector3(sn.x, sn.y, sn.z),
                new window.THREE.Vector3(tn.x, tn.y, tn.z)
                );

            var line = new window.THREE.Line(edgeGeometry, edgeMaterial);
            this.children.push(line);
            scene.add(line);
        }
    }
}