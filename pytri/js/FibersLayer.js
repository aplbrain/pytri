class FibersLayer extends window.substrate.Layer {

    constructor(props) {
        super(props);
        this.data = props.data;
        this.downsample = props.downsample || 1;
        this.alpha = props.alpha || 1;
    }

    toggleVisible() {
        this.children.forEach(c => {
            c.visible = !c.visible;
        });
    }

    reload(fibers) {
        let self = this;
        self.children = [];
        self.fibers = fibers;

        for (var i = 0; i < self.fibers.length; i++) {
            var fiberGeometry = new window.THREE.Geometry();
            for (var j = 0; j < self.fibers[i].length; j++) {
                if (j % self.downsample === 0) {
                    fiberGeometry.vertices.push(
                        new window.THREE.Vector3(...self.fibers[i][j])
                    );
                }
            }
            var line = new window.THREE.Line(
                fiberGeometry,
                new window.THREE.LineBasicMaterial({
                    color: 0x00ffff,
                    transparent: true,
                    opacity: self.alpha
                })
            );
            self.children.push(line);

            self.scene.add(line);
        }
    }


    requestInit(scene) {
        let self = this;
        self.scene = scene;
        let fibers = self.data;
        self.reload(fibers);
    }
}
