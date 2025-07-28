# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 13:22:20 2025

@author: door1
"""

import os
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from scipy.spatial import distance

import umap


def convert_to_R(data, columns):
    shape = data.shape
    index = pd.MultiIndex.from_product([range(s)for s in shape], names=columns)
    df = pd.DataFrame({'data': data.flatten()}, index=index).reset_index()
    return df


def fix_ID(all_calls):
    all_calls['animal_id'] = all_calls['animal_id'].astype(str)
    for index,row in all_calls.iterrows():        
        animalID = row['animal_id']
        if len(str(animalID)) ==3:
            animalID = '0'+str(animalID)
            all_calls.loc[index,'animal_id']=animalID
    return all_calls


data_folder = os.path.join(os.path.dirname(os.getcwd()), 'metadata')
out_folder = os.path.join(os.getcwd(), 'data')

adult_calls = pd.read_csv(os.path.join(data_folder,  'vae_features_adults.csv'))
pup_calls =  pd.read_csv(os.path.join(data_folder, 'vae_features_dataset.csv'))

# Clean datasets
adult_calls = adult_calls.iloc[:, -56:]
adult_calls['is_adult'] = True
pup_calls = pup_calls.iloc[:, -56:]
pup_calls['is_adult'] = False

# Combine data
all_calls = pd.concat([adult_calls, pup_calls], ignore_index=True)


## Only include scs from touch conditions
sc_calls = all_calls[all_calls['call_type'] == 'sc']
sc_calls = sc_calls[~sc_calls['isolate']]
sc_calls = sc_calls.reset_index()

## Importing causes the id to lose the leading 0, so add back in and convert to string
sc_calls = fix_ID(sc_calls)

# Exclude unknown animals
sc_calls = sc_calls[~(sc_calls['animal_id']=='na')]
sc_calls = sc_calls[~(sc_calls['animal_id']=='0000')]


## Create list of features
features = [  'zero_crossings', 'duration', 
            'mean_entropy',  'voiced_perc', 'bandwidth', 'n_peaks']
vae_features = []
n_latent_means = 32
for i in range(n_latent_means):
	vae_features+=[f'latent_mean_{i}']
    
all_features = features + vae_features
all_features_np = np.array(all_features)



# Create dataset for UMAP/random forest
X = sc_calls[all_features].to_numpy()
y = sc_calls['colony'].to_numpy()


############### Fig 3A ####################
x_norm = StandardScaler().fit_transform(X)
reducer = umap.UMAP()
embedding = reducer.fit_transform(x_norm)


# Create new DF to plot UMAP in R
umap_df = sc_calls[['call_type', 'timepoint', 'animal_id', 'colony', 'is_adult','wav_file']]
umap_df['umap_1'] = embedding[:,0]
umap_df['umap_2'] = embedding[:,1]

umap_df.to_csv(os.path.join(out_folder, 'umap_embedding_sc.csv'), index=False)


############### Fig 3B - distance to colony adult ####################
# Extract Boffin colony adults
sc_adult = umap_df[umap_df['is_adult']]
sc_adult = sc_adult[sc_adult['colony'] == 'boffin_adults']
ave_aduls = [sc_adult['umap_1'].mean(), sc_adult['umap_2'].mean()]

# Separate out pups
sc_pups = umap_df[~umap_df['is_adult']]
pup_id = sc_pups['animal_id'].unique()
timepoints = sc_pups['timepoint'].unique()


distance_time = pd.DataFrame(columns=['timepoint', 'animal_ID', 'colony', 'distance'])
for id in pup_id:
    for tp in timepoints:
        # get all the labels from this file
        df_temp = sc_pups[np.logical_and(sc_pups['animal_id']==id, sc_pups['timepoint']==tp)]
        if len(df_temp)>5:
            # find points in embedding in range
            ave_x = df_temp['umap_1'].mean()
            ave_y = df_temp['umap_2'].mean()
            dst = distance.euclidean([ave_x, ave_y], ave_aduls)
            
            timepoint = df_temp['timepoint'].iloc[0]
            animalID = df_temp['animal_id'].iloc[0]
            colony = df_temp['colony'].iloc[0]
            #across all cts
            entry =  pd.DataFrame.from_dict({
                 "animal_ID": [animalID],
                 "timepoint": [timepoint],
                 "colony": [colony],
                 "distance": [dst]
            })
            distance_time = pd.concat([distance_time, entry], ignore_index=True)
            
distance_time.to_csv(os.path.join(out_folder,'UMAP_distance_development.csv'), index=False)              


############### Fig 3C - distance within litters ####################
timepoints = sc_pups['timepoint'].unique()
pup_id = sc_pups['animal_id'].unique()
# Create time ranges, because recordings were not done on the exact same day
time_steps = np.arange(min(timepoints), 75, 5)

distance_litters = pd.DataFrame(columns=['timepoint', 'animal_ID', "animal_ID2", 'colony', 'distance'])
for tp_idx, tp in enumerate(time_steps[:-1]):
    # get all the labels from this file
    inc = np.logical_and(sc_pups['timepoint']>=time_steps[tp_idx], sc_pups['timepoint']<time_steps[tp_idx+1])
    for id1_idx, id1 in enumerate(pup_id):
        for id2 in pup_id[id1_idx+1:]:
            df_temp_id1 = sc_pups[np.logical_and(inc, sc_pups['animal_id']==id1)]
            df_temp_id2 = sc_pups[np.logical_and(inc, sc_pups['animal_id']==id2)]
            if (len(df_temp_id1)>5) & (len(df_temp_id2)>5):
                # find points in embedding in range
                ave_id1 = [df_temp_id1['umap_1'].mean(), df_temp_id1['umap_2'].mean()]
                ave_id2 = [df_temp_id2['umap_1'].mean(), df_temp_id2['umap_2'].mean()]
                dst = distance.euclidean(ave_id1, ave_id2)
                
                timepoint = tp
                animalID1 = id1
                animalID2 = id2
                same_colony = df_temp_id1['colony'].iloc[0] == df_temp_id2['colony'].iloc[0]
                #across all cts
                entry =  pd.DataFrame.from_dict({
                     "animal_ID": [animalID1],
                     "animal_ID2": [animalID2],
                     "timepoint": [timepoint+2],
                     "colony": [same_colony],
                     "distance": [dst]
                })
                distance_litters = pd.concat([distance_litters, entry], ignore_index=True)
            
distance_litters.to_csv(os.path.join(out_folder,'UMAP_litter_distance.csv'), index=False)      



### Figure S6A - Distance to other colony adults ###
sc_adult = umap_df[umap_df['is_adult']]
boffin_adults = sc_adult[sc_adult['colony'] == 'boffins_adults']
ave_boffin = [boffin_adults['umap_1'].mean(), boffin_adults['umap_2'].mean()]

took_adults = sc_adult[sc_adult['colony'] == 'took_adults']
ave_took = [took_adults['umap_1'].mean(), took_adults['umap_2'].mean()]


lan_adults = sc_adult[sc_adult['colony'] == 'lannister_adults']
ave_lan = [lan_adults['umap_1'].mean(), lan_adults['umap_2'].mean()]


sc_pups = umap_df[~umap_df['is_adult']]
pup_id = sc_pups['animal_id'].unique()
timepoints = sc_pups['timepoint'].unique()
distance_time = pd.DataFrame(columns=['timepoint', 'animal_ID', 'colony', 'distance'])
adults = ['boffin', 'took', 'lannister']
adult_aves = [ave_boffin, ave_took, ave_lan]
for id in pup_id:
    for tp in timepoints:
        # get all the labels from this file
        df_temp = sc_pups[np.logical_and(sc_pups['animal_id']==id, sc_pups['timepoint']==tp)]
        if len(df_temp)>5:
            
            # find points in embedding in range
            ave_x = df_temp['umap_1'].mean()
            ave_y = df_temp['umap_2'].mean()
            for adult_idx, adult in enumerate(adults):
                ave_aduls = adult_aves[adult_idx]
                dst = distance.euclidean([ave_x, ave_y], ave_aduls)
                
                timepoint = df_temp['timepoint'].iloc[0]
                animalID = df_temp['animal_id'].iloc[0]
                colony = df_temp['colony'].iloc[0]
                #across all cts
                entry =  pd.DataFrame.from_dict({
                     "animal_ID": [animalID],
                     "timepoint": [timepoint],
                     "colony": [colony],
                     'adult_colony': [adult],
                     "distance": [dst]
                })
                distance_time = pd.concat([distance_time, entry], ignore_index=True)
            
distance_time.to_csv(os.path.join(out_folder,'UMAP_distance_development_by_adult.csv'), index=False)              


### Figure S6B - adult Boffin litter distance to other colony adults ###

# Find the IDs of the original Boffin litter
boffin1_pups = sc_pups[sc_pups['colony'] == 'boffin']
pup_id = boffin1_pups['animal_id'].unique()

## Find those pups in the adult list
boffin1_adults = sc_adult[sc_adult['animal_id'].isin(pup_id)]

## Combine into a dataframe
boffin1_comb = pd.concat([boffin1_pups, boffin1_adults])

## Split the adults by when recorded as adults - only compare to original colony adults
sc_adult_temp = umap_df[umap_df['is_adult']]
sc_adult_temp['second_batch'] = sc_adult_temp['wav_file'].str.contains('10-06-2025', regex=False)

boffin1_adult = sc_adult_temp[sc_adult_temp['second_batch']]
boffin2_adult = sc_adult_temp[~sc_adult_temp['second_batch']]

ave_boffin1 = [boffin1_adult['umap_1'].mean(), boffin1_adult['umap_2'].mean()]

timepoints = boffin1_comb['timepoint'].unique()
distance_time = pd.DataFrame(columns=['timepoint', 'animal_ID', 'colony', 'distance', 'is_adult'])
for id in pup_id:
    for tp in timepoints:
        # get all the labels from this file
        df_temp = boffin1_comb[np.logical_and(boffin1_comb['animal_id']==id, boffin1_comb['timepoint']==tp)]
        if len(df_temp)>5:
            # find points in embedding in range
            ave_x = df_temp['umap_1'].mean()
            ave_y = df_temp['umap_2'].mean()
            
            timepoint = df_temp['timepoint'].iloc[0]
            animalID = df_temp['animal_id'].iloc[0]
            colony = df_temp['colony'].iloc[0]
            is_adult = df_temp['is_adult'].iloc[0]
            
          
            dst = distance.euclidean([ave_x, ave_y], ave_boffin1)
          
            
            #across all cts
            entry =  pd.DataFrame.from_dict({
                 "animal_ID": [animalID],
                 "timepoint": [timepoint],
                 "colony": [colony],
                 "distance": [dst],
                 'is_adult': [is_adult]
            })
            distance_time = pd.concat([distance_time, entry], ignore_index=True)
            
distance_time.to_csv(os.path.join(out_folder,'UMAP_distance_development_ori_pups.csv'), index=False)              

### Figure S6C - adult Boffin litter distance wintin ###

# Use previous dataset with Boffin litter as pups and adults
timepoints = boffin1_comb['timepoint'].unique()
pup_id = boffin1_comb['animal_id'].unique()

distance_litters = pd.DataFrame(columns=['timepoint', 'animal_ID', "animal_ID2", 'colony', 'distance'])
for tp_idx, tp in enumerate(timepoints):
    # get all the labels from this file
    inc = boffin1_comb['timepoint']==tp
    for id1_idx, id1 in enumerate(pup_id):
        for id2 in pup_id[id1_idx+1:]:
            df_temp_id1 = boffin1_comb[np.logical_and(inc, boffin1_comb['animal_id']==id1)]
            df_temp_id2 = boffin1_comb[np.logical_and(inc, boffin1_comb['animal_id']==id2)]
            if (len(df_temp_id1)>5) & (len(df_temp_id2)>5):
                # find points in embedding in range
                ave_id1 = [df_temp_id1['umap_1'].mean(), df_temp_id1['umap_2'].mean()]
                ave_id2 = [df_temp_id2['umap_1'].mean(), df_temp_id2['umap_2'].mean()]
                dst = distance.euclidean(ave_id1, ave_id2)
                
                timepoint = tp
                animalID1 = id1
                animalID2 = id2
                same_colony = df_temp_id1['colony'].iloc[0] == df_temp_id2['colony'].iloc[0]
                #across all cts
                entry =  pd.DataFrame.from_dict({
                     "animal_ID": [animalID1],
                     "animal_ID2": [animalID2],
                     "timepoint": [timepoint],
                     "colony": [same_colony],
                     "distance": [dst]
                })
                distance_litters = pd.concat([distance_litters, entry], ignore_index=True)
            
distance_litters.to_csv(os.path.join(out_folder,'UMAP_litter_distance_boffin1_litter.csv'), index=False)      


