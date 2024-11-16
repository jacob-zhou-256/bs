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

    def forward(self, input):
        y = self.net_1(input)
        return self.net_2(y.view(y.shape[0], -1))
    
    def save(self, path, epoch):
        torch.save(self.state_dict(), os.path.join(path, f"1-{epoch}-model.pth"))


class MultiViewFeatureFuse(nn.Module):
    def __init__(self, model, num_classes):
        super(MultiViewFeatureFuse, self).__init__()
        self.num_classes = num_classes
        self.view_num = 12
        self.net_1 = model.net_1
        self.net_2 = model.net_2
    
    def forward(self, input):
        x = self.net_1(input)
        y = x.view((input.shape[0]/self.view_num, self.view_num, x.shape[-3], x.shape[-2], x.shape[-1]))
        return self.net_2(torch.max(y, 1)[0].view(y.shape[0], -1))

    def save(self, path, epoch):
        torch.save(self.state_dict(), os.path.join(path, f"2-{epoch}-model.pth"))