import warnings
import numpy as np
import soundfile as sf

def get_waveforms(audio_filename, start_times, end_times, max_dur=None):

	with sf.SoundFile(audio_filename, 'r+') as track:
		assert len(start_times) == len(end_times), "start_times and end_times must have the same length"
		assert np.all(np.array(end_times) > np.array(start_times)), "end_times must be greater than start_times"
		assert track.seekable(), "track must be seekable"

		# extract waveforms
		waveforms = []
		sr = track.samplerate
		for s, e in zip(start_times, end_times):
			duration = e - s
			start_frame = int(s * sr)
			frames_to_read = int(duration * sr)

			if duration < 0:
				raise ValueError(f"End time {e} is before start time {s}")
			if start_frame + frames_to_read > track.frames:
				raise ValueError(f"file {audio_filename} is too short to read segment {s}-{e}")
			if max_dur is not None and duration > max_dur + 1e-4:
				warnings.warn(f"Found segment longer than max_dur: {str(duration)}s, max_dur={max_dur}s")

			track.seek(start_frame)
			waveform = track.read(frames_to_read)

			# if multiple channels, average them
			if len(waveform.shape) > 1:
				waveform = waveform.mean(axis=1)

			waveforms.append(waveform)

	return waveforms, sr