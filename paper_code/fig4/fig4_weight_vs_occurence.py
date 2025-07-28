# -*- coding: utf-8 -*-
"""
@author: Dori M. Grijseels
"""
import os
import pandas as pd
import numpy as np

data_folder = os.path.join(os.path.dirname(os.getcwd()), 'metadata')
out_folder = os.path.join(os.getcwd(), 'data')


## Preprocess weights
df = pd.read_csv(os.path.join(data_folder, 'all_weights_combined.csv'), sep='\t', encoding='utf-16')

boffin1_ids = ['0278', '0279', '0280', '0281', '0282', '0283', '0284', '0285']
lannister_ids = ['0321', '0322', '0323', '0324', '0325', '0326', '0327', '0328']
boffin2_ids = ['0409', '0411', '0412', '0413', '0415', '0416', '0418']

weight_cols = [col for col in df.columns if 'Weight' in col]
date_cols = [col for col in df.columns if 'Date' in col]
df_weights = []
for _, row in df.iterrows():        
    animalID = row['ID']
    animalID = '0'+animalID[-3:]
    if animalID in boffin1_ids:
        colony = 'Boffin'
    if animalID in lannister_ids:
        colony = 'Lannister'
    if animalID in boffin2_ids:
        colony = 'Boffin 2'
        
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
                df_weights.append([animalID, date_diff, weight_temp, colony])
df_weights = pd.DataFrame(df_weights, columns=['AnimalID', 'DateMeasured', 'Weight', 'Colony'])
df_weights.reset_index(inplace=True, names='WeightID')

df_weights.to_csv(os.path.join(out_folder,'all_weights.csv'))


###### Figure 4B-C######################

# load lannister ID translation - to fix difference between pup and adult ID numbers
lan_id= pd.read_csv(os.path.join(data_folder, 'lannister_id.csv'), sep='\t', encoding='utf-16')


## Load occurence from fig 1
call_occurence = pd.read_csv(os.path.join(os.path.dirname(os.getcwd()), r'fig1\data\call_occurence_by_animal.csv'), sep=',', encoding='utf-8')

## Include only soft chirps
sc_occurence = call_occurence[call_occurence['vocal_type']=='sc']


sc_occurence['weight'] = np.nan

for index,row in sc_occurence.iterrows():        
    animalID = row['animal_id']
    if row['colony'] == 'lannister':
        animalID = '0'+str(int(lan_id[lan_id['id_data'] == int('5914')]['id_abn']))
    day = row['day']
    corr_weight = df_weights[(df_weights['DateMeasured']==day) & (df_weights['AnimalID']==animalID)]
    if len(corr_weight)>0:
        weight = corr_weight['Weight'].values[0]
        sc_occurence.loc[index,'weight']=weight

sc_occurence.to_csv(os.path.join(out_folder,'sc_occ.csv'))


