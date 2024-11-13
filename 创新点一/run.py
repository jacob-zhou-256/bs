import os
import torch
import torch.optim as optim
import torch.nn as nn
from Model import SingleViewFeatureExtract
from ImgDataset import SingleViewDataset
from Trainer import ModelTrainer

def main():
    dataset_path = "/root/autodl-tmp/modelnet40_images_new_12x"
    model_save_path = "/root/autodl-tmp"
    learning_rate = 5e-5
    weight_decay = 0.001
    num_epochs = 30
    num_classes = len(os.listdir(dataset_path))

    cnet = SingleViewFeatureExtract(num_classes)
    optimizer = optim.Adam(cnet.parameters(), lr=learning_rate, weight_decay=weight_decay)

    train_dataset = SingleViewDataset(dataset_path, "train")
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=8, shuffle=True, num_workers=0)

    test_dataset = SingleViewDataset(dataset_path, "test")
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=8, shuffle=False, num_workers=0)

    trainer = ModelTrainer(cnet, train_loader, test_loader, optimizer, nn.CrossEntropyLoss())
    trainer.train(num_epochs, model_save_path)

if __name__ == "__main__":
    main()