# Naked mole-rat vocal ontogeny

# Preprocessing
- Make sure all files are named in the following way: '[colony]\_[recording\_date]\_[animal\_id]\_[file_number]
- Wav files and corresponding text files should have the same name
- Run util/extract_spectrograms to extract individual wav files and spectrograms for each call, and obtain a csv file with animal colony, id, and age for each call

# VAE
- From: Jack Goffinet, Samuel Brudner, Richard Mooney, John Pearson (2021) Low-dimensional learned feature spaces quantify individual and group differences in vocal repertoires eLife 10:e67855
- Original code: https://github.com/pearsonlab/autoencoded-vocal-analysis
- Run run_vae from util folder to train and extract latent means

# Soft chirp analysis
- Extract the adult calls using util/extract_spectrograms_adult.py
- This will extract spectrograms, do the feature extraction, and extract latent means using the pre-trained VAE