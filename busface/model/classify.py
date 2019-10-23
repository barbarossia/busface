import numpy as np
from sklearn import svm
from sklearn import manifold
from sklearn.metrics import f1_score, recall_score, accuracy_score, precision_score, confusion_matrix
from busface.util import logger, get_data_path, MODEL_PATH, APP_CONFIG
import os
from sklearn.decomposition import PCA
import numpy as np

MODEL_FILE = MODEL_PATH + 'train.mdl'
MIN_TRAIN_NUM = int(APP_CONFIG['sample.n_components'])

def create_model():
    knn = KNeighborsClassifier(n_neighbors=11)
    return knn

def train():
    model = create_model()
    X_train, X_test, y_train, y_test = prepare_data()
    total = len(X_test) + len(X_train)
    if total < MIN_TRAIN_NUM:
        raise ValueError(f'训练数据不足, 无法训练模型. 需要{MIN_TRAIN_NUM}, 当前{total}')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    confusion_mtx = confusion_matrix(y_test, y_pred)
    scores = evaluate(confusion_mtx, y_test, y_pred)
    models_data = (model, scores)
    dump_model(get_data_path(MODEL_FILE), models_data)
    logger.info('new model trained')
    return models_data


def evaluate(confusion_mtx, y_test, y_pred):
    tn, fp, fn, tp = confusion_mtx.ravel()
    # accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    logger.info(f'tp: {tp}, fp: {fp}')
    logger.info(f'fn: {fn}, tn: {tn}')
    # logger.info(f'accuracy_score: {accuracy}')
    logger.info(f'precision_score: {precision}')
    logger.info(f'recall_score: {recall}')
    logger.info(f'f1_score: {f1}')
    model_scores = dict(precision=precision, recall=recall, f1=f1)
    model_scores = {key: float('{:.2f}'.format(value))
                    for key, value in model_scores.items()}
    return model_scores
