class ScatterLayer extends window.substrate.Layer {
    constructor(opts) {
        super(opts);
        this.radius = opts.radius || 0.15;
        this.colors = opts.colors || 0x00babe;
        if (typeof(this.colors) == "number") {
            this.c_array = false;
        } else {
            this.c_array = true;
        }
        this.data = opts.data;
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
            this.children.push(sph);
            scene.add(sph);

        }
    }
}
