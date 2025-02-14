from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from datetime import datetime, timedelta
import pandas as pd
import math
import numpy as np
import random
from tqdm import trange

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

from math import sqrt
from pandas import read_csv, DataFrame
from scipy import stats

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
from random import *


def prep_data(data, covariates, data_start, train = True):
 time_len = data.shape[0]
 # print("time_len: ", time_len)
 input_size = window_size-stride_size
 windows_per_series = np.full((num_series), (time_len-input_size) // stride_size)
 # print("windows pre: ", windows_per_series.shape)
 if train: windows_per_series -= (data_start+stride_size-1) // stride_size
 # print("data_start: ", data_start.shape)
 print(data_start)
 # print("windows: ", windows_per_series.shape)
 print(windows_per_series)
 total_windows = np.sum(windows_per_series)
 x_input = np.zeros((total_windows, window_size, 1 + num_covariates +1), dtype='float32')
 label = np.zeros((total_windows, window_size), dtype='float32')
 v_input = np.zeros((total_windows, 2), dtype='float32')
 #cov = 3: ground truth + age + day_of_week + hour_of_day + num_series
 #cov = 4: ground truth + age + day_of_week + hour_of_day + month_of_year + num_series
 count = 0
 if not train:
 covariates = covariates[-time_len:]
 for series in trange(num_series):
 cov_age = stats.zscore(np.arange(total_time-data_start[series]))
 if train:
 covariates[data_start[series]:time_len, 0] = cov_age[:time_len-data_start[series]]
 else:
 covariates[:, 0] = cov_age[-time_len:]
 for i in range(windows_per_series[series]):
 if train:
 window_start = stride_size*i+data_start[series]
 else:
 window_start = stride_size*i
 window_end = window_start+window_size
 # '''

 # print("x: ", x_input[count, 1:, 0].shape)
 # print("window start: ", window_start)
 # print("window end: ", window_end)
 # print("data: ", data.shape)
 # print("d: ", data[window_start:window_end-1, series].shape)
 # '''
 x_input[count, 1:, 0] = data[window_start:window_end-1, series]
 x_input[count, :, 1:1+num_covariates] = covariates[window_start:window_end, :]
 x_input[count, :, -1] = series

 label[count, :] = data[window_start:window_end, series]
 nonzero_sum = (x_input[count, 1:input_size, 0]!=0).sum()
 print(x_input)
 if nonzero_sum == 0:
 v_input[count, 0] = 0
 else:
 v_input[count, 0] = np.true_divide(x_input[count, 1:input_size, 0].sum(),nonzero_sum)+1
 x_input[count, :, 0] = x_input[count, :, 0]/v_input[count, 0]
 if train:
 label[count, :] = label[count, :]/v_input[count, 0]
 count += 1
 prefix = os.path.join(save_path, 'train_' if train else 'test_')
 np.save(prefix+'data_'+save_name, x_input)
 print("Data Shape =" + str(x_input.shape))
 np.save(prefix+'v_'+save_name, v_input)
 np.save(prefix+'label_'+save_name, label)
 print("Label input.shape" + str(label.shape))

def gen_covariates(times, num_covariates):
 covariates = np.zeros((times.shape[0], num_covariates))
 for i, input_time in enumerate(times):
 covariates[i, 1] = input_time.weekday()
 covariates[i, 2] = input_time.hour
 covariates[i, 3] = input_time.month
 for i in range(1,num_covariates):
 covariates[:,i] = stats.zscore(covariates[:,i])

 for i in range(covariates.shape[0]):
 for j in range(covariates.shape[1]):
 if(np.isnan(covariates[i,j])):
 covariates[i,j] = 0;
 return covariates[:, :num_covariates]

def visualize(data, week_start):
 x = np.arange(window_size)
 f = plt.figure()
 plt.plot(x, data[week_start:week_start+window_size], color='b')
 f.savefig("visual.png")
 plt.close()

if __name__ == '__main__':

 global save_path
 # name = 'LD2011_2014.txt'
 name = 'Multivariate_data.csv'
 save_name = 'elect'
 window_size = 20
 stride_size = 1
 num_covariates = 4

 train_start = '2019-12-23 00:00:0000'
 train_end = '2023-10-09 00:00:0000'
 test_start = '2023-10-16 00:00:0000'
 # need additional 7 days as given info
 test_end = '2025-10-13 00:00:0000'
 pred_days = 7
 given_days = 7

 save_path = os.path.join('data', save_name)
 if not os.path.exists(save_path):
 os.makedirs(save_path)
 csv_path = os.path.join(save_path, name)
 if not os.path.exists(csv_path):
 zipurl = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip'
 with urlopen(zipurl) as zipresp:
 with ZipFile(BytesIO(zipresp.read())) as zfile:
 zfile.extractall(save_path)

 data_frame = pd.read_csv(csv_path,parse_dates=True)
 time_stamps = data_frame["Month"].to_numpy()

 for idx, x in np.ndenumerate(time_stamps):
 d = datetime.strptime(time_stamps[idx], '%d-%b-%y')
 time_stamps[idx] = d.strftime('%d-%m-%Y')
 print(time_stamps[idx])



 data_frame = pd.read_csv(csv_path, index_col=0, parse_dates=True)
 data_frame = data_frame.drop(['Family', 'Color','County', 'Article','Sub_Family','Distribution','Size','FabricType'], axis=1)
 data_frame = data_frame.dropna(how='any')
 one_hot = pd.get_dummies(data_frame['Event'])
 data_frame = data_frame.drop('Event', axis=1)
 # Join the encoded df
 data_frame = data_frame.join(one_hot)
 columns_titles = ["Price (Euros)", "Discount", "Child Health Day",
 "Christmas Season", "Columbus Day", "Cyber Monday", "Easter Monday",
 "First Day of Pride Month", "President's Day", "Raksha Bandhan",
 "Stephen Foster Memorial Day", "Super Bowl","sales_units"]
 data_frame = data_frame.reindex(columns=columns_titles)

 print(data_frame.columns)

 covariates = gen_covariates(data_frame[train_start:test_end].index, num_covariates)
 train_data = data_frame[train_start:train_end].values
 train_data = data_frame[train_start:train_end].values
 test_data = data_frame[test_start:test_end].values
 # f = plt.figure()
 # plt.plot(data_frame['Sales_qty'])
 # f.savefig('hey.png')

 print("Shape =" + str(train_data.shape))
 print("Shape =" + str(test_data.shape))
 data_start = (train_data!=0).argmax(axis=0) #find first nonzero value in each time series
 total_time = data_frame.shape[0]
 num_series = data_frame.shape[1]
 prep_data(train_data, covariates, data_start)
 prep_data(test_data, covariates, data_start, train=False)
 # print(train_data)
