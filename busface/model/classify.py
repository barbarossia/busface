import numpy as np
from sklearn import svm
from sklearn import manifold
from sklearn.externals import joblib
from busface.util import get_cwd
import os
from sklearn.decomposition import PCA
import numpy as np

class Classify:
    X = np.zeros(2, )
    y = np.zeros(5)
    clsf = None
    tsne = None
    path = "data\model"
    model_file = os.path.join(get_cwd(), path, "train.mdl")



    def __init__(self):
        self.clsf = svm.SVC(gamma='scale')
        self.tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)

    def setTrainData(self, trainData):
    #     for t in trainData:
    #         self.X.append(t)
        self.X = trainData

    def setTypeData(self, typeData):
        #for t in typeData:
        #    self.y.append(t)
        self.y = typeData

    # 降维处理
    def dimentionTransform(self, faceData, isTrain=False):
        newX = []
        faceCnt = 0
        n_components = 150
        pca = PCA(n_components=n_components, svd_solver='randomized',
                  whiten=True).fit(faceData)
        newX = pca.transform(faceData)
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
