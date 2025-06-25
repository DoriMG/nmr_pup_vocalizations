# -*- coding: utf-8 -*-
"""
@author: Dori M. Grijseels
"""

import sys
import os
from datetime import datetime
import pandas as pd
import numpy as np
import librosa
from scipy.signal import butter, filtfilt
import noisereduce as nr
import cv2

# Custom functions import
from preprocessing import clean_call_types, extract_and_resample_wavs, find_all_text_files, load_calls, load_wav_file

# Spectrogram settings
nfft = 512
win_length = int(nfft/2)
hop_length = int(win_length/4)
cutoff_freq = 1000
order = 4
X_SHAPE = (128,128)
reload = 1

# List all folders to extract
colonies = ['boffin', 'lannister','boffin_2']

all_calls_list = [] # List will contain all dictionaries, to be concatenated into a giant dataframe at the end
for colony in colonies:
    folders = [os.path.join(r"../data", colony)]
    
    # Hard-coded birth dates for the 3 litters
    if colony == 'boffin':
        birthdate = datetime.strptime('27-02-2024', '%d-%m-%Y')
    if colony == 'lannister':
        birthdate = datetime.strptime('02-10-2024', '%d-%m-%Y')
        folders = [r'\\gpfs.corp.brain.mpg.de\bark\data\1_Projects\pup_paper\data\lannister\isolate\20241003',
                   r'\\gpfs.corp.brain.mpg.de\bark\data\1_Projects\pup_paper\data\lannister\isolate\20241005',
                   r'\\gpfs.corp.brain.mpg.de\bark\data\1_Projects\pup_paper\data\lannister\probed\20241003',
                   r'\\gpfs.corp.brain.mpg.de\bark\data\1_Projects\pup_paper\data\lannister\probed\20241005']
    if colony == 'boffin_2':
        birthdate = datetime.strptime('02-04-2025', '%d-%m-%Y')
        folders = [r'\\gpfs.corp.brain.mpg.de\bark\data\1_Projects\pup_paper\data\boffin_2\isolate',
                   r'\\gpfs.corp.brain.mpg.de\bark\data\1_Projects\pup_paper\data\boffin_2\probed']
    
    
    # Find all txt files in the folder
    all_files = find_all_text_files(folders, check_sub_folders=1)
    
    #Clean hidden files made by Macs
    clean_files = [file for file in all_files if '._' not in file ]
    
    for file in clean_files:
        print(file)
        
        ## Extract recording date and animal ID
        date = file.split('_')[-3]
        ani_id = file.split('_')[-2]
        
        # Check what format the recording date is in, and calculate pup age
        if len(date) == 8:
            time_point = (datetime.strptime(date, '%d-%m-%y')-birthdate).days
        else:
            time_point = (datetime.strptime(date, '%d-%m-%Y')-birthdate).days
        
        # extract all calls
        calls = load_calls(file,  delimiter='\t')
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
        
# Combine into one master dataframe
all_calls = pd.concat(all_calls_list, ignore_index=True)
all_calls = clean_call_types(all_calls)

# Save out
out_folder = r'..\\metadata'
all_calls.to_csv(os.path.join(out_folder, 'call_dataset.csv'))

