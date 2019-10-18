from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
from busface.model.classify import Classify
import cv2
import traceback
import numpy as np
import pandas as pd

def process_data(df):
    '''
    do all processing , like onehotencode tag string
    '''
    X = df[['tags']]
    y = df[['target']]

    clf = Classify()
    clf.setTrainData(X.face.values)
    clf.setTypeData(y.target.values)
    try:
        clf.train()
        clf.saveModule()
    except Exception as e:
        print('system error')
        traceback.print_exc()
    return X, y


def prepare_data():
    items = load_data()
    dicts = as_dict(items)
    df = pd.DataFrame(dicts, columns=['id', 'face', 'target'])
    return df

def load_data():
    '''
    load data from database and do processing
    '''
    rate_type = RATE_TYPE.USER_RATE.value
    rate_value = None
    page = None
    items, _ = get_items(rate_type=rate_type, rate_value=rate_value,
                         page=page)
    return items


def as_dict(items):
    face_list = []

    for item in items:
        for face in item.faces_dict:
            if face.value is not None:
                d = {
                    'id': item.fanhao,
                    'face': convert_image(face.value),
                    'target': item.rate_value
                }

                face_list.append(d)

    return face_list


def convert_image(value):
    image = np.asarray(bytearray(value), dtype="uint8")
    image = cv2.imdecode(image, cv2.COLOR_BGR2GRAY)
    # grayFace = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image