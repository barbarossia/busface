'''
html parser to extract data
'''
import re
import requests
from collections import namedtuple
from requests_html import HTML
from aspider.routeing import get_router
import numpy as np
import cv2
import traceback
import busface.model.faceDetector as fd
from urllib.request import urlopen
import urllib.request
from busface.util import logger, APP_CONFIG


class AppURLopener(urllib.request.FancyURLopener):
    version = "App/1.7"


router = get_router()

Tag = namedtuple('Tag', ['type', 'value'])
Face = namedtuple('Face', ['type', 'value', 'link'])

DESIRED_SIZE_W = int(APP_CONFIG['image.crop_width'])
DESIRED_SIZE_H = int(APP_CONFIG['image.crop_height'])

def parse_item(text):
    '''
    Args:
        text : str - html text

    Returns:
        tuple: (dict, list)
        dict - meta data for this item
        list - tags for this item
    '''
    html = HTML(html=text)
    title_css = 'body > div.container > h3'
    title = html.find(title_css)[0].text
    cover_img_css = 'body > div.container > div.row.movie > div.col-md-9.screencap > a'
    cover_img_url = html.find(cover_img_css)[0].attrs['href']
    tags_css = 'body > div.container > div.row.movie > div.col-md-3.info'
    tags = html.find(tags_css)[0].find('p')
    release_date = tags[1].text
    length = tags[2].text

    sample_img_css = 'body > div.container > #sample-waterfall > a.sample-box'
    samples = html.find(sample_img_css)

    # meta data
    meta = {}
    meta['fanhao'], meta['title'] = title.split(maxsplit=1)
    meta['cover_img_url'] = cover_img_url
    meta['release_date'] = release_date.split()[1]
    meta['length'] = re.search(r'\d+', length).group()

    tag_list = {}
    tag_list.setdefault('star', [])
    tag_list.setdefault('genre', [])
    for tag in tags[3:]:
        links = tag.find('a')
        spans = tag.find('span.header')
        if spans and len(links) == 1:
            tag_type = (spans[0].text)
            tag_value = links[0].text
            if tag_type != '' and tag_value != '':
                tag_list.setdefault(tag_type, []).append(tag_value)
        else:
            for link in links:
                tag_link = link.attrs['href']
                tag_value = link.text
                if 'genre' in tag_link:
                    tag_type = 'genre'
                if 'star' in tag_link:
                    tag_type = 'star'
                if tag_type != '' and tag_value != '':
                    tag_list.setdefault(tag_type, []).append(tag_value)


    face_list = []
    cover = create_face('cover', cover_img_url)
    if cover is not None:
        face_list.extend(cover)

    for sample in samples:
         link = sample.attrs['href']
         face_type = 'sample'
         sample_face = create_face(face_type, link)
         if sample_face is not None:
            face_list.extend(sample_face)

    meta['tags'] = tag_list
    return meta, face_list


def create_tag(tag_type, tag_value):
    tag = Tag(tag_type, tag_value)
    return tag


def create_face(face_type, face_link):
    blobs = parse_faces(face_link)
    if blobs is None: return None

    faces = []
    for blob in blobs:
        if blob is not None:
            face = Face(face_type, blob, face_link)
            faces.append(face)
    return faces

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
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    # resp = urllib.urlopen(url)
    # image = np.asarray(bytearray(resp.read()), dtype="uint8")
    # image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    try:
        # image = imutils.url_to_image(url)
        opener = AppURLopener()
        response = opener.open(url)
        image = np.asarray(bytearray(response.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    except Exception as e:
        traceback.print_exc()
        return None
    # return the image
    return image
