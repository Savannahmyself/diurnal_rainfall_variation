#! /usr/bin/env python
# coding=utf-8

import datetime
import numpy as np
import os
import pandas as pd
import string
import sys
from dateutil.parser import parse
from time import time

nRows = 440
nCols = 700


def clusters_merge(filename,file):
    #读取聚类结果数据，中国区所有栅格单元的标准化降水日变化数据
    res_list = [[] for row in range(19)]  #初始化19类的19行列表，存储每类的降水日变化数据
    pd_variation = pd.read_csv(file, encoding='utf-8', usecols=range(24), header=None)
    file_asc = "H:\\preci-extract\\rainfall_variation\\data_input_output\\kmeans_1211\\kmeans_clusters" + "\\" + filename.split(".")[0] + ".asc"
    print(file_asc)
    pd_asc = pd.read_csv(file_asc, skiprows=6, encoding="utf-8", usecols=range(700), sep='\t', header=None)
    #读取每个栅格单元的类别，根据索引号，读取该栅格的标准化降水日变化数据，存储到对应类别的列表中
    index = 0
    for i in range(nRows):
        for j in range(nCols):
            if pd_asc.iloc[i, j] == -99:
                continue
            else:
                num = int(pd_asc.iloc[i, j])
                res_list[num].append(pd_variation.iloc[index, :])
                index += 1

    #计算每类的平均降水日变化数据，存储到列表中
    ave_list = []
    for i in range(19):
        ave_res = sum(res_list[i])/len(res_list[i])
        ave_list.append(ave_res)

    #将每类的平均降水日变化结果存储到.csv表中
    store_path = "H:\\preci-extract\\rainfall_variation\\data_input_output\\kmeans_1211\\kmeans_clusters\\clusters_average" + "\\" + filename.split(".")[0] + "average" + ".csv"
    f1 = open(store_path, 'w')
    for data in ave_list:
        for j in range(23):
            if data[j] >=2:
                data[j] =2
            f1.write(str(data[j]) + ",")
        if data[23] >2:
            data[23] = 2
        f1.write(str(data[23]))
        f1.write("\n")


if __name__ == '__main__':
    file_path = r"H:\preci-extract\rainfall_variation\data_input_output\kmeans_1211\kmeans_input_data"
    for filename in os.listdir(file_path):
        file = file_path + "\\" + filename   #中国区每个三个栅格数据的标准化降水日变化表
        clusters_merge(filename, file)

    #测试代码
    # file_asc = "H:\\preci-extract\\rainfall_variation\\data_input_output\\kmeans_clusters\\08-16_6-8month_yearly_mean_amount.asc"
    # # pd_asc = pd.read_csv(file_asc, skiprows=6, encoding="utf-8",  usecols=range(700), engine='python', sep='\t', delimiter=None,
    # #                      index_col=False, header=None, skipinitialspace=True)
    # pd_asc = pd.read_csv(file_asc, skiprows=6, encoding="utf-8", usecols=range(700), sep='\t',header=None)
    #
    # file = r"H:\preci-extract\rainfall_variation\data_input_output\Kmeans_input_data\08-16_6-8month_yearly_mean_amount.csv"
    # pd_variation = pd.read_csv(file, usecols=range(24), encoding='utf-8', header=None)
    # # print(pd_variation.iloc[0, :])
    #
    # data_list = []
    # for i in range(10):
    #     data_list.append(pd_variation.iloc[i, :])
    #
    # average = sum(data_list)/len(data_list)
    # # print(data_list)
    # # print(sum(data_list))
    # # print(len(data_list))
    # print(average)