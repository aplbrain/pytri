class MeshLayer extends Layer {
    constructor(props) {
        super(props);
        this.data = props.data;
        this._material = props.material;
    }

    requestInit(scene) {
        let self = this;
        self.needsUpdate = true;

        let mesh = new window.THREE.OBJLoader().parse(self.data);
        self._meshGeometry = new window.THREE.Mesh(
            new window.THREE.Geometry().fromBufferGeometry(mesh.children[0].geometry),
            new window.THREE.MeshNormalMaterial()
        );
        self.children = [self._meshGeometry];

        scene.add(self._meshGeometry);
    }
}