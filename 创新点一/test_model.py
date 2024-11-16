import torch
import torch.nn as nn
import torchvision.models as models

class HierarchicalMultiTaskFeatureExtract(nn.Module):
    def __init__(self, num_classes, num_models):
        super(HierarchicalMultiTaskFeatureExtract, self).__init__()
        # 使用VGG11的特征提取部分
        self.feature_extractor = models.vgg11(pretrained=True).features
        # 共享的全连接层
        self.shared_fc = nn.Linear(512 * 7 * 7, 4096)
        
        # 类别分类器
        self.class_classifier = nn.Linear(4096, num_classes)
        # 模型分类器
        self.model_classifier = nn.Linear(4096, num_models)

    def forward(self, x):
        # 提取特征
        features = self.feature_extractor(x).view(x.size(0), -1)
        shared_features = torch.relu(self.shared_fc(features))
        
        # 分类任务
        class_out = self.class_classifier(shared_features)
        model_out = self.model_classifier(shared_features)
        
        return class_out, model_out

# 损失函数：多任务损失，同时计算类别和模型的交叉熵损失
def hierarchical_loss(class_outputs, model_outputs, class_labels, model_labels, model_to_class_map):
    class_loss_fn = nn.CrossEntropyLoss()
    model_loss_fn = nn.CrossEntropyLoss()
    
    # 计算类别损失
    class_loss = class_loss_fn(class_outputs, class_labels)
    
    # 确保模型标签和类别标签的对应关系
    model_loss = 0
    for i, model_label in enumerate(model_labels):
        expected_class = model_to_class_map[model_label.item()]  # 获取模型对应的类别
        model_loss += model_loss_fn(model_outputs[i].unsqueeze(0), torch.tensor([expected_class]).cuda())
    
    return class_loss + model_loss

# 训练过程
def train_model(train_loader, model, optimizer, model_to_class_map, num_epochs):
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for data, model_labels, class_labels in train_loader:
            data, model_labels, class_labels = data.cuda(), model_labels.cuda(), class_labels.cuda()
            
            optimizer.zero_grad()
            # 得到类别标签和模型标签的输出
            class_outputs, model_outputs = model(data)
            
            # 计算损失
            loss = hierarchical_loss(class_outputs, model_outputs, class_labels, model_labels, model_to_class_map)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss/len(train_loader):.4f}")

# 模型初始化和优化器
model = HierarchicalMultiTaskFeatureExtract(num_classes=10, num_models=50).cuda()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# model_to_class_map: 模型标签到类别标签的映射（预定义）
model_to_class_map = {0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 2}  # 示例：模型 0 和 1 属于类别 0，模型 2 和 3 属于类别 1，依此类推

# 假设train_loader已经定义好了
train_model(train_loader, model, optimizer, model_to_class_map, num_epochs=10)
