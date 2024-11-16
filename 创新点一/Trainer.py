import numpy as np
import torch
import os
from torch.autograd import Variable

class ModelTrainer():
    def __init__(self, stage, model, train_loader, test_loader, optimizer, loss_fn, view_num=12):
        self.stage = stage
        self.model = model
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.optimizer = optimizer
        self.loss_fn = loss_fn

        self.file_size = len(self.train_loader.dataset.img_paths)
        self.view_num = view_num

        self.model.cuda()
    
    def train(self, n_epochs, save_path):
        best_acc = 0.0
        out_path = os.path.join(save_path, "log.txt")
        for epoch in range(n_epochs):
            # 模型训练阶段
            self.model.train()
            # 训练前打乱数据顺序(以视图为基本单元)
            rand_arr = np.random.permutation(int(self.file_size / self.view_num))
            new_img_paths = []
            for idx in range(len(rand_arr)):
                new_img_paths.append(self.train_loader.dataset.img_paths[rand_arr[idx]*self.view_num:(rand_arr[idx]+1)*self.view_num])
            self.train_loader.dataset.filepaths = new_img_paths
            # 单次训练
            train_correct_samples = 0
            train_total_samples = 0
            for idx, _, data in self.train_loader:
                if self.stage == 1: # 第一阶段
                    data = data.cuda()
                else:               # 第二阶段
                    N, V, C, H, W = data.size()
                    data = Variable(data).view(-1, C, H, W).cuda()
                target = Variable(idx).cuda().long()
                self.optimizer.zero_grad()  # 旧梯度清空
                out_put = self.model(data)  # 前向传播
                loss = self.loss_fn(out_put, target)    # 损失计算

                pred = torch.max(out_put, 1)[1]
                results = pred == target    # 生成布尔张量
                train_correct_samples += results.sum()
                train_total_samples += results.size()[0]

                loss.backward() # 反向传播
                self.optimizer.step()   # 更新模型
            
            train_acc = train_correct_samples.float() / train_total_samples  # 当前eopch训练准确率
            
            # 模型评估阶段
            self.model.eval()
            test_correct_samples = 0
            test_total_samples = 0
            for idx, _, data in self.train_loader:
                if self.stage == 1: # 第一阶段
                    data = data.cuda()
                else:               # 第二阶段
                    N, V, C, H, W = data.size()
                    data = Variable(data).view(-1, C, H, W).cuda()
                target = Variable(idx).cuda().long()
                out_put = self.model(data)
                pred = torch.max(out_put, 1)[1]
                results = pred == target
                batch_correct_samples = results.sum()
                batch_total_samples = results.size()[0]

                test_correct_samples += batch_correct_samples
                test_total_samples += batch_total_samples

            test_acc = test_correct_samples.float() / test_total_samples # 当前eopch测试准确率

            content = "stage %d, epoch %d: train_loss %.3f, train_acc %.3f, test_acc %.3f" % (self.stage, epoch+1, loss, train_acc, test_acc)
            log_to_file(out_path, content)
            
            # 保存最优训练结果
            if test_acc > best_acc:
                best_acc = test_acc
                self.model.save(save_path)
            
            # 调整学习率
            if (epoch + 1) % 10 == 0:
                for param_group in self.optimizer.param_groups:
                    param_group["lr"] = param_group["lr"] * 0.5
        
        # 打印最终结果
        content = "模型准确率为 %.3f" % (best_acc)
        log_to_file(out_path, content)


def log_to_file( out_file, content):
    with open(out_file, "a") as f:
        f.write(content + "\n")