# -*- coding: utf-8 -*-
"""
Created on Sat May 10 21:07:23 2025

@author: door1
"""

import os
from datetime import datetime
import pandas as pd
import numpy as np
import librosa
from scipy.signal import butter, filtfilt
import noisereduce as nr
import cv2
from torch.utils.data import DataLoader
from vae.models.dataset import SyllableDataset, ToTensor
from vae.models.vae import VAE

# custom imports
# Custom functions import
from feature_extraction import compute_all_features
from preprocessing import clean_call_types, extract_and_resample_wavs, find_all_text_files, load_calls, load_wav_file

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


# Spectrogram settings
nfft = 512
win_length = int(nfft/2)
hop_length = int(win_length/4)
cutoff_freq = 1000
order = 4
X_SHAPE = (128,128)
reload = 1

# List all folders to extract
data_folder = r"\\gpfs.corp.brain.mpg.de\bark\data\1_Projects\pup_paper\data"
colonies = ['took_adults', 'boffin_adults', 'lannister_adults']

# Load metadata
metadata = pd.read_csv(r'..\metadata\adult_info.csv', sep='\t', encoding='utf-16')
metadata['short_ID'] = [x.strip()[-4:] for x in metadata['ID']]
metadata['chip'] = [str(x).strip()[-4:] for x in metadata['Lab ID']]

all_calls_list = [] # List will contain all dictionaries, to be concatenated into a giant dataframe at the end
for colony in colonies:
    folders = [os.path.join(data_folder, colony)]
       
    all_files = find_all_text_files(folders, check_sub_folders=1)
    clean_files = [file for file in all_files if '._' not in file and '_fs' not in file]
    
    for file in clean_files:
        print(file)
        
        ## Extract recording date and animal ID
        date = file.split('_')[-3]
        ani_id = file.split('_')[-2]
        
        # Boffin is indexed by chip not by animal id
        if colony=='boffin_adults':
            temp_df = metadata[metadata['chip'] == ani_id]
            ani_id = temp_df['short_ID'].values[0]
        
        temp_df = metadata[metadata['short_ID'] == ani_id]
        birthdate = datetime.strptime(temp_df['DOB'].values[0], '%Y-%m-%d')
    
        ani_id = temp_df['ID'].values[0][-4:]
        if len(date) == 8:
            time_point = (datetime.strptime(date, '%d-%m-%Y')-birthdate).days
        else:
            time_point = (datetime.strptime(date, '%y%m%d')-birthdate).days
        
        # extract all calls
        calls = load_calls(file,  delimiter='\t')
        calls['call_type'].replace('nan', 'sc') # In adults empty call type indicates sc
        
        # extract wav file
        wav_data, samplerate = load_wav_file(file)
        
        # high-pass filter the data
        nyq = 0.5 * samplerate
        normal_cutoff = cutoff_freq / nyq
        b, a = butter(order, normal_cutoff, btype='highpass') 
        filtered_data = filtfilt(b, a, wav_data)
        reduced_noise = nr.reduce_noise(y=filtered_data, sr=samplerate)
        
        # get individual wav snippet and spectrogram per call
        calls = extract_and_resample_wavs(calls, reduced_noise, samplerate)
        
        # Create folder to save out spectrograms
        head, tail = os.path.split(file)
        file_name = tail.split('.')[0]
        out_path = os.path.join(head, file_name)
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        if not os.path.exists(out_path+'_wavs'):
            os.mkdir(out_path+'_wavs')
        
        # save out spectrograms
        out_files = []
        wav_files = []
        for index, row in calls.iterrows():
            audio = row['wav']
            sr = row['samplerate']
            spec = librosa.feature.melspectrogram(y=audio, sr = samplerate,  
                                                  n_fft=nfft, win_length=win_length, 
                                                  hop_length=hop_length, fmax=8000, fmin=1000,n_mels=64)
            S = np.abs(spec)
            S = np.log(spec)
            
            S_resize = cv2.resize(S, X_SHAPE, interpolation=cv2.INTER_CUBIC)
            S_resize = (S_resize-np.min(S_resize))/(np.max(S_resize)-np.min(S_resize))
            
            save_file = os.path.join(out_path, str(index)+'.npy')
            out_files.append(save_file)
            np.save(save_file, S_resize)
            
            save_file = os.path.join(out_path+'_wavs', str(index)+'.npy')
            wav_files.append(save_file)
            np.save(save_file, audio)
        calls['spec_file'] = out_files
        calls['wav_file'] = wav_files
        calls['ann_file'] = file
        
        # Add metadata
        calls['timepoint'] = time_point
        calls['animal_id'] = ani_id
        calls['colony'] = colony
        
        all_calls_list.append(calls)

all_calls = pd.concat(all_calls_list, ignore_index=True)
all_calls = clean_call_types(all_calls)

out_folder = r'..\\metadata'
all_calls.to_csv(os.path.join(out_folder, 'call_dataset_adults.csv'))

## Run feature extraction
samplerate = 22050

# Calculate all features        
all_calls = compute_all_features(all_calls, samplerate, n_fft = 256, preload=0)

# Add column to determine whether it was a recording in the no-touch condition
all_calls['isolate'] = 'True'
all_calls = clean_call_types(all_calls)

# Save out the features
all_calls.to_csv(os.path.join(out_folder, 'features_dataset_adults.csv'))

## Extract latent features
# Create the dataset
dataset = SyllableDataset(all_calls, 'spec_file', transform=ToTensor())
hyperparams = {
		"z_dim": 32,
		"num_data": None, # None for all data 
		"epochs": 100,
        "train_size": 0.8
		}

## Load model 
save_dir = r"../models"
model = VAE(z_dim=hyperparams["z_dim"], save_dir=save_dir, model_name="vae")
model_checkpoint = os.path.join(save_dir, 'vae_checkpoint_99.pt')
model.load_state(model_checkpoint)

# #xtract latent means
dataloader = DataLoader(dataset, batch_size=4, shuffle=False)
latent_means = model.get_latent(dataloader)

n_latent_means = 32
for i in range(n_latent_means):
	all_calls[f'latent_mean_{i}'] = latent_means[:, i]

all_calls.to_csv(os.path.join(out_folder, 'vae_features_adults.csv'))
