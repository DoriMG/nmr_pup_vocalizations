"""
@author: Dori M. Grijseels
"""

import sys
import os
import pandas as pd
import numpy as np

# Custom functions import
sys.path.append(r'../util')
from feature_extraction import compute_all_features

def convert_to_R(data, columns):
    """ Function to transform a N-shaped array into a pd DataFrame with N+1 columns"""
    shape = data.shape
    index = pd.MultiIndex.from_product([range(s)for s in shape], names=columns)
    df = pd.DataFrame({'data': data.flatten()}, index=index).reset_index()
    return df


def clean_call_types(all_calls):
    """ Additional cleaning of typos if needed"""
    all_calls['call_type'] = all_calls['call_type'].replace('yq', 'sq')
    all_calls['call_type'] = all_calls['call_type'].replace('rw', '?')
    all_calls['call_type'] = all_calls['call_type'].replace('cop', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('ci', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('xo', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('coi', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('cj', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('co0', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('vo', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('cp', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('o', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('coc', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('co<', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('oc', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('gr', '?')
    all_calls['call_type'] = all_calls['call_type'].replace('tw', '?')
    all_calls['call_type'] = all_calls['call_type'].replace('?', 'other')
    return all_calls

data_folder = r'..\metadata'
out_folder = r'data'

# Load the dataset output by extract_spectrograms
all_calls = pd.read_csv(os.path.join(data_folder, 'call_dataset.csv'))
samplerate = 22050

# Calculate all features        
all_calls = compute_all_features(all_calls, samplerate, n_fft = 256, preload=0)

# Add column to determine whether it was a recording in the no-touch condition
all_calls['isolate'] = all_calls['spec_file'].str.contains('isolate')
all_calls = clean_call_types(all_calls)

# Save out the features
all_calls.to_csv(os.path.join(out_folder, 'features_dataset.csv'))


####################### Analysis for Fig 1 ################################
# only include touch experiments
all_calls = all_calls[~all_calls['isolate']]

# Features to include
features = [ 'pitch',  'zero_crossings', 'duration', 'mean_entropy','voiced_perc', 'bandwidth', 'n_peaks']

# Find all unique pups and recording days to loop through
pup_id = all_calls['animal_id'].unique()
timepoints  = all_calls['timepoint'].unique()
sound_types = all_calls['call_type'].unique()

################# #### Fig 1C-F and Fig S1 ####################### 
# Create dataframe to save out mean features
mean_features = pd.DataFrame(columns=['timepoint', 'animal_ID', 'colony']+ features)

for id in pup_id:
    for tp in timepoints:
        # get all the labels from this file
        df_temp = all_calls[np.logical_and(all_calls['animal_id']==id, all_calls['timepoint']==tp)]
        if len(df_temp)>5:# Only include if at least 5 calls
             timepoint = df_temp['timepoint'].iloc[0]
             animalID = df_temp['animal_id'].iloc[0]
             colony = df_temp['colony'].iloc[0]
             #across all cts
             entry =  pd.DataFrame.from_dict({
                  "animal_ID": [animalID],
                  "timepoint": [timepoint],
                  "colony": [colony]
             })
             for f in features:
                 mean_of_feat = np.nanmean(df_temp[f])
                 entry[f] = mean_of_feat
             # Pitch only for >0.4 tonal
             pitch_df_temp = df_temp[df_temp['voiced_perc']>0.4]
             if len(pitch_df_temp)>5: # Only include if at least 5 calls
                 mean_of_feat = np.nanmean(df_temp['pitch'])
                 entry['pitch'] = mean_of_feat
             mean_features = pd.concat([mean_features, entry], ignore_index=True)
          
# Save out results
mean_features.to_csv(os.path.join(out_folder,'call_features.csv'), index=False)  

################# #### Fig 1L-N, Fig S3 ####################### 
# find individual call type abundance

sound_counts = pd.DataFrame(columns=['timepoint', 'animal_ID', 'colony']+ sound_types.tolist())
# Get the mean counts for each pup for each timepoint 
for id in pup_id:
    for tp in timepoints:
        # get all the labels from this file
        df_temp = all_calls[np.logical_and(all_calls['animal_id']==id, all_calls['timepoint']==tp)]
        if len(df_temp)>0:
            timepoint = df_temp['timepoint'].iloc[0]
            animalID = df_temp['animal_id'].iloc[0]
            colony = df_temp['colony'].iloc[0]
            number_of_sounds = len(df_temp)
            sound_count_array = np.zeros((sound_types.__len__(), ))
            for s,sound_type in enumerate(sound_types):
            
                # Calculate percentage calls per dataset
                curr_count = len(df_temp[df_temp['call_type']==sound_type])
                sound_count_array[s] = curr_count/number_of_sounds
            
            sound_counts.loc[len(sound_counts.index)] = [timepoint,animalID,colony] + sound_count_array.tolist()  
            

# Transform the count data to a way that GGplot can easily use
count_data =pd.DataFrame(columns=['data','vocal_type', 'day', 'vocal_int', 'timepoint', 'animal_id'])
# sound_types = np.asarray(['ch', 'co', 'ph','sc', 'sq','tw','?'])
all_animals = sound_counts['animal_ID'].unique()
timepoint_lists = []
for animal in all_animals:
    df_temp = sound_counts[sound_counts['animal_ID'] == animal]
    timepoint = df_temp['timepoint'].iloc[0]
    animalID = df_temp['animal_ID'].iloc[0]
    counts =df_temp[sound_types].values
    timepoints  = df_temp['timepoint'].unique()
    
    count_data_temp = convert_to_R(counts, ['timepoint', 'vocal_int'])
    count_data_temp['day'] = timepoints[(count_data_temp['timepoint']).astype(int)]
    count_data_temp['vocal_type'] = sound_types[(count_data_temp['vocal_int']).astype(int)]
    count_data_temp['animal_id'] = animalID
    count_data_temp['colony'] =  df_temp['colony'].iloc[0]
    count_data = pd.concat([count_data, count_data_temp], ignore_index=True)
   

count_data.to_csv(os.path.join(out_folder,'call_occurence_by_animal.csv'), index=False) 
    
