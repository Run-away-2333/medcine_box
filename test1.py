# import os
#
# # current_dir = os.getcwd()
# # print("当前工作目录:", current_dir)
from typing import List
#
# temperatures: List[float] = [22.5, 23.1, 21.9, 22.0, 22.8]
# avernt = 0
# for i in temperatures:
#     avernt += i
# print("平均温度:", avernt / len(temperatures))
#
# print("最大:", max(temperatures))
# print("最小:", min(temperatures))
#
# temperatures.append(23.5)
#
# led_sequence = "1010001110"
# count = 0
# for i in led_sequence:
#     if i == '1':
#         count += 1
# print(count)
#
# for i in led_sequence[::-1]:
#     print(i, end='')
#
# print()
#
# new_str = ""
# for i in led_sequence:
#     if i == '0':
#         new_str += '1'
#     else:
#         new_str += '0'
#
# print(new_str)

# text_str = "<>"
# new_len = 0
# str_cnt = 0
# while True:
#     str_cnt = text_str[str_cnt:].find('>')
#     print(str_cnt)
#     if str_cnt != -1:
#         new_len += 1
#     else:
#         break
#
# lis_1 = []
# if lis_1 is None:
#     print("list")

import pandas as pd

# 1. 读取传感器数据文件
df = pd.read_csv('sensor_data.csv')

# 2. 显示数据的基本信息
print("数据基本信息:")
print(f"行数: {df.shape[0]}, 列数: {df.shape[1]}")
print(df.info())
print(df.describe())

# 3. 计算每个传感器的平均温度
avg_temp = df[['sensor_1', 'sensor_2', 'sensor_3', 'sensor_4']].mean()
print("\n每个传感器的平均温度:")
print(avg_temp)

# 4. 找出温度最高的时刻和对应的传感器
# 先将timestamp列转换为日期时间类型
df['timestamp'] = pd.to_datetime(df['timestamp'])
# 找出每个传感器的最高温度
max_temp = df[['sensor_1', 'sensor_2', 'sensor_3', 'sensor_4']].max()
print("\n每个传感器的最高温度:")
print(max_temp)

# 找出全局最高温度的时刻和传感器
max_value = df[['sensor_1', 'sensor_2', 'sensor_3', 'sensor_4']].values.max()
# 找出哪一行和哪一列包含最高温度
for col in ['sensor_1', 'sensor_2', 'sensor_3', 'sensor_4']:
    if max_value in df[col].values:
        max_row = df[df[col] == max_value]
        print(f"\n最高温度 {max_value}°C 出现在 {max_row['timestamp'].values[0]} 的 {col}")

# 5. 将每个传感器的温度数据重采样为每小时平均值 (已经是小时数据，这里作为演示)
# 设置timestamp为索引
df_indexed = df.set_index('timestamp')
# 重采样，如果需要其他时间间隔可以修改'H'
resampled = df_indexed.resample('H').mean()
print("\n重采样后的数据前5行:")
print(resampled.head())





