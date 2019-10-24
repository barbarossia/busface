import random
from busface.model import classifier as clf
from busface.spider.db import Item, get_items, ItemRate


def test_train_model():
    clf.train()

def test_recommend():
    total, count = clf.recommend()
    print('total:', total)
    print('recommended:', count)