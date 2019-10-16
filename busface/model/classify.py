import numpy as np
from sklearn import svm
from sklearn import manifold
from sklearn.externals import joblib
from busface.util import get_cwd
import os

class Classify:
    X = []  # 训练数据集
    y = []  # 类型数据集
    clsf = None
    tsne = None
    path = "data\model"
    model_file = os.path.join(get_cwd(), path, "train.mdl")

    def __init__(self):
        self.clsf = svm.SVC(gamma='scale')
        self.tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)

    def setTrainData(self, trainData):
        for t in trainData:
            self.X.append(t)

    def setTypeData(self, typeData):
        for t in typeData:
            self.y.append(t)

    # 降维处理
    def dimentionTransform(self, faceData):
        newX = []
        for x in faceData:
            dim2X = self.tsne.fit_transform(x)
            sum0 = 0
            sum1 = 0
            for nx in dim2X:
                sum0 += nx[0]
                sum1 += nx[1]
            newX.append([sum0 / len(dim2X), sum1 / len(dim2X)])
        return newX

    def train(self):
        if len(self.y) < 2:
            print("样本少于 2 个，请继续选择")
            return
        print("开始训练")

        # 先将 32*32 图形矩阵降维至 2*32，然后计算两列的平均值之后再分类
        newX = self.dimentionTransform(self.X)
        self.clsf.fit(newX, self.y)

    def chkType(self, faceData):
        clsf = joblib.load(self.model_file)
        newFaces = self.dimentionTransform(faceData)
        arr = clsf.predict(newFaces)
        return arr

    def saveModule(self):
        print("开始保存模型")
        joblib.dump(self.clsf, self.model_file)
        print("保存结束")