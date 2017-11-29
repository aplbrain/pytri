class ImageLayer extends Layer {
    constructor(opts) {
        super(opts);
        this.dataURI = opts.dataURI;
        this.width = opts.width;
        this.height = opts.height;
        this.position = opts.position;
    }

    requestInit(scene) {
        let self = this;
        self.needsUpdate = true;

        let geometry = new window.THREE.PlaneBufferGeometry(self.width, self.height);
        let image = new Image();
        image.src = self.dataURI;
        let texture = new window.THREE.Texture(image);
        texture.needsUpdate = true;
        let material = new window.THREE.MeshBasicMaterial({map: texture});
        let plane = new window.THREE.Mesh(geometry, material);
        plane.material.side = window.THREE.FrontSide;
        let rotationMatrix = new Matrix4();
        rotationMatrix.set(
            0, 1, 0, 0,
            1, 0, 0, 0,
            0, 0, -1, 0,
            0, 0, 0, 1
        );
        plane.rotation.setFromRotationMatrix(rotationMatrix);
        plane.position.set(
            self.position["x"],
            self.position["y"],
            self.position["z"]
        );

        self.children.push(plane);
        scene.add(plane);
    }
}
