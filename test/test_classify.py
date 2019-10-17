from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
from busface.model.classify import Classify
import cv2
import traceback
import numpy as np
import pandas as pd

def test_train():
    rate_type = RATE_TYPE.USER_RATE
    rate_value = None
    page = None
    items, _ = get_items(
        rate_type=rate_type, rate_value=rate_value, page=page)
    assert len(items) > 0

    dicts = as_dict(items)
    df = pd.DataFrame(dicts, columns=['id', 'face', 'target'])
    X = df[['face']]
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

def test_chkType_like():
    fanhao = 'IPX-358'
    item = Item.get_by_fanhao(fanhao)
    Item.get_faces_dict(item)

    faces = []
    for face in item.faces_dict:
        if face.value is not None:
            faces.append(convert_image(face.value))

    clf = Classify()
    try:
        arr = clf.chkType(faces)
        assert len(arr) > 0
    except Exception as e:
        print('system error')
        traceback.print_exc()

def test_chkType_dislike():
    fanhao = 'YSN-484'
    item = Item.get_by_fanhao(fanhao)
    Item.get_faces_dict(item)

    faces = []
    for face in item.faces_dict:
        if face.value is not None:
            faces.append(convert_image(face.value))

    clf = Classify()
    try:
        result = clf.chkType(faces)
        assert len(result) > 0
    except Exception as e:
        print('system error')
        traceback.print_exc()


def convert_image(value):
    image = np.asarray(bytearray(value), dtype="uint8")
    image = cv2.imdecode(image, cv2.COLOR_BGR2GRAY)
    # grayFace = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def as_dict(items):
    face_list = []

    for item in items:
        for face in item.faces_dict:
            if face.value is not None:
                d = {
                    'id': item.fanhao,
                    'face': convert_image(face.value),
                    #'face': face.value,
                    'target': item.rate_value
                }

                face_list.append(d)

    return face_list