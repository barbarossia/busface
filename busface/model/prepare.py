from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
import cv2
import traceback
import numpy as np
import pandas as pd
import re
from sklearn.decomposition import PCA
from busface.util import MODEL_PATH, get_data_path, APP_CONFIG
from sklearn.model_selection import train_test_split

MODEL_FILE = MODEL_PATH + 'train.mdl'
MIN_TRAIN_NUM = int(APP_CONFIG['sample.n_components'])

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
    ids = np.zeros(5)

    def set_images(self, image_data):
        self.images = image_data

    def set_data(self, data_):
        self.data = data_

    def set_target(self, target_data):
        self.target = target_data

    def set_target_names(self, target_names_data):
        self.target_names = target_names_data

    def set_ids(self, ids):
        self.ids = ids

def create_data(dicts):
    images = []
    data_list = []
    targets = []
    ids = []
    target_names = ['dislike', 'like']

    for dict in dicts:
        data, image, target, id = dict['data'], dict['image'], dict['target'], dict['id']
        images.append(image)
        data_list.append(data)
        targets.append(target)
        ids.append(id)

    lfw = lfw_bus()
    lfw.set_data(np.asarray(data_list))
    lfw.set_images(np.asarray(images))
    lfw.set_target(np.asarray(targets))
    lfw.set_target_names(np.asarray(target_names))
    lfw.set_ids(np.asarray(ids))
    return lfw

def create_bus_data():
    items = load_data()
    dicts = as_dict(items)
    return create_data(dicts)

def prepare_data():
    bus_data = create_bus_data()

    X = bus_data.data

    # the label to predict is the id of the person
    y = bus_data.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42)

    return X_train, X_test, y_train, y_test

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
    file = '{}/{}.txt'.format(get_data_path(MODEL_PATH), name)
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
                    'id': item.fanhao,
                    'data': data,
                    'image': image,
                    'target': item.rate_value
                }

                face_list.append(d)

    return face_list

def prepare_predict_data():
    # get not rated data
    rate_type = None
    rate_value = None
    page = None
    unrated_items, _ = get_items(
        rate_type=rate_type, rate_value=rate_value, page=page)
    #mlb = load_model(get_data_path(MODEL_FILE))
    dicts = as_dict(unrated_items)
    lfw = create_data(dicts)
    return lfw.ids, dimension(lfw.data)

def dimension(X_train):
    pca = PCA(n_components=MIN_TRAIN_NUM, svd_solver='randomized',
              whiten=True).fit(X_train)
    X_train_pca = pca.transform(X_train)
    return X_train_pca