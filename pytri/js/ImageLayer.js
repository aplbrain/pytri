class ImageLayer extends window.substrate.Layer {
    constructor(opts) {
        super(opts);
        this.dataURI = opts.dataURI;
        this.width = opts.width;
        this.height = opts.height;
        this.position = opts.position;
        this.rotation = opts.rotation;
    }

    requestInit(scene) {
        let self = this;
        self.needsUpdate = true;

        let geometry = new window.THREE.PlaneGeometry(self.width, self.height);
        let image = new Image();
        image.src = self.dataURI;
        let texture = new window.THREE.Texture(image);
        texture.needsUpdate = true;
        let material = new window.THREE.MeshBasicMaterial({
            map: texture,
            side: window.THREE.DoubleSide
        });
        let plane = new window.THREE.Mesh(geometry, material);
        plane.rotation.set(
            self.rotation["x"],
            self.rotation["y"],
            self.rotation["z"]
        );
        plane.position.set(
            self.position["x"],
            self.position["y"],
            self.position["z"]
        );

        self.children.push(plane);
        scene.add(plane);
    }
}
