import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
import re
import sys

def compute_curvature(y):
    """计算曲率以确定最佳eps值"""
    dy = np.gradient(y)
    d2y = np.gradient(dy)
    curvature = np.abs(d2y) / (1 + dy**2)**1.5
    return curvature

# 处理输入文件
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    group_id = parts[0]
    gene_ids = parts[1:]
    
    # 提取基因编号并转换为数值
    data = []
    valid_genes = []
    for gene in gene_ids:
        match = re.search(r'G(\d{4})\d{2}', gene)
        if match:
            num = int(match.group(1))
            data.append(num)
            valid_genes.append(gene)
    if len(data) < 2:  # 跳过不满足最小基因数的group
        continue
    data = np.array(data).reshape(-1, 1)
    
    min_samples = 2
    # 计算k距离
    nbrs = NearestNeighbors(n_neighbors=min_samples)
    nbrs.fit(data)
    distances, _ = nbrs.kneighbors(data)
    k_distances = np.sort(distances[:, 1], axis=0)
    
    # 计算最佳eps
    curvature = compute_curvature(k_distances)
    optimal_eps = k_distances[np.argmax(curvature)]
    if optimal_eps<2:
        optimal_eps=2
    
    # DBSCAN聚类
    db = DBSCAN(eps=optimal_eps, min_samples=min_samples)
    db.fit(data)
    labels = db.labels_
    
    # 格式化和输出
    genes_str = ','.join(valid_genes)
    k_dist_str = ','.join([f"{x:.3f}" for x in k_distances])
    eps_str = f"{optimal_eps:.3f}"
    if len(data) == 2 and optimal_eps>2: 
        labels_str = "-1,-1"
    else:
        labels_str = ','.join(map(str, labels))
    print (f"{group_id}\t{genes_str}\t{k_dist_str}\t{eps_str}\t{labels_str}")
