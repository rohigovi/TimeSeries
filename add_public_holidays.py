from datetime import date
import holidays
import numpy as np
import pandas as pd
import os

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
data_frame = pd.read_csv(csv_path, parse_dates=True)
# Select country
us_holidays = holidays.US()


# If it is a holidays then it returns True else False

# What holidays is it?

for index, row in data_frame.iterrows():
    # print(row['trans_date'])
    # print(us_holidays.get(row['trans_date']))
    if  not pd.isna(row['trans_date']):
        if not us_holidays.__contains__(row['trans_date']):
            # print(us_holidays.get(row['trans_date']))
            data_frame.loc[index,'Event'] = 'None'
        else:
            data_frame.loc[index, 'Event'] = us_holidays.get(row['trans_date'])

print(data_frame['Event'])

data_frame.to_csv('Multivariate_Data_Added_Holidays.csv')