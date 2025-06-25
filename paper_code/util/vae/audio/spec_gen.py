import numpy as np
from scipy.signal import stft
from scipy.interpolate import RegularGridInterpolator

EPSILON = 1e-12

def get_specs(waveforms, fs, p):
	min_freq = p['min_freq']
	max_freq = p['max_freq']
	num_freq_bins = p['num_freq_bins']
	n_perseg = p['nperseg']

	assert min_freq < max_freq
	assert n_perseg % 2 == 0 and n_perseg > 2
	if p['mel']:
		target_freqs = np.linspace(_mel(min_freq), _mel(max_freq), num_freq_bins)
		target_freqs = _inv_mel(target_freqs)
	else:
		target_freqs = np.linspace(min_freq, max_freq, num_freq_bins)

	specs = []
	for waveform in waveforms:
		waveform = waveform/np.max(np.abs(waveform))
		spec = generate_spec(waveform, p, fs, target_freqs=target_freqs)

		specs.append(spec)
	return specs


def generate_spec(audio, p, fs, target_freqs=None, target_times=None, fill_value=-1/EPSILON, remove_dc_offset=True):
	nperseg = p['nperseg']
	noverlap = p['noverlap']
	mel_flag = p['mel']
	min_freq = p['min_freq']
	max_freq = p['max_freq']
	num_freq_bins = p['num_freq_bins']
	num_time_bins = p['num_time_bins']
	spec_min_val = p['spec_min_val']
	spec_max_val = p['spec_max_val']
	time_stretch_flag = p['time_stretch']
	max_dur = p['max_dur']
	within_syll_normalize_flag = p['within_syll_normalize']
	normalize_quantile = p['normalize_quantile']
	
	if remove_dc_offset:
		audio = audio - np.mean(audio)
	f, t, spec = stft(audio, fs=fs, nperseg=nperseg, noverlap=noverlap)

	spec = np.log(np.abs(spec) + EPSILON)
	interp = RegularGridInterpolator((t, f), spec.T, bounds_error=False, fill_value=fill_value)
	# Define target frequencies.
	if target_freqs is None:
		if mel_flag:
			target_freqs = np.linspace(_mel(min_freq), _mel(max_freq), num_freq_bins)
			target_freqs = _inv_mel(target_freqs)
		else:
			target_freqs = np.linspace(min_freq, max_freq, num_freq_bins)
	
	# Define target times.
	if target_times is None:
		duration = len(audio) / fs
		if time_stretch_flag:
			duration = np.sqrt(duration * max_dur)  # stretched duration
		shoulder = 0.5 * (max_dur - duration)
		centered_start = -shoulder
		centered_end = duration + shoulder
		target_times = np.linspace(centered_start, centered_end, num_time_bins)
	
	# Then interpolate.
	target_points = np.array(np.meshgrid(target_times, target_freqs)).T.reshape(-1, 2)
	interp_spec = interp(target_points).reshape(len(target_times), len(target_freqs)).T

	spec_min_val = np.min(interp_spec[interp_spec>-1000]) - EPSILON # make sure to not include fill value in minimum
	spec_max_val = np.max(interp_spec) + EPSILON - spec_min_val
	spec = interp_spec

	# Normalize

	spec -= spec_min_val
	spec /= (spec_max_val)
	spec = np.clip(spec, 0.0, 1.0)

	if within_syll_normalize_flag:
		spec -= np.quantile(spec, normalize_quantile)
		spec[spec<0.0] = 0.0
		spec /= np.max(spec) + EPSILON

	# flip the spectrogram along y-axis
	spec = np.flipud(spec)

	return spec


def _mel(a):
	"""https://en.wikipedia.org/wiki/Mel-frequency_cepstrum"""
	return 1127 * np.log(1 + a / 700)


def _inv_mel(a):
	"""https://en.wikipedia.org/wiki/Mel-frequency_cepstrum"""
	return 700 * (np.exp(a / 1127) - 1)