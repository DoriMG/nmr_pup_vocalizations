# -*- coding: utf-8 -*-
"""
@author: Dori M. Grijseels
"""

import os
import pandas as pd
import numpy as np

data_folder = os.path.join(os.path.dirname(os.getcwd()), 'metadata')
out_folder = os.path.join(os.getcwd(), 'data')

## Load and preprocess Boffin 2 weights

df =  pd.read_csv(os.path.join(data_folder, 'boffin_2_weights.csv'), sep='\t', encoding='utf-16')

weight_cols = [col for col in df.columns if 'Weight' in col]
date_cols = [col for col in df.columns if 'Date' in col]
df_weights = []
for _, row in df.iterrows():        
    animalID = row['ID']
    animalID = animalID[-3:]
    DOB = pd.to_datetime(row['DOB'], errors='coerce')
    pd.to_datetime(DOB, errors='coerce')
    if len(weight_cols) == len(date_cols):
        for i in range(len(weight_cols)):
            weight_temp = row[weight_cols[i]]
            if type(weight_temp) == str:
                weight_temp = float(weight_temp.replace(',', '.'))
            date_temp = row[date_cols[i]]
            if type(date_temp) == str:
                date_temp = pd.to_datetime(date_temp, errors='coerce')
                date_diff = (date_temp-DOB).days
            if not np.isnan(weight_temp):
                df_weights.append([animalID, date_diff, weight_temp])
df_weights = pd.DataFrame(df_weights, columns=['AnimalID', 'DateMeasured', 'Weight'])
df_weights.reset_index(inplace=True, names='WeightID')
n_weights = len(df_weights)

## Load and Boffin 2 lengths
len_df = pd.read_csv(os.path.join(data_folder, 'lengths_boffin2.csv'))
len_df['pup ID'] = len_df['pup ID'].astype(str)


## Consolidate weight into lengths data
len_df['weight'] = np.nan
for idx, row in len_df.iterrows():
    ID = row['pup ID']
    day = row['day']
    weight_row = df_weights[(df_weights['AnimalID'] == ID) & (df_weights['DateMeasured'] == day)]
    len_df.at[idx, 'weight'] = weight_row['Weight']
    
    
len_df['potbelly'] = len_df['belly_width']/len_df['body_length']
len_df['rel_head'] = len_df['head_width']/len_df['body_length']

len_df.to_csv(os.path.join(out_folder, 'body_development.csv'))