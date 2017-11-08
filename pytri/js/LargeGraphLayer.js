

class GraphLayer extends Layer {
    constructor(opts) {
        super(opts);
        this.graph = {
            nodes: opts.graph.nodes,
            edges: opts.graph.links,
        };
        this.colormap = opts.colormap || (_ => 0xffffff);
        // this.nodeColor = opts.color
        this.nodeSize = opts.node_size

        this.maxX = opts.minMaxVals[0];
        this.minX = opts.minMaxVals[1];
        this.maxY = opts.minMaxVals[2];
        this.minY = opts.minMaxVals[3];
        this.maxZ = opts.minMaxVals[4];
        this.minZ = opts.minMaxVals[5];

        this.xSubtract = this.minX + ((this.maxX - this.minX) / 2);
        this.ySubtract = this.minY + ((this.maxY - this.minY) / 2);
        this.zSubtract = this.minZ + ((this.maxZ - this.minZ) / 2);
    }

    reload(data) {
        this.scene.remove(this.pSys);
        this.requestInit(this.scene, data);
    }

    scaledPos(nodeData) {
        let xPos = nodeData.x - this.xSubtract
        let yPos = nodeData.y - this.ySubtract
        let zPos = nodeData.z - this.zSubtract
        return({'x': xPos, 'y': yPos, 'z': zPos})
    }
    
    requestInit(scene) {
        let self = this;
        let graph = {
            nodes: this.graph.nodes,
            edges: this.graph.edges,
        };
        window.graph = graph;

        let particleSystem = new window.THREE.GPUParticleSystem({
            maxParticles: graph.nodes.length,
        });

        this.pSys = particleSystem;
        scene.add(particleSystem);

        for (let nodeId in graph.nodes) {
            let val = graph.nodes[nodeId];
            let pos = this.scaledPos(val)
            particleSystem.spawnParticle({
                position: pos,
                size: this.nodeSize,
                color: 0xffffff
            });
        }
        self.children.push(particleSystem)

        let edgeGeometry = new THREE.Geometry();
        graph.edges.forEach(edge => {
            let start = graph.nodes[edge["source"]];
            let startPos = this.scaledPos(start)
            let stop = graph.nodes[edge["target"]];
            let stopPos = this.scaledPos(stop)
                edgeGeometry.vertices.push(
                    //new THREE.Vector3((start.x - 31055) / (35/8), (start.y-19513) / (35/8), start.z-584)
                    new THREE.Vector3(startPos.x, startPos.y, startPos.z)
                );
                edgeGeometry.vertices.push(
                    new THREE.Vector3(stopPos.x, stopPos.y, stopPos.z)
                    //new THREE.Vector3((stop.x - 31055)  / (35/8), (stop.y-19513) / (35/8), stop.z-584)
                );  
        });
        let edges = new THREE.LineSegments(
            edgeGeometry,
            new THREE.LineBasicMaterial({
                color: 0x00babe
            })
        );
        self.children.push(edges);
        scene.add(edges);   
    }
}