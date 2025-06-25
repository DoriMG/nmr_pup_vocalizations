# -*- coding: utf-8 -*-
"""
@author: Dori M. Grijseels
"""

""" This file contains all functions needed to extract softchirp features from traced spectrograms"""

import numpy as np
from librosa.core import piptrack
import librosa
import scipy
from scipy import stats
from scipy.ndimage import gaussian_filter1d
from scipy import ndimage
import cv2
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import time



def wiener_entropy(s_npy,  n_fft = 256, hop_length=64):
    """ Computes Wiener entropy of wav """
    ent = librosa.feature.spectral_flatness(y = s_npy,  n_fft = n_fft,hop_length=hop_length)
    return np.var(ent), np.mean(ent), np.max(ent), ent


def compute_zero_crossing(s_npy,):
    """ Computes averate zero crossing ratio of wav """
    return np.mean(librosa.zero_crossings(s_npy, pad=False))

def compute_duration(call):
    """Computes duration of the call """
    return call['new_len']

def compute_f0(data, samplerate, nfft, hop_length):
    """Computes the mean fundamental frequency and percentage voiced"""
    f0, voiced_flag, voiced_probs = librosa.pyin(data, sr=samplerate,frame_length=nfft, hop_length=hop_length, fmin=librosa.note_to_hz('C2'),fmax=8000, fill_na = np.nan)
    return np.nanmean(f0), np.mean(voiced_flag)

def compute_bandwidth(data, samplerate, nfft, hop_length,  win_length):
    """Computes the spectral bandwidth"""
    spec_bw = librosa.feature.spectral_bandwidth(y=data, sr=samplerate,n_fft=nfft, win_length=win_length, hop_length=hop_length)
    return np.nanmean(spec_bw)

def harmonic_peaks(data, samplerate, nfft, hop_length, win_length):
    """Computes the number of harmonic peaks"""
    pitches, magnitudes = librosa.piptrack(y=data, sr=samplerate,n_fft=nfft, win_length=win_length, hop_length=hop_length)
    n_peaks = np.sum(pitches>0, axis=0)
    return np.nanmean(n_peaks)


def compute_all_features(calls, samplerate,  n_fft=256, preload = 1):
    """ Computes all the features for each call and adds it to the all_calls file"""
    features = [ 'pitch',  'zero_crossings', 'duration', 
                'entropy_variance', 'mean_entropy', 'maximum_entropy', 'voiced_perc', 'bandwidth', 'n_peaks']
      
    nfft = 512
    win_length = int(nfft/2)
    hop_length = int(win_length/4)
    df = pd.DataFrame(columns=features)
    
    #If the previous run aborted, use this to reload and continue
    if preload:
        df = pd.read_csv('temp.csv')
        df = df.iloc[:,1:]
        
    t = time.time()
    for index, call in calls.iloc[len(df):].iterrows():
        print(index)
        s = np.load(call['wav_file'])
 
        # Compute all features
        pitch, voiced_perc = compute_f0(s, samplerate, nfft, hop_length)
        zero_crossings = compute_zero_crossing(s)
        duration =len(s)/samplerate  
        ent_var, mean_ent, max_ent,  ent = wiener_entropy(s, n_fft=nfft) 
        bandwidth = compute_bandwidth(s, samplerate, nfft, hop_length, win_length)
        n_peaks = harmonic_peaks(s, samplerate, nfft, hop_length, win_length)
             
        entry = pd.DataFrame.from_dict({
            "pitch": [pitch],
            "zero_crossings": [zero_crossings],
            "duration": [duration],
            "entropy_variance": [ent_var] ,
            "mean_entropy": [mean_ent],
            "maximum_entropy": [max_ent],
            "voiced_perc": [voiced_perc],
            "bandwidth": [bandwidth],
            "n_peaks":[n_peaks]
            })

        df = pd.concat([df, entry], ignore_index=True)
        
        # Show progress and save out intermediate
        if index%1000 == 0:
            print('time expired:')
            print(time.time() - t)
            df.to_csv('temp.csv')

    calls = pd.concat([calls, df], ignore_index=False, axis=1)
    
    return calls