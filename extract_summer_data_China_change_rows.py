#! /usr/bin/env python
# coding=utf-8

#1、创建一个用以存储每个中国区域（96309个）格网单元降水数据（起始时间、降水量（大于0.1mm））的二维列表
#2、遍历每小时的.grd文件，检查中国区域的格网单元数据，若降水量值大于0.1mm（有效降水），则将该数据存储入对应的索引号的列表中
#3、将每个中国区域的格网单元的降水输出到按照行列号和索引号命名的.csv文件中


import datetime
import gdal
import numpy as np
import os
import pandas as pd
import time
import string
import sys
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from struct import *

nRows = 440
nCols = 700
num = nRows * nCols
fmt = '%df' % (num,)
minimum = 1e-10  #一个极小值

# 读取文件，输出为440*700二维数组
def readfile(maskFile):
    f = open(maskFile, 'rb')  #以二进制格式打开一个文件用于只读
    s = f.read(nRows * nCols * 4)   #总的字节数
    data = np.array(unpack(fmt, s))    #unpack()函数实现字节串转数字，以fmt的格式，将字节串s转换成数字
    list = data.reshape((440, 700))
    f.close()
    return list

#从原始.grd数据中提取各个格网单元的降水数据
def extract_rainfall_data(file_dir, store_dir, year):
    # 创建一个用以存储各格网单元降水数据的二维列表
    datalist = []
    #读取中国区域内的栅格数据
    fn = r"H:\Academy\data\China_region_WGS84\China.tif"
    ds = gdal.Open(fn)
    extent_china = ds.ReadAsArray(0, 0, nCols, nRows)
    for j in range(nRows):
        for k in range(nCols):
            if extent_china[j][k] == 0:
                continue
            datalist.append([])

    #遍历指定年份文件夹下的逐小时降水数据文件
    path_year = file_dir + "\\" + str(year)
    for month in os.listdir(path_year):
        mon_num = os.path.splitext(month)[0][-1:]
        if int(mon_num) in range(6, 9):
            path_month = path_year + "\\" + str(month)
            for filename in os.listdir(path_month):
                start_time = os.path.splitext(filename)[0][-10:]
                time = datetime.datetime.strptime(start_time, "%Y%m%d%H")
                # 读取文件
                filepath = path_month + "\\" + filename
                data = readfile(filepath)
                # 将单个栅格文件中对应格网的数据存入对应序号的列表里中
                index = 0
                for j in range(nRows):
                    for k in range(nCols):
                        if extent_china[j][k] == 0:
                            continue
                        if float(data[439-j][k]) > minimum:
                            s = '%s,%.4f\n' % (str(time), float(data[439-j][k]))
                            datalist[index].append(s)
                        index += 1

    # 将指定年份数据存入列表中后，将对应列表索引号的格网单元降水数据写入csv文件中
    index = 0
    for j in range(nRows):
        for k in range(nCols):
            if extent_china[j][k] <= 0:
                continue
            isExists = os.path.exists(store_dir)
            # 判断结果
            if not isExists:
                # 如果不存在则创建目录
                # 创建目录操作函数
                os.makedirs(store_dir)
            # 按照栅格所在的行列号以及索引号命名降水事件文件
            store_path = store_dir + "\\" + "rainfall_" + str(j + 1) + "_" + str(k + 1) + "_No." + str(index + 1) + ".csv"
            f1 = open(store_path, 'a')
            # f1.write("start_time" + "," + "rainfall_value" + "\n")
            for data in datalist[index]:
                (s1, s2) = data.split(',')
                f1.write(s1 + "," + s2)
            index += 1

if __name__ == '__main__':
    file_dir = "H:\\China_grid_rainfall_hourly"
    store_dir = "H:\\preci-extract\\rainfall_variation\\data_input_output\\data_all_6-8_change_rows"

    for year in range(2008, 2017):
        extract_rainfall_data(file_dir, store_dir, year)