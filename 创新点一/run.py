import os
import torch
import torch.optim as optim
import torch.nn as nn
from Model import SingleViewFeatureExtract, MultiViewFeatureFuse
from ImgDataset import SingleViewDataset, MultiViewDataset
from Trainer import ModelTrainer

def main():
    dataset_path = "/root/autodl-tmp/modelnet40_images_new_12x"
    model_save_path = "/root/autodl-tmp"
    learning_rate = 5e-5
    weight_decay = 0.001
    num_epochs = 30
    num_classes = len(os.listdir(dataset_path))
    """第一阶段 单视图特征提取"""
    cnet = SingleViewFeatureExtract(num_classes)
    optimizer = optim.Adam(cnet.parameters(), lr=learning_rate, weight_decay=weight_decay)

    train_dataset = SingleViewDataset(dataset_path, "train")
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=8, shuffle=True, num_workers=0)

    test_dataset = SingleViewDataset(dataset_path, "test")
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=8, shuffle=False, num_workers=0)

    trainer = ModelTrainer(1, cnet, train_loader, test_loader, optimizer, nn.CrossEntropyLoss())
    trainer.train(num_epochs, model_save_path)

    """第二阶段 多视图特征融合"""
    cnet2 = MultiViewFeatureFuse(cnet, num_classes)
    optimizer = optim.Adam(cnet2.parameters(), lr=learning_rate, weight_decay=weight_decay, betas=(0.9, 0.999))

    train_dataset = MultiViewDataset(dataset_path, "train")
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=8, shuffle=False, num_workers=0)

    test_dataset = MultiViewDataset(dataset_path, "test")
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=8, shuffle=False, num_workers=0)

    trainer = ModelTrainer(2, cnet2, train_loader, test_loader, optimizer, nn.CrossEntropyLoss())
    trainer.train(num_classes, model_save_path)

if __name__ == "__main__":
    main()