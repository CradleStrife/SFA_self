// hcluster-esm.js
// 引入依赖模块
import distance from 'distancejs';
import extend from 'extend';

// 定义 hcluster 函数
const hcluster = function() {
    let data;
    let clusters;
    let clustersGivenK;
    let treeRoot;
    let posKey = 'position';
    let distanceName = 'angular';
    let distanceFn = distance.angular;
    let linkage = 'avg';
    let verbose = false;

    // 简单的构造函数
    function clust() {}

    // 数据设置和获取方法
    clust.data = function(value) {
        if (!arguments.length) return data;
        data = value;
        clust._buildTree();
        return clust;
    };

    // 其他设置和获取方法
    clust.posKey = function(value) {
        if (!arguments.length) return posKey;
        posKey = value;
        return clust;
    };
    clust.linkage = function(value) {
        if (!arguments.length) return linkage;
        linkage = value;
        return clust;
    };
    clust.verbose = function(value) {
        if (!arguments.length) return verbose;
        verbose = value;
        return clust;
    };
    clust.distance = function(value) {
        if (!arguments.length) return distanceName;
        distanceName = value;
        distanceFn = {
            angular: distance.angular,
            euclidean: distance.euclidean
        }[value] || distance.angular;
        return clust;
    };

    // 获取树属性的方法
    clust.orderedNodes = function() {
        if (!treeRoot) throw new Error('Need to passin data and build tree first.');
        return treeRoot.indexes.map((ndx) => data[ndx]);
    };
    clust.tree = function() {
        if (!treeRoot) throw new Error('Need to passin data and build tree first.');
        return treeRoot;
    };
    clust.getClusters = function(n) {
        if (!treeRoot) throw new Error('Need to passin data and build tree first.');
        if (n > data.length) throw new Error('n must be less than the size of the dataset');
        return clustersGivenK[data.length - n].map((indexes) =>
            indexes.map((ndx) => data[ndx])
        );
    };

    // 数学和矩阵工具函数
    clust._squareMatrixPairs = function(n) {
        const pairs = [];
        for (let row = 0; row < n; row++) {
            for (let col = row + 1; col < n; col++) {
                pairs.push([row, col]);
            }
        }
        return pairs;
    };

    clust._avgDistance = function(setA, setB) {
        let distance = 0;
        for (let ndxA = 0; ndxA < setA.length; ndxA++) {
            for (let ndxB = 0; ndxB < setB.length; ndxB++) {
                distance += data[setA[ndxA]]._distances[setB[ndxB]];
            }
        }
        return distance / setA.length / setB.length;
    };

    clust._minDistance = function(setA, setB) {
        const distances = [];
        for (let ndxA = 0; ndxA < setA.length; ndxA++) {
            for (let ndxB = 0; ndxB < setB.length; ndxB++) {
                distances.push(data[setA[ndxA]]._distances[setB[ndxB]]);
            }
        }
        return distances.sort()[0];
    };

    clust._maxDistance = function(setA, setB) {
        const distances = [];
        for (let ndxA = 0; ndxA < setA.length; ndxA++) {
            for (let ndxB = 0; ndxB < setB.length; ndxB++) {
                distances.push(data[setA[ndxA]]._distances[setB[ndxB]]);
            }
        }
        return distances.sort()[distances.length - 1];
    };

    // 构建聚类树的方法
    clust._buildTree = function() {
        if (!data || !data.length) throw new Error('Need `data` to build tree');
        clusters = [];
        clustersGivenK = [];
        const tree = {};

        data.forEach((d, ndx) => {
            d._distances = data.map((compareTo) =>
                distanceFn(d[posKey], compareTo[posKey])
            );
            clusters.push(extend(d, {
                height: 0,
                indexes: [ndx]
            }));
        });

        for (let iter = 0; iter < data.length - 1; iter++) {
            if (verbose) {
                console.log(
                    iter + ': ' + clusters.map((c) => c.indexes).join('|')
                );
            }
            const clusterPairs = clust._squareMatrixPairs(clusters.length);
            clusterPairs.forEach((pair) => {
                pair[2] = clust['_' + linkage + 'Distance'](
                    clusters[pair[0]].indexes,
                    clusters[pair[1]].indexes
                );
            });
            const nearestPair = clusterPairs.reduce(
                (pairA, pairB) => (pairA[2] <= pairB[2] ? pairA : pairB),
                [0, 0, Infinity]
            );
            const newCluster = {
                name: 'Node ' + iter,
                height: nearestPair[2],
                indexes: clusters[nearestPair[0]].indexes.concat(
                    clusters[nearestPair[1]].indexes
                ),
                children: [clusters[nearestPair[0]], clusters[nearestPair[1]]]
            };
            if (verbose) {
                console.log(newCluster);
            }
            clustersGivenK.push(clusters.map((c) => c.indexes));
            clusters.splice(Math.max(nearestPair[0], nearestPair[1]), 1);
            clusters.splice(Math.min(nearestPair[0], nearestPair[1]), 1);
            clusters.push(newCluster);
        }
        treeRoot = clusters[0];
    };

    return clust;
};

export default hcluster;