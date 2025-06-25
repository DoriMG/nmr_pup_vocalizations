import numpy as np
import pandas as pd

def copy_segments_to_standard_format(orig_seg_dirs, new_seg_dirs, \
	seg_ext, delimiter, usecols, skiprows, \
	max_duration=None, min_duration=None, call_selection=[]):

	assert seg_ext in ['.txt', '.csv'], "Expected seg_ext to be '.txt' or '.csv'!"
	assert len(orig_seg_dirs) == len(new_seg_dirs), f"{len(orig_seg_dirs)} != {len(new_seg_dirs)}"
	assert len(usecols) == 2, "Expected two columns (for onsets and offsets)!"

	for orig_seg_dir, new_seg_dir in zip(orig_seg_dirs, new_seg_dirs):
		# create new_seg_dir if it does not exist
		if not new_seg_dir.exists():
			new_seg_dir.mkdir(parents=True)
		
		# copy segments to standard format
		for seg_fn in orig_seg_dir.glob(f"*{seg_ext}"):
			pd_df = pd.read_csv(seg_fn, sep=delimiter, skiprows=skiprows, header=None)
			# select only the calls in call_selection
			if len(pd_df.columns) == 3: # if there is a 3rd column, it is the call type
				if call_selection:
					segs = pd_df[pd_df.iloc[:,2].isin(call_selection)].loc[:,usecols].values
				else:
					segs = pd_df.loc[:,usecols].values
			else:
				segs = pd_df.loc[:,usecols].values
			
			# Filter segments for duration
			segs = filter_segments(segs, max_duration, min_duration)
			
			new_seg_fn = new_seg_dir / seg_fn.name
			header = "Onsets/offsets copied from " + seg_fn.__str__()
			np.savetxt(new_seg_fn, segs, fmt='%.5f', header=header)
			
def filter_segments(segs, max_duration=None, min_duration=None):
    if max_duration is not None:
        segs = np.array([seg for seg in segs if seg[1] - seg[0] < max_duration])
    
    if min_duration is not None:
        segs = np.array([seg for seg in segs if seg[1] - seg[0] > min_duration])
    
    return segs

