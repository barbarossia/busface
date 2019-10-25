import random
from busface.model import classifier as clf
from busface.spider.db import Item, get_items, ItemRate
from busface.model.prepare import as_dict


def test_train_model():
    clf.train()

def test_recommend():
    total, count = clf.recommend()
    print('total:', total)
    print('recommended:', count)

def test_parapare():
    fanhao_list= ['KBI-020', 'HND-746']

    items = []
    for item_id in fanhao_list:
        item = Item.get_by_fanhao(item_id)
        if item is not None:
            item_rate = ItemRate.get_by_fanhao(item.fanhao)
            item.rate_value = item_rate.rate_value
            Item.get_faces_dict(item)
            items.append(item)

    dicts = as_dict(items)
    dicts