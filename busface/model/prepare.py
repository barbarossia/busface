from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
import cv2
import traceback
import numpy as np
import pandas as pd
import re
import os
from busface.util import get_cwd

DATA_PATH = 'data/'
MODEL_PATH = 'model/'
model_path = os.path.join(get_cwd(), DATA_PATH, MODEL_PATH)


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


class lfw_bus:
    images = np.zeros(2, )
    data = np.zeros(5)
    target = np.zeros(5)
    target_names = np.zeros(5)

    def set_images(self, image_data):
        self.images = image_data

    def set_data(self, data_):
        self.data = data_

    def set_target(self, target_data):
        self.target = target_data

    def set_target_names(self, target_names_data):
        self.target_names = target_names_data

def create_bus_data():
    items = load_data()
    dicts = as_dict(items)
    images = []
    data_list = []
    targets = []
    target_names = ['dislike', 'like']

    for dict in dicts:
        data, image, target = dict['data'], dict['image'], dict['target']
        images.append(image)
        data_list.append(data)
        targets.append(target)

    lfw = lfw_bus()
    lfw.set_data(np.asarray(data_list))
    lfw.set_images(np.asarray(images))
    lfw.set_target(np.asarray(targets))
    lfw.set_target_names(np.asarray(target_names))
    return lfw


def create_lfw():
    target_names = ['Aizawa', 'Asuka', 'Hashimoto', 'Takahashi', 'Tsubasa', 'YuaMikami']
    #target_names = ['Aizawa']
    images = []
    data_list = []
    targets = []

    for i in range(len(target_names)):
        data, image, target = get_data_by_name(target_names[i], i)
        images.extend(image)
        data_list.extend(data)
        targets.extend(target)

    lfw = lfw_bus()
    lfw.set_data(np.asarray(data_list))
    lfw.set_images(np.asarray(images))
    lfw.set_target(np.asarray(targets))
    lfw.set_target_names(np.asarray(target_names))
    return lfw

def get_data_by_name(name, target_value):
    file = '{}/{}.txt'.format(model_path, name)
    with open(file, 'r') as file:
        fanhao_list = file.read()
    data, image = get_faces(fanhao_list)

    target = [target_value] * len(data)
    return data, image, target

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


def get_faces(list):
    items = []
    fanhao_list = get_fanhao(list)

    for item_id in fanhao_list:
        item = Item.get_by_fanhao(item_id)
        if item is not None:
            Item.get_faces_dict(item)
            items.append(item)

    dicts = as_dict(items)
    #df = pd.DataFrame(dicts, columns=['data', 'image'])
    data_list = []
    images = []
    for dic in dicts:
        data_list.append(dic['data'])
        images.append(dic['image'])
    return data_list, images


def read_image(value):
    image = np.asarray(bytearray(value), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def convert_image(image):
    h, w = image.shape[:2]
    vec = image.reshape(w * h)
    return vec

def as_dict(items):
    face_list = []

    for item in items:
        for face in item.faces_dict:
            if face.value is not None:
                image = read_image(face.value)
                data = convert_image(image)
                d = {
                    'data': data,
                    'image': image,
                    'target': item.rate_value
                }

                face_list.append(d)

    return face_list