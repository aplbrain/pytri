import Layer from 'apl-substrate/components/Layer';


export default class VolumeLayer extends Layer {

    constructor(props) {
        super(props);
        this.getData = props.getData;
        this.colormap = props.colormap || (_ => 0xffffff);
    }

    reload(data) {
        this.scene.remove(this.pSys);
        this.requestInit(this.scene, data);
    }

    rescale(pt) {
        return [
            pt[0] * 2,
            pt[1] * 2,
            pt[2] * 2
        ];
        // let rescaler : number = 10;
        // return pt * rescaler;
    }

    getAt(i, j, k) {
        return this.data[
            i + this.shape[0] * (j + this.shape[1] * k)
        ]
    }

    requestInit(scene, dat) {
        let self = this;
        this.scene = scene;
        let { data, shape } = dat || self.getData();
        self.data = data;
        self.shape = shape.reverse();


        let particleSystem = new window.THREE.GPUParticleSystem({
            maxParticles: self.shape[0] * self.shape[1] * self.shape[2]
        });

        this.pSys = particleSystem;
        scene.add(particleSystem);

        for (var i = 0; i < self.shape[0]; i++) {
            for (var j = 0; j < self.shape[1]; j++) {
                for (var k = 0; k < self.shape[2]; k++) {
                    let vec = new window.THREE.Vector3(
                        ...self.rescale(
                            [(i - self.shape[0]/2),
                            (j - self.shape[1]/2),
                            (k - self.shape[2]/2)]
                        )
                    );
                    let val = self.getAt(i, j, k);
                    if (val > 60) {
                        particleSystem.spawnParticle({
                            position: vec,
                            color: self.colormap(val / 10),
                            colorRandomness: 0,
                            size: val / 20,
                        });
                    }
                }
            }
        };
        particleSystem.scale.set(1.1, 1.1, 1.1);
    }
}
