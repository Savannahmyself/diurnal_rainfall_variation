#! /usr/bin/env python
#coding=utf-8

#读取制作好的输入数据，利用kmeans聚类方法进行聚类分析，所得结果存储入.asc文件中，非中国区域用-99标记


import datetime
import gdal
import os
import numpy as np
import pandas as pd
import string
import sys
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

nRows = 440
nCols = 700
xMin = 70.05
yMin = 15.05
yMax = yMin + 44
dx = 0.1
delta = 0.000001
noDataValue = -99
num = nRows * nCols
fmt = '%df' % (num,)

header = """NCOLS %d
NROWS %d
XLLCENTER %f
YLLCENTER %f
cellsize %f
NODATA_VALUE %f
""" % (nCols, nRows, xMin, yMin, 0.1, -99)


def Kmeans_analysis(filename,filepath,storepath):

    name = os.path.splitext(filename)[0]
    # 打开数据文件,将每个格网单元的24小时标准化年均降水频率和年均降水量数据存入analysis_data数据框中
    analysis_data = pd.read_csv(filepath, usecols=range(1, 7), header=None, skiprows=1)

    #计算不同聚类数的聚类结果，挑选最合适的作为最终的结果
    for n_digits in range(2, 31):
        #    下面进行聚类分析
        #    k-means++就是选择初始seeds的一种算法，聚类簇数为n_clusters=n_digits,
        #     n_init，默认的是：n_init=10
        #   Number of time the k-means algorithm will be run with different centroid seeds.
        #   The final results will be the best output of n_init consecutive runs in terms of inertia.

        kmeans = KMeans(init='k-means++', n_clusters=n_digits, n_init=10)

        kmeans.fit(analysis_data)

        #    Obtain labels for each point in mesh. Use last trained model.
        Z_Value = []
        for i in range(len(analysis_data.iloc[:, 0])):
            # print(analysis_data.iloc[i])
            Z = kmeans.predict(np.array(analysis_data.iloc[i]).reshape(1, 6))
            Z_Value.append(Z[0])
        #将聚类结果输出到.asc文件中
        file_output = storepath + "\\" + str(name) + "_"+str(n_digits) + ".asc"
        f = open(file_output, 'w')
        f.write(header)
        # 读取中国区域内的栅格数据
        fn = r"G:\rainfall_variation\China_new.tif"
        ds = gdal.Open(fn)
        extent_china = ds.ReadAsArray(0, 0, nCols, nRows)

        # 将单个栅格文件中对应格网的数据存入对应序号的列表里中,非中国区域赋值-99
        index = 0
        for j in range(nRows):
            for k in range(nCols):
                if extent_china[j][k] == 0:
                    f.write(str(-99) + "\t")
                else:
                    tmp_num = Z_Value[index]
                    f.write(str(tmp_num) + "\t")
                    index += 1
            f.write("\n")
        f.close()

        #将聚类的距离值存储
        file_distance = storepath + "\\" + str(name) + "_" + "Distance" + ".txt"
        f = open(file_distance, 'a')
        f.write(str(kmeans.inertia_) + "\t")
        f.close()

if __name__ == '__main__':
    path = r"G:\rainfall_variation\data_in_out_1228\data_input"
    storepath = r"G:\rainfall_variation\data_in_out_1228\data_output"
    for filename in os.listdir(path):
        filepath = path + "\\" + filename
        Kmeans_analysis(filename, filepath, storepath)
