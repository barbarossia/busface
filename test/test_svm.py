from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
from busface.model.classify import Classify
import cv2
import traceback
import numpy as np
import pandas as pd
import re
from busface.util import logger

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


def test_create_lfw():
    lfw_people = create_lfw()
    # introspect the images arrays to find the shapes (for plotting)
    n_samples, h, w = lfw_people.images.shape

    # for machine learning we use the 2 data directly (as relative pixel
    # positions info is ignored by this model)
    X = lfw_people.data
    n_features = X.shape[1]

    # the label to predict is the id of the person
    y = lfw_people.target
    target_names = lfw_people.target_names
    n_classes = target_names.shape[0]

    print("Total dataset size:")
    print("n_samples: %d" % n_samples)
    print("n_features: %d" % n_features)
    print("n_classes: %d" % n_classes)


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


def test_get_data_by_name():
    name = 'Aizawa'
    target_value = 0
    data, image, target = get_data_by_name(name, target_value)
    data
    image
    target

def get_data_by_name(name, target_value):
    file = './{}.txt'.format(name)
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
                    'image': image
                }

                face_list.append(d)

    return face_list

