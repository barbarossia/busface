import numpy as np
import cv2
import traceback
import busface.model.faceDetector as fd
import urllib.request
from busface.util import logger, APP_CONFIG

DESIRED_SIZE_W = int(APP_CONFIG['sample.crop_width'])
DESIRED_SIZE_H = int(APP_CONFIG['sample.crop_height'])

class AppURLopener(urllib.request.FancyURLopener):
    version = "App/1.7"

def up_scale_face(oriimg, old_size):
    ratio = float(DESIRED_SIZE_W) / old_size[1]
    new_size = tuple([int(x * ratio) for x in old_size])

    # new_size should be in (width, height) format

    oriimg = cv2.resize(oriimg, (new_size[1], new_size[0]))

    delta_w = DESIRED_SIZE_W - new_size[1]
    delta_h = DESIRED_SIZE_H - new_size[0]

    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    color = [0, 0, 0]
    new_img = cv2.copyMakeBorder(oriimg, top, bottom, left, right, cv2.BORDER_CONSTANT,
                                 value=color)

    return new_img


def down_scale_face(oriimg, old_size):

    # new_size should be in (width, height) format

    delta_w = DESIRED_SIZE_W - old_size[1]
    delta_h = DESIRED_SIZE_H - old_size[0]

    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    color = [0, 0, 0]
    new_img = cv2.copyMakeBorder(oriimg, top, bottom, left, right, cv2.BORDER_CONSTANT,
                                 value=color)

    return new_img

def resize_face(oriimg):

    old_size = oriimg.shape[:2]  # old_size is in (height, width) format

    if old_size[0] > DESIRED_SIZE_H:
        oriimg = pre_resize_face_h(oriimg)

    old_size = oriimg.shape[:2]  # old_size is in (height, width) format
    if old_size[1] > DESIRED_SIZE_W:
        oriimg = pre_resize_face_w(oriimg)

    old_size = oriimg.shape[:2]  # old_size is in (height, width) format
    if old_size[0] < DESIRED_SIZE_H or old_size[1] < DESIRED_SIZE_W:
        return down_scale_face(oriimg, old_size)
    elif old_size[0] == DESIRED_SIZE_H and old_size[1] == DESIRED_SIZE_W:
        return oriimg
    else:
        return up_scale_face(oriimg, old_size)

def pre_resize_face_h(img):
    h, w = img.shape[:2]
    scale = 1
    if h > DESIRED_SIZE_H:
        scale = DESIRED_SIZE_H / h
    dims = (int(w * scale), DESIRED_SIZE_H)
    new_img = cv2.resize(img, dims, interpolation=cv2.INTER_AREA)
    return new_img

def pre_resize_face_w(img):
    h, w = img.shape[:2]
    scale = 1
    if w > DESIRED_SIZE_W:
        scale = DESIRED_SIZE_W / w
    dims = (DESIRED_SIZE_W, int(h * scale))
    new_img = cv2.resize(img, dims, interpolation=cv2.INTER_AREA)
    return new_img

def parse_face(face, inputImg):
    x = face[0]
    y = face[1]
    w = face[2]
    h = face[3]

    if x < 0 or y < 0 or w < 0 or h < 0:
        return None
    if w < DESIRED_SIZE_W or h < DESIRED_SIZE_H:
        return None

    img = inputImg[y:y + h, x:x + w]
    faceImg = img.copy()

    resized_face = resize_face(faceImg)
    img_encode = cv2.imencode('.jpg', resized_face)[1]
    blob = img_encode.tobytes()
    return blob

def parse_faces(url):
    inputImg = url_to_image(url)

    faces = fd.detect_faces_dnn(inputImg)
    if not faces:
        return None

    faces_data = []
    for face in faces:
        data = parse_face(face, inputImg)
        faces_data.append(data)

    return faces_data


def url_to_image(url):
    try:
        opener = AppURLopener()
        response = opener.open(url)
        image = np.asarray(bytearray(response.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    except Exception as e:
        traceback.print_exc()
        return None
    return image
