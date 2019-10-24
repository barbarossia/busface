from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
from busface.model.classifier import Classify
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
    try:
        #faces = np.asarray(X.face.values)
        faces = test_read_image_convert_array()
        clf = Classify()
        clf.setTrainData(faces)
        clf.setTypeData(y.target.values)

        clf.train()
        clf.saveModule()
    except Exception as e:
        print('system error')
        traceback.print_exc()

def test_train_fanhao():
    with open('./YuaMikami.txt', 'r') as file:
        fanhao_list = file.read()
    faces = get_faces(fanhao_list)
    try:
        X = np.asarray(faces)
        expect = [1] * len(faces)
        expect[0] = 0
        y = np.asarray(expect)
        clf = Classify()
        clf.setTrainData(X)
        clf.setTypeData(y)

        clf.train()
        clf.saveModule()
    except Exception as e:
        print('system error')
        traceback.print_exc()


def get_fanhao(items):
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
    return fanhao_list;


def get_faces(items):
    faces = []
    fanhao_list = get_fanhao(items)

    for item_id in fanhao_list:
        item = Item.get_by_fanhao(item_id)
        if item is not None:
            Item.get_faces_dict(item)
            for face in item.faces_dict:
                if face.value is not None:
                    faces.append(convert_image(face.value))
    return faces

def test_chkType_like():
    with open('./YuaMikami.txt', 'r') as file:
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
    # image = np.frombuffer(image, dtype="uint8")
    image = cv2.imdecode(image, cv2.COLOR_BGR2GRAY)
    h, w = image.shape[:2]
    scale = 1
    #if h > 300 or w > 400:
    #    scale = 300 / max(h, w)
    #dims = (int(w * scale), int(h * scale))
    dims = (30, 40)
    interpln = cv2.INTER_LINEAR if scale > 1.0 else cv2.INTER_AREA
    image = cv2.resize(image, dims, interpolation=interpln)
    h, w = 30, 40
    # grayFace = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    vec = image.reshape(w * h)
    #vec = image.astype('float32')
    #image = np.asarray(image)
    return vec

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

def read_image(path):
    img = cv2.imread(path)
    h, w = img.shape[:2]
    scale = 1
    if h > 300 or w > 400:
        scale = 600 / max(h, w)
    dims = (int(w * scale), int(h * scale))
    interpln = cv2.INTER_LINEAR if scale > 1.0 else cv2.INTER_AREA
    img = cv2.resize(img, dims, interpolation=interpln)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    y, x = 0, 0
    h, w = 300, 400
    img = gray[y:y + h, x:x + w]
    img = img.copy()
    vec = img.reshape(w * h)
    # vec = vec.astype('float32')
    return vec

def test_read_image_convert_array():
    img1 = read_image('./6rfl_b.jpg')
    img2 = read_image('./6ewu_b.jpg')
    img3 = read_image('./798z_b.jpg')
    img = [img1, img2, img3]
    faces = np.asarray(img)
    faces
    return faces
