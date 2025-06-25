# -*- coding: utf-8 -*-
"""
@author: Dori M. Grijseels
"""

import librosa
import pandas as pd
import numpy as np
import os
import soundfile as sf


def find_all_text_files(folders, check_sub_folders=1):
    """Find all files with a .txt extension in all folders in folder list (and subfolders if check_sub_folders = 1 (default))"""
    all_files = []
    for f, folder in enumerate(folders):
        for subfolder in os.listdir(folder):

            if os.path.isdir(os.path.join(folder, subfolder)):
                if check_sub_folders:
                    folders.append(os.path.join(folder, subfolder))                
            elif subfolder.endswith(".txt"):
                all_files.append(os.path.join(folder,subfolder))
    return all_files

def load_calls(file, delimiter='\t'):
    """Extract calls from txt outputed by Audacity.
    The file should be a tab-separated csv file with 3 columns and no headers.
    """
    # read calls into pandas dataframe
    calls = pd.read_csv(file, delimiter='\t', names = ['start_time', 'end_time', 'call_type'])
    calls = calls.fillna('nan')

    # Clean up call type
    calls['call_type'] = calls['call_type'].apply(lambda x: x.lower().strip() if isinstance(x, str) else x)
    
    return calls

def load_wav_file(file, goal_sr=22050):
    """Finds the wav file with the same name as the .txt file
    All files are resampled to goal_sr"""
    dataset = os.path.splitext(file)[0]
    folder_name, fname = os.path.split(dataset)
    data, samplerate = sf.read(os.path.join(folder_name, fname+'.wav'))
    if data.ndim>1:
        data = data[:,0]
    if samplerate >goal_sr:
        data = librosa.resample(data, orig_sr=samplerate, target_sr=goal_sr)
    return data, goal_sr

def extract_and_resample_wavs(calls, wav_data, samplerate):
    """Extract spectrogram and wav file for each call"""
    # Spectrogram settings
    nfft = 128
    hop_length = int(nfft/8)
    delta = 0.03 # seconds added on either end
    loudness_factor = 0.2
    cutoff_freq = 1000
    order = 4
    
    # Look through each call, load the wav snippet, recut the start and end, and save out the wav snippet
    call_wavs = []
    ori_lens = []
    new_lens  = []
    for index, call in calls.iterrows():
        t_start = max(0, int((call['start_time']-delta)*samplerate))
        t_end = min(int((call['end_time']+delta)*samplerate), len(wav_data))
        call_wav = wav_data[t_start:t_end]
  
        loudness_profile = librosa.feature.rms(y=call_wav, frame_length=nfft, hop_length = hop_length).T
  
        # Recut calls
        time_factor = len(call_wav)/len(loudness_profile)
        max_loudness_profile = np.nanmax(loudness_profile)
        fwhm = (max_loudness_profile-np.nanmin(loudness_profile))*loudness_factor+np.nanmin(loudness_profile)
        new_start_time = np.where(loudness_profile>fwhm)[0][0]
        new_end_time = np.where(loudness_profile>fwhm)[0][-1]
        
        start_time = (t_start+int(new_start_time*time_factor))/samplerate
        end_time = (t_start+int(new_end_time*time_factor))/samplerate
        
        call_wav = wav_data[t_start+int(new_start_time*time_factor):t_start+int(new_end_time*time_factor)]
        call_wavs.append(call_wav)
        
        ori_lens.append(call['end_time']-call['start_time'])
        new_lens.append(end_time-start_time)
        

    calls['wav'] = call_wavs
    calls['ori_len'] = ori_lens
    calls['new_len'] = new_lens
    calls['samplerate'] = samplerate
    return calls


def clean_call_types(all_calls):
    """Clean call types by combinding subcategories and fixing typos"""
    all_calls['call_type'] = all_calls['call_type'].apply(lambda x: x.lower().strip() if isinstance(x, str) else x)
    all_calls['call_type'] = all_calls['call_type'].replace('us', 'ph')
    all_calls['call_type'] = all_calls['call_type'].replace('ds', 'ph')
    all_calls['call_type'] = all_calls['call_type'].replace('gc', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('check', '?')
    all_calls['call_type'] = all_calls['call_type'].replace('nan', '?')
    all_calls['call_type'] = all_calls['call_type'].replace('cs', '?')
    all_calls['call_type'] = all_calls['call_type'].replace('a', 's')
    all_calls['call_type'] = all_calls['call_type'].replace('coo', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('gr', 'g')
    all_calls['call_type'] = all_calls['call_type'].replace('c', 'co')
    all_calls['call_type'] = all_calls['call_type'].replace('pupf', 'mo')
    all_calls['call_type'] = all_calls['call_type'].replace('g', 'gr')
    all_calls['call_type'] = all_calls['call_type'].replace('s', 'sc')
    all_calls['call_type'] = all_calls['call_type'].replace('wh', 'ph')
    all_calls['call_type'] = all_calls['call_type'].replace('w', 'ph')
    all_calls['call_type'] = all_calls['call_type'].replace('mo', 'ph')
    return all_calls