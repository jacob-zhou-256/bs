import os
import glob
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image


class SingleViewDataset(Dataset):
    def __init__(self, root_dir, type):
        self.root_dir = root_dir
        self.type = type
        self.classnames = []
        for item in os.listdir(root_dir):
            self.classnames.append(item)
        
        self.img_paths = []
        for item in self.classnames:
            all_files = sorted(glob.glob(os.path.join(root_dir, item, type, "*.png")))
            self.img_paths.extend(all_files)

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def __len__(self):
        return len(self.img_paths)

    def __getitem__(self, idx):
        img_path = self.img_paths[idx]
        label = img_path.split('/')[-3]
        class_id = self.classnames.index(label)

        image = Image.open(img_path).convert("RGB")
        image = self.transform(image)
        return class_id, label, image