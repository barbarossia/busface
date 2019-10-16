from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
from busface.model.classify import Classify
import cv2
import traceback
import numpy as np


def test_train():
    rate_type = RATE_TYPE.USER_RATE
    rate_value = None
    page = None
    items, _ = get_items(
        rate_type=rate_type, rate_value=rate_value, page=page)
    assert len(items) > 0

    faces = []
    typeSet = []
    for item in items:
        for face in item.faces_dict:
            faces.append(convert_image(face.value))
            if item.item_rate.rate_value == RATE_VALUE.LIKE:
                typeSet.append(1)
            else:
                typeSet.append(0)

    clf = Classify()
    clf.setTrainData(faces)
    clf.setTypeData(typeSet)
    try:
        clf.train()
        clf.saveModule()
    except Exception as e:
        print('system error')
        traceback.print_exc()

def test_chkType():
    fanhao = 'IPZ-931'
    item = Item.get_by_fanhao(fanhao)
    Item.get_faces_dict(item)

    faces = []
    for face in item.faces_dict:
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
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    grayFace = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return grayFace