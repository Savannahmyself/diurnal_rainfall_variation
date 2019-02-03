#! /usr/bin/env python
# coding=utf-8
import csv
import datetime
import gdal
import numpy as np
import os
import pandas as pd
import string
import sys
from dateutil.parser import parse
from time import time
nRows = 440
nCols = 700

cell_num = 95337  #中国区总的有效格网单元数
minimum = 1e-20  #一个极小值

def cal_norm_rainfall_data(row,col):

    path = r"H:\preci-extract\rainfall_variation\data_input_output\data_all_6-8_change_rows"
    files = os.listdir(path)
    filename = 'rainfall_%d_%d_'%(row, col)

    for file in files:
        if file.endswith('.csv') and filename in file:
            filepath = path + '\\' + file
            df = pd.read_csv(filepath, encoding='utf-8', header=None)
            # 创建24小时降水量列表，用以存储08-16年，每个格网单元每小时（0~23）的降水量数据
            amount = []
            for i in range(24):
                amount.append([])
            # 遍历该格网单元数据表中的数据，提取开始时间，并筛选夏季（6、7、8 三个月）的降水量数据存入对应小时的列表中
            year_list = []
            for i in range(len(df)):
                value = float(df.iloc[i, 1])  # 1h降水事件数值
                if 0.1 <= value <= 100:  # 限定有效降水数据的范围
                    time = parse(str(df.iloc[i, 0]))  # 开始时间（UTC），LST=UTC+Lon/15
                    delta_time = round((69.95 + 0.1 * col) / 15)  # 计算该格网单元与UTC时间的时差,四舍五入
                    lst_time = time + datetime.timedelta(hours=int(delta_time))  # 计算该格网单元的地方太阳时（LST）
                    # if int(lst_time.year) in range(2008, 2017):
                    #     if int(lst_time.month) in range(6, 9):
                    hour = int(lst_time.hour)  # 获取小时数
                    year = int(lst_time.year)  # 获取年份数据
                    amount[hour].append(float(value))
                    if year not in year_list:  # 统计有效降水年份
                        year_list.append(year)

            year_num = len(year_list)
            # 计算0~23时，每小时的年均降水频率和降水量和降水强度，存储入列表
            fr_hourly_list = []
            am_hourly_list = []
            int_hourly_list = []
            for i in range(24):
                sum_f = len(amount[i])
                sum_a = sum(amount[i])
                fr_yearly = float(sum_f / float(year_num))
                am_yearly = sum_a / year_num
                if fr_yearly <= minimum:
                    int_yearly = 0
                else:
                    int_yearly = am_yearly / fr_yearly
                fr_hourly_list.append(fr_yearly)
                am_hourly_list.append(am_yearly)
                int_hourly_list.append(int_yearly)

            # 计算每个格网0~23时，标准化后每小时的年均降水频率和降水量
            average_fr = sum(fr_hourly_list) / 24
            average_am = sum(am_hourly_list) / 24
            average_int = sum(int_hourly_list) / 24
            fr_norm_list = []
            am_norm_list = []
            int_norm_list = []

            for i in range(24):
                if average_fr <= minimum:
                    fr_norm_value = 0
                else:
                    fr_norm_value = fr_hourly_list[i] / average_fr - 1

                if average_am <= minimum:
                    am_norm_value = 0
                else:
                    am_norm_value = am_hourly_list[i] / average_am - 1

                if average_int <= minimum:
                    int_norm_value = 0
                else:
                    int_norm_value = int_hourly_list[i] / average_int - 1

                fr_norm_list.append('%.2f' % fr_norm_value)
                am_norm_list.append('%.2f' % am_norm_value)
                int_norm_list.append('%.2f' % int_norm_value)
    return fr_norm_list, am_norm_list, int_norm_list


if __name__ == '__main__':
    # 创建用于存储所有格网单元，标准化后的24小时年均降水频率和年均降水量数据的列表
    fre_all = [[] for row in range(cell_num)]
    amu_all = [[] for row in range(cell_num)]
    int_all = [[] for row in range(cell_num)]
    fre_norm = []
    am_norm = []
    int_norm = []

    # 读取中国区域内的栅格数据
    fn = r"G:\rainfall_variation\China_new.tif"
    ds = gdal.Open(fn)
    extent_china = ds.ReadAsArray(0, 0, nCols, nRows)
    index = 0
    for i in range(nRows):
        for j in range(nCols):
            if extent_china[i, j] == 1:
                fre_norm, am_norm, int_norm = cal_norm_rainfall_data(i+1, j+1)
                # 将每个格网单元24小时的标准化降水频率和降水量数据存入最终汇总的列表中
                for k in range(24):
                    fre_all[index].append(fre_norm[k])
                    amu_all[index].append(am_norm[k])
                    int_all[index].append(int_norm[k])
                index += 1
    # print(fre_all)
    # 汇总完的所有格网单元标准化后的数据存储入相应的csv表中
    store_path = r"G:\rainfall_variation\data_in_out_1228\data_input"
    isExists = os.path.exists(store_path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(store_path)
    # 按照不同历时命名文件
    str_path_fre = store_path + "\\" + "08-16" + "_6-8month_yearly_normalized_frequency" + ".csv"
    str_path_amu = store_path + "\\" + "08-16" + "_6-8month_yearly_normalized_amount" + ".csv"
    str_path_int = store_path + "\\" + "08-16" + "_6-8month_yearly_normalized_intensity" + ".csv"

    f_fre = open(str_path_fre, 'w')
    f_amu = open(str_path_amu, 'w')
    f_int = open(str_path_int, 'w')

    for i in range(cell_num):
        for j in range(23):
            f_fre.write(str(fre_all[i][j]) + ',')
            f_amu.write(str(amu_all[i][j]) + ',')
            f_int.write(str(int_all[i][j]) + ',')
        f_fre.write(str(fre_all[i][23]) + '\n')
        f_amu.write(str(amu_all[i][23]) + '\n')
        f_int.write(str(int_all[i][23]) + '\n')
