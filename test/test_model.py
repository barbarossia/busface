import random
from busface.model import classifier as clf
from busface.spider.db import Item, get_items, ItemRate, RATE_TYPE
from busface.model.prepare import as_dict, create_data, MIN_TRAIN_NUM, dimension
from busface.model.classifier import predict, create_group, RATIO


def test_train_model():
    clf.train()

def test_recommend():
    total, count = clf.recommend()
    print('total:', total)
    print('recommended:', count)

def test_classify():
    ids, X = prepare_predict_data()
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

def prepare_predict_data():
    # get not rated data
    fanhao_list = ['GS-289', 'IENF-035', 'HBAD-502', 'PIYO-047']

    unrated_items = []
    for item_id in fanhao_list:
        item = Item.get_by_fanhao(item_id)
        if item is not None:
            Item.get_faces_dict(item)
            item_rate = ItemRate.get_by_fanhao(item_id)
            item.rate_value = item_rate.rate_value
            unrated_items.append(item)

    dicts = as_dict(unrated_items)
    lfw = create_data(dicts)
    n_samples = lfw.data.shape[0]
    if n_samples < MIN_TRAIN_NUM:
        raise ValueError(f'训练数据不足, 无法训练模型. 需要{MIN_TRAIN_NUM}, 当前{n_samples}')
    return lfw.ids, dimension(lfw.data)