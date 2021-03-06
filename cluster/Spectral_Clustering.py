# 文件功能：实现 Spectral Cluster 算法

import numpy as np
from numpy import *
import pylab
import random, math
from itertools import cycle, islice
import nearset_nerghbor.kdtree as kdtree
from nearset_nerghbor.result_set import KNNResultSet, RadiusNNResultSet
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy.stats import multivariate_normal
from cluster.KMeans import K_Means
plt.style.use('seaborn')


class Spectral(object):
    def __init__(self, n_clusters):
        self.n_clusters = n_clusters
        self.result = None

    def fit(self, data):
        # 作业3
        # 屏蔽开始
        # initiation

        W = np.zeros((data.shape[0], data.shape[0]), dtype=np.float64)
        root = kdtree.kdtree_construction(data, leaf_size=10)
        leaf_size = ((data.max(axis = 0) - data.min(axis=0))/((data.shape[0])**(0.3))).max() * 2
        neighbor = 50
        index = 0
        while (index < data.shape[0]) :
            # RNN
            # result_set = RadiusNNResultSet(radius=leaf_size)
            # kdtree.kdtree_radius_search(root, data, result_set, data[index])
            #KNN
            result_set = KNNResultSet(capacity=neighbor)  # neighbor
            kdtree.kdtree_knn_search(root, data, result_set, data[index])
            i = 0
            while i < result_set.size() :
                if index != result_set.dist_index_list[i].index :
                    W[index, result_set.dist_index_list[i].index] = 1 / result_set.dist_index_list[i].distance
                i += 1
            index += 1
        d = W.sum(axis=1)
        print('min: ', d.min())
        d_inv = d ** (-0.5)
        print('min: ',d_inv.min())
        D = np.diag(d)
        # unnormalized
        L = D - W
        # normalized
        L = np.diag(d_inv) @ L @ np.diag(d_inv)

        eigenvectors, eigenvalues, vh = np.linalg.svd(L, hermitian = True)
        sort = eigenvalues.argsort()
        eigenvalue = eigenvalues[sort]
        eigenvector = eigenvectors[:, sort]
        # determine cluster num
        num1 = np.linspace(0, eigenvalues.shape[0] - 2, eigenvalues.shape[0] - 1, dtype=int32)
        num2 = num1 + 1
        cha = eigenvalue[num2] - eigenvalue[num1]
        idx = 0
        while(True):
            if cha[idx+1] / cha[idx] < 3:
                idx += 1
            else:
                break
        cluster_num1 = idx+2
        idx = 0
        while(True):
            if cha[idx] < cha[idx+1]:
                idx += 1
            else:
                break
        cluster_num2 = idx + 1
        if cluster_num2 > cluster_num1:
            cluster_num = cluster_num2
        else:
            cluster_num = cluster_num1

        print('total points:',data.shape[0], 'spectral clusters num:', cluster_num, 'given:', self.n_clusters)
        #self.n_clusters = cluster_num

        V = eigenvector[:,0:self.n_clusters]
        # 归一化
        idx = np.arange(V.shape[0])
        V[idx, :] = V[idx, :] / np.linalg.norm(V[idx, :])
        Y_kmeans = K_Means(n_clusters=self.n_clusters)
        Y_kmeans.fit(V)
        self.result = Y_kmeans.predict(V)

        # 屏蔽结束

    def predict(self, data):
        # 屏蔽开始
        result = self.result
        return result
        # 屏蔽结束


# 生成仿真数据
def generate_X(true_Mu, true_Var):
    # 第一簇的数据
    num1, mu1, var1 = 400, true_Mu[0], true_Var[0]
    X1 = np.random.multivariate_normal(mu1, np.diag(var1), num1)
    # 第二簇的数据
    num2, mu2, var2 = 600, true_Mu[1], true_Var[1]
    X2 = np.random.multivariate_normal(mu2, np.diag(var2), num2)
    # 第三簇的数据
    num3, mu3, var3 = 1000, true_Mu[2], true_Var[2]
    X3 = np.random.multivariate_normal(mu3, np.diag(var3), num3)
    # 合并在一起
    X = np.vstack((X1, X2, X3))
    # 显示数据
    # plt.figure(figsize=(10, 8))
    # plt.axis([-10, 15, -5, 15])
    # plt.scatter(X1[:, 0], X1[:, 1], s=5)
    # plt.scatter(X2[:, 0], X2[:, 1], s=5)
    # plt.scatter(X3[:, 0], X3[:, 1], s=5)
    # plt.show()
    return X


if __name__ == '__main__':
    # 生成数据
    true_Mu = [[0.5, 0.5], [5.5, 2.5], [1, 7]]
    true_Var = [[1, 3], [2, 2], [6, 2]]
    X = generate_X(true_Mu, true_Var)
    #X =  np.array([[1, 2], [2, 2], [5, 8], [8, 8], [1, 0], [9, 11]])

    spectral = Spectral(n_clusters=3)
    spectral.fit(X)
    cat = spectral.predict(X)
    print(cat)

    plt.figure(figsize=(10, 8))
    plt.axis([-10, 15, -5, 15])
    colors = np.array(list(islice(cycle(['#377eb8', '#ff7f00', '#4daf4a',
                                         '#f781bf', '#a65628', '#984ea3',
                                         '#999999', '#e41a1c', '#dede00']),
                                  int(max(cat) + 1))))
    plt.scatter(X[:, 0], X[:, 1], s=5, color=colors[cat])
    plt.show()
    print(cat)
    # 初始化



