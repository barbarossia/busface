from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
from busface.model.classify import Classify
import cv2
import traceback
import numpy as np
import pandas as pd
import re
from busface.util import logger

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


def get_faces(items):
    faces = []
    rows = items.splitlines()
    fanhao_list = []
    pattern = r'([A-Z]+)-?([0-9]+)'
    for row in rows:
        if ',' in row:
            fanhao, _ = row.split(',')
        else:
            fanhao = row
        fanhao = fanhao.strip().upper()
        match = re.search(pattern, fanhao)
        if match and len(match.groups()) == 2:
            series, num = match.groups()
            matched_fanhao = f'{series}-{num}'
            fanhao_list.append((matched_fanhao))


    for item_id in fanhao_list:
        item = Item.get_by_fanhao(item_id)
        if item is not None:
            Item.get_faces_dict(item)
            for face in item.faces_dict:
                if face.value is not None:
                    faces.append(convert_image(face.value))
    return faces

def test_chkType_like():
    with open('./Hashimoto.txt', 'r') as file:
        fanhao_list = file.read()
    faces = get_faces(fanhao_list)

    clf = Classify()
    try:
        result = clf.chkType(faces)
        expect = [1] * len(faces)

        logger.debug(' ,'.join(map(str, expect)))
        logger.debug(' ,'.join(map(str, result)))

        compare = [i for i, j in zip(expect, result) if i == j]
        logger.debug(' ,'.join(map(str, compare)))
    except Exception as e:
        print('system error')
        traceback.print_exc()

def test_chkType_dislike():
    fanhao = 'SORA-236'
    item = Item.get_by_fanhao(fanhao)
    Item.get_faces_dict(item)

    faces = []
    for face in item.faces_dict:
        if face.value is not None:
            faces.append(convert_image(face.value))

    clf = Classify()
    try:
        result = clf.chkType(faces)
        assert result[0] == 0
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