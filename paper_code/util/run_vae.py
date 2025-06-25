# -*- coding: utf-8 -*-
"""
@author: Dori M. Grijseels
"""

from torch.utils.data import DataLoader, random_split
from vae.models.dataset import SyllableDataset, ToTensor
from vae.models.vae import VAE
import pandas as pd
import os 


## Load metadata
data_folder = r'metadata'
all_calls = pd.read_csv(os.path.join(data_folder, 'features_dataset.csv'))

# Create the dataset
dataset = SyllableDataset(all_calls, 'spec_file', transform=ToTensor())

# Create dataloaders for train and test sets
dataloader = DataLoader(dataset, shuffle=True)

# Run VAE
hyperparams = {
		"z_dim": 32,
		"num_data": None, # None for all data 
		"epochs": 100,
        "train_size": 0.8
		}


database_dir = r"../metadata/call_dataset.csv"
save_dir = r"../models"

train_size = int(hyperparams['train_size'] * len(dataset))
test_size = len(dataset) - train_size
# Split the dataset
train_dataset, test_dataset = random_split(dataset, [train_size, test_size])
# Create dataloaders for train and test sets
train_dataloader = DataLoader(train_dataset, batch_size=4, shuffle=True)
test_dataloader = DataLoader(test_dataset, batch_size=4, shuffle=True)

# Create the model
model = VAE(z_dim=hyperparams["z_dim"], save_dir=save_dir, model_name="vae")

# Train the model
model.train_loop(train_dataloader, test_dataloader, epochs=101, save_freq=1)

## Extract latent features
model_checkpoint = os.path.join(save_dir, 'vae_checkpoint_99.pt')
model.load_state(model_checkpoint)
dataloader = DataLoader(dataset, batch_size=4, shuffle=False)
latent_means = model.get_latent(dataloader)

n_latent_means = 32
for i in range(n_latent_means):
	all_calls[f'latent_mean_{i}'] = latent_means[:, i]

all_calls.to_csv(os.path.join(data_folder, 'vae_features_dataset.csv'))
