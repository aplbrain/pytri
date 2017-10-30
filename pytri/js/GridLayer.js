class GridLayer extends Layer {

    constructor(props) {
        super(props);
        this.x_lim = props.x_lim || [-5, 5];
        this.y_lim = props.y_lim || [-5, 5];
        this.z_lim = props.z_lim || [-5, 5];
        this.x_count = props.x_count || 10;
        this.y_count = props.y_count || 10;
        this.z_count = props.z_count || 10;
    }

    requestInit(scene) {
        let self = this;

        let lineGeo = new window.THREE.Geometry();


        let x_inc = (this.x_lim[1] - this.x_lim[0]) / this.x_count;

        for (let xi = this.x_lim[0]; xi < this.x_lim[1]; xi += x_inc) {
            lineGeo.vertices.push(
                new window.THREE.Vector3(x_inc, -this.y_lim[0], 0)
            );
            lineGeo.vertices.push(
                new window.THREE.Vector3(x_inc, this.y_lim[0], 0)
            );
        }

        let line = new window.THREE.LineSegments(
            lineGeo,
            new window.THREE.LineBasicMaterial({
                color: 0xff0000
            })
        );
        self.children.push(line);
        scene.add(line);
    }
}
