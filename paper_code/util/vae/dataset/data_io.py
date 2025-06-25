from pathlib import Path
import numpy as np
import soundfile as sf


def get_audio_seg_filenames(audio_dir, segment_dir, audio_type='.wav', segment_type='.txt'):
	
	# get all files of the specified type in the directories
	annotation_files = list(Path(segment_dir).rglob(f'*{segment_type}'))
	audio_files = list(Path(audio_dir).rglob(f'*{audio_type}'))
	
	# get the file names without the extension
	annotation_files_temp = [Path(file).stem for file in annotation_files]
	audio_files_temp = [Path(file).stem for file in audio_files]

	# get the matched files
	matched_files = list(set(annotation_files_temp).intersection(audio_files_temp))

	# get the file paths
	seg_filenames = [file for file in annotation_files if Path(file).stem in matched_files]
	audio_filenames = [file for file in audio_files if Path(file).stem in matched_files]

	# sort the lists
	audio_filenames = sorted(audio_filenames)
	seg_filenames = sorted(seg_filenames)
	
    # print a warning if there are unmatched files
	if len(annotation_files_temp) != len(audio_files_temp):
		print(f"Warning: {len(audio_files_temp)} audio files and {len(annotation_files_temp)} segment files found in directory {audio_dir.parent}")
		# print the unmatched files
		unmatched_audio_files = [file for file in audio_files if Path(file).stem not in matched_files]
		unmatched_seg_files = [file for file in annotation_files if Path(file).stem not in matched_files]
		if unmatched_audio_files:
			print("Unmatched audio files:")
			for file in unmatched_audio_files: print(file)
		if unmatched_seg_files:
			print("Unmatched segment files:")
			for file in unmatched_seg_files: print(file)
		print()
	return audio_filenames, seg_filenames


def read_onsets_offsets_from_file(txt_filename):
	"""
	Read a text file to collect onsets and offsets.

	Note
	----
	* The text file must have two coulumns separated by whitespace and ``#``
	  prepended to header and footer lines.
	"""
	segs = np.loadtxt(txt_filename)
	assert segs.size % 2 == 0, f"Incorrect formatting: {txt_filename} " 
	segs = segs.reshape(-1,2)
	return segs[:,0], segs[:,1]


def check_audio_seg_files(audio_filename, seg_filename):
	# check that filenames match
	if not (audio_filename.stem == seg_filename.stem):
		print(f" Filenames {audio_filename} and {seg_filename} do not match")

	# load the audio file
	with sf.SoundFile(audio_filename, 'r') as track:
		audio_duration = len(track) / track.samplerate
		# round to 5 decimal places
		audio_duration = round(audio_duration, 5)
	
	# load the segments
	onsets, offsets = read_onsets_offsets_from_file(seg_filename)
	
	# check if the segments are within the audio file
	if not np.all(onsets > 0):
		print(f"Negative onset found in {seg_filename}")
		# print the offending segments
		offending_segments = np.where(onsets < 0)[0]
		for idx in offending_segments:
			print(f"Segment {idx}: onset={onsets[idx]}, offset={offsets[idx]}")
	if not np.all(offsets <= audio_duration):
		print(f"Offset beyond audio duration found in {seg_filename}")
		# print the offending segments
		offending_segments = np.where(offsets > audio_duration)[0]
		for idx in offending_segments:
			print(f"Segment {idx}: onset={onsets[idx]}, offset={offsets[idx]}, audio_file_duration={audio_duration}")