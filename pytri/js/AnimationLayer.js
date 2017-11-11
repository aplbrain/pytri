class AnimationLayer extends Layer {
    constructor(opts) {
        super(opts);
        this.graphName = opts.graphName;
        this.visualizer = opts.visualizer;
        this.graphLayerNodes = window.V[this.visualizer].renderLayers[this.graphName].children;
        this.graph = window.V[this.visualizer].renderLayers[this.graphName].data;
        this.setData(opts.onNodes, opts.color)
    }

    setData(onNodes, color) {
        console.log(onNodes)
        console.log(color)
        this.onNodes = onNodes;
        this.color = color;
        this.requestInit;
    }


    requestInit(scene) {
        if (this.onNodes) {
            for (var i=0; i < this.onNodes.length; i++) {
                let node = this.onNodes[i];
                let name = "node" + String(node);
                let sceneNode = scene.getObjectByName(name)
                sceneNode.material.color = new THREE.Color(this.color);
            }
        } 
    }
}