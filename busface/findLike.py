import sqlite3
import cv2
import numpy as np
from classify_findLike import Classify

conn = sqlite3.connect('./testPic.db')
c = conn.cursor()

def transformFace(blobData):
	image = np.asarray(bytearray(blobData), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# scaledFace = cv2.resize(gray,(32,32))
	h, w = gray.shape[:2]
	vec = gray.reshape(w * h)
	return vec

sql_like = "select id,type,value from faces where type=1"
sql_dislike = "select id,type,value from faces where type=0"
sql_check = "select id,type,value from faces where type=2"

trainData = []
trainType = []

checkData = []
checkType = []
clf = Classify()
cnt = 0

print("Fetch Data")
print("--------------------")
def readytraninData(sql,type):
	global trainData,trainType
	resLst = c.execute(sql)
	tmpTrain = []
	tmpType = []
	for res in resLst:
		face = transformFace(res[2])
		tmpTrain.append(face)
		tmpType.append(type)
	checkData.extend(tmpTrain[0:100])
	trainData.extend(tmpTrain[100:])
	checkType.extend(tmpType[0:100])
	trainType.extend(tmpType[100:])
	return len(tmpTrain)

def readyChkData(sql):
	resLst = c.execute(sql)
	chk = []
	cnt = 0
	for res in resLst:
		face = transformFace(res[2])
		chk.append(face)
		cnt += 1
	return chk,cnt

#  --------  ready data
cnt_like = readytraninData(sql_like,1)
cnt_dislike = readytraninData(sql_dislike,0)

chk_pic,cnt_pic = readyChkData(sql_check)

#  --------  train like and dislike
clf.setTrainData(np.asarray(trainData))
clf.setTypeData(np.asarray(trainType))

clf.train()
clf.saveModule()

print("Check predict")

def checkPredict(chk_Data_,pred):
	res_true = 0
	res_false = 0

	chk_Data = np.asarray(chk_Data_)
	chk_data_pca = clf.dimentionTransform(chk_Data)
	res,score = clf.chkType(chk_data_pca)

	# 决策树时使用
	for s in score:
		if s[pred]<0.5:
			res_false += 1
		else:
			res_true += 1

	#  非决策树时使用
	# for s in res:
	# 	if s==pred:
	# 		res_false += 1
	# 	else:
	# 		res_true += 1

	return res_true,res_false

res_t1,res_f1 = checkPredict(checkData,1)
res_t0,res_f0 = checkPredict(checkData,0)
res_t21,res_f21 = checkPredict(chk_pic,1)
res_t20,res_f20 = checkPredict(chk_pic,0)

tp = res_t1 + res_t0
tn = res_f1 + res_f0
fp = res_f21 + res_f20
fn = res_t21 + res_t20

print("--------------------")
print("like",cnt_like)
print("dislike",cnt_dislike)
print("check",cnt_pic)
print("--------------------")
print("TP: " , tp)
print("TN: " , tn)
print("FP: " , fp)
print("FN: " , fn)
print("--------------------")
print("Accuracy: ",(tp+tn)/(tp+tn+fp+fn))