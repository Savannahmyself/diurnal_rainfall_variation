# diurnal_rainfall_variation
codes about diurnal rainfall variation ：

extract_summer_data_China_change_rows.py:
从原始.grd数据中提取每个格网单元6~8月的有效降水数据(>=0.1mm)，将其存储入以该格网单元的行列号及索引号命名的.csv文件中。

China_Summer_rainfall_kmeans_input.py:
提取每个格网单元有效降水数据的.csv表中夏季（6、7、8三月数据）的降水数据，统计每个格网单元0-23小时，每个小时的年均降水频率和降水量，汇总中国区域所有的格网单元（95337个）的24小时频率数据和降水量、降水强度数据到.csv表中。

cal_kmeans_output.py
根据中国区每个格网单元0-23小时，每小时的年均降水频率和年均降水量、降水强度数据进行聚类分析，聚类数由2-30，对比聚类中心到各样点的距离平方和，选择合适的聚类数。非中国区域的数据赋值-99。

kmeans_merge.py:
计算每一类栅格数据的平均24小时降水变化值
