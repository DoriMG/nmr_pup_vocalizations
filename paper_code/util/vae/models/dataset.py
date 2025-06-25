import torch
import numpy as np
from torch.utils.data import Dataset

class SyllableDataset(Dataset):
    def __init__(self, metadata, file_col, transform=None):
        self.metadata = metadata
        self.transform = transform
        self.file_col = file_col

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        spec = np.load(self.metadata.iloc[idx][self.file_col])
        spec = spec.astype(np.float32)
        if self.transform:
            spec = self.transform(spec)

        return spec
    
class ToTensor(object):
    def __call__(self, spec):
        return torch.from_numpy(spec).unsqueeze(0)