import torch
import os
import torch.nn as nn
import torchvision.models as models


class SingleViewFeatureExtract(nn.Module):
    def __init__(self, num_classes):
        super(SingleViewFeatureExtract, self).__init__()
        self.net_1 = models.vgg11(pretrained=True).features
        self.net_2 = models.vgg11(pretrained=True).classifier
        self.net_2._modules["6"] = nn.Linear(4096, num_classes)

    def forward(self, x):
        y = self.net_1(x)
        return self.net_2(y.view(y.shape[0], -1))
    
    def save(self, path, epoch):
        torch.save(self.state_dict(), os.path.join(path, f"{epoch}-model.pth"))
