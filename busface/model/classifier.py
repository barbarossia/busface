from sklearn.metrics import f1_score, recall_score, accuracy_score, precision_score, confusion_matrix
from busface.util import logger, get_data_path, MODEL_PATH, APP_CONFIG
from busface.model.prepare import prepare_data, prepare_predict_data
from sklearn import tree
from busface.model.persist import load_model, dump_model
from sklearn.decomposition import PCA
from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
import pandas as pd
from sklearn.svm import SVC

MODEL_FILE = MODEL_PATH + 'train.mdl'
MIN_TRAIN_NUM = int(APP_CONFIG['sample.n_components'])
RATIO = float(APP_CONFIG['recommend.ratio'])

def load():
    model_data = load_model(get_data_path(MODEL_FILE))
    return model_data


def create_model():
    clf = SVC(C=10, cache_size=200, class_weight=None, coef0=0.0,
        decision_function_shape='ovr', degree=3, gamma=0.005, kernel='rbf',
        max_iter=-1, probability=False, random_state=None, shrinking=True,
        tol=0.001, verbose=False)
    return clf


def dimension(X_train, X_test):
    pca = PCA(n_components=MIN_TRAIN_NUM, svd_solver='randomized',
              whiten=True).fit(X_train)
    X_train_pca = pca.transform(X_train)
    X_test_pca = pca.transform(X_test)
    return X_train_pca, X_test_pca


def predict(X_test):
    model, _ = load()
    y_pred = model.predict(X_test)
    return y_pred


def train():
    model = create_model()
    X_train, X_test, y_train, y_test = prepare_data()
    total = len(X_test) + len(X_train)
    if total < MIN_TRAIN_NUM:
        raise ValueError(f'训练数据不足, 无法训练模型. 需要{MIN_TRAIN_NUM}, 当前{total}')
    X_train_pca, X_test_pca = dimension(X_train, X_test)
    model.fit(X_train_pca, y_train)
    y_pred = model.predict(X_test_pca)
    confusion_mtx = confusion_matrix(y_test, y_pred)
    scores = evaluate(confusion_mtx, y_test, y_pred)
    models_data = (model, scores)
    dump_model(get_data_path(MODEL_FILE), models_data)
    logger.info('new model trained')
    return models_data


def evaluate(confusion_mtx, y_test, y_pred):
    tn, fp, fn, tp = confusion_mtx.ravel()
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    logger.info(f'tp: {tp}, fp: {fp}')
    logger.info(f'fn: {fn}, tn: {tn}')
    logger.info(f'accuracy_score: {accuracy}')
    logger.info(f'precision_score: {precision}')
    logger.info(f'recall_score: {recall}')
    logger.info(f'f1_score: {f1}')
    model_scores = dict(accuracy = accuracy, precision=precision, recall=recall, f1=f1)
    model_scores = {key: float('{:.2f}'.format(value))
                    for key, value in model_scores.items()}
    return model_scores

def recommend():
    '''
    use trained model to recommend items
    '''
    ids, X = prepare_predict_data()
    if len(X) == 0:
        logger.warning(
            f'no data for recommend')
        return
    count = 0
    total = len(ids)
    y_pred = predict(X)
    df = create_group(ids, y_pred)
    ids = df['id'].values
    y_mean = df['value'].values
    for id, y in zip(ids, y_mean):
        if y > RATIO:
            count += 1
            value = 1
        else:
            value = 0
        rate_type = RATE_TYPE.SYSTEM_RATE
        rate_value = value
        item_id = id
        item_rate = ItemRate(rate_type=rate_type,
                             rate_value=rate_value, item_id=item_id)
        item_rate.save()
    logger.warning(
        f'predicted {total} items, recommended {count}')
    return total, count

def create_group(ids, y):
    data = {'id': ids, 'value': y}
    df = pd.DataFrame(data, columns=['id', 'value'])
    df = df.groupby(['id']).mean().reset_index()
    return df