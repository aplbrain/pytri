class MeshLayer extends Layer {
    constructor(props) {
        super(props);
        this.data = props.data;
        this.opacity = props.opacity;
    }

    requestInit(scene) {
        let self = this;
        self.needsUpdate = true;

        if (self.opacity) {
            self._material = new window.THREE.MeshNormalMaterial({
                opacity: self.opacity,
                side: window.THREE.DoubleSide,
                transparent: true
            });
        } else {
            self._material = new window.THREE.MeshNormalMaterial({
                side: window.THREE.DoubleSide,
            });
        }

        let mesh = new window.THREE.OBJLoader().parse(self.data);
        self._meshGeometry = new window.THREE.Mesh(
            new window.THREE.Geometry().fromBufferGeometry(mesh.children[0].geometry),
            self._material
        );
        self.children = [self._meshGeometry];

        scene.add(self._meshGeometry);
    }
}
