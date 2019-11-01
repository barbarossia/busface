import numpy as np
from sklearn import svm
from sklearn import manifold
from sklearn.externals import joblib
# from sklearn.svm import SVC
from sklearn import tree
from sklearn import neighbors
from sklearn.decomposition import PCA

class Classify:

	X = []	# 训练数据集
	y = []	# 类型数据集
	clsf = None
	tsne = None

	def  __init__(self):
		# self.clsf = svm.SVC(gamma='scale')
		self.clsf = tree.DecisionTreeClassifier()
		# self.clsf = neighbors.KNeighborsClassifier(30, weights='distance')
		self.tsne = manifold.TSNE(n_components=3, init='pca', random_state=0)

	def setTrainData(self,trainData):
		self.X = trainData

	def setTypeData(self,typeData):
		self.y = typeData

	# 降维处理
	def dimentionTransform(self,faceData,isTrain=False):
		# newX = self.tsne.fit_transform(faceData)
		pca = PCA(n_components=16, svd_solver='randomized',whiten=True).fit(faceData)
		newX = pca.transform(faceData)
		# newX = self.tsne.fit_transform(newX)
		return newX

	def train(self):
		if len(self.y)<2:
			print("样本少于 2 个，请继续选择")
			return
		print("开始训练")

		# 降维
		newX = self.dimentionTransform(self.X,True)
		self.clsf.fit(newX,self.y)

		print("训练完成")

	def chkType(self,faceData):
		clsf = joblib.load('./train.mdl')
		arr = clsf.predict(faceData)
		score = clsf.predict_proba(faceData)
		# score = None
		# print(score)
		return arr,score

	def saveModule(self):
		print("开始保存模型")
		joblib.dump(self.clsf,'./train.mdl')
		print("保存结束")