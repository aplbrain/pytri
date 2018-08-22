class VolumeLayer extends window.substrate.Layer {
    constructor(opts) {
        super(opts);
        this.data = opts.data;
        this.shape = opts.shape;
    }

    reload(data) {
        this.scene.remove(this.pSys);
        this.requestInit(this.scene, data);
    }

    getAt(i, j, k) {
        return this.data[
            i + this.shape[0] * (j + this.shape[1] * k)
        ];
    }

    requestInit(scene) {
        let self = this;

        let particleSystem = new window.THREE.GPUParticleSystem({
            maxParticles: this.data.length,
        });

        this.pSys = particleSystem;
        scene.add(particleSystem);

        let i = 0;
        for (let x = 0; x < this.shape[0]; x++) {
            for (let y = 0; y < this.shape[0]; y++) {
                for (let z = 0; z < this.shape[0]; z++) {
                    let val = this.data[i];
                    particleSystem.spawnParticle({
                        position: {x, y, z},
                        size: val * 10,
                        color: 0x00babe,
                    });
                    i++;
                }
            }
        }
        self.children.push(particleSystem);
    }
}
