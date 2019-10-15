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


class AppURLopener(urllib.request.FancyURLopener):
    version = "App/1.7"


router = get_router()

Tag = namedtuple('Tag', ['type', 'value'])
Face = namedtuple('Face', ['type', 'value', 'link'])


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

    sample_img_css = 'body > div.container > #sample-waterfall > a.sample-box > div.photo-frame'
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
    face_list.append(create_face('cover', None, cover_img_url))

    for sample in samples:
        links = sample.find('img')[0].attrs['src']
        face_type = 'sample'
        face_list.append(create_face(face_type, None, links))

    meta['tags'] = tag_list
    return meta, face_list


def create_tag(tag_type, tag_value):
    tag = Tag(tag_type, tag_value)
    return tag


def create_face(face_type, face_value, face_link):
    # face_link = router.get_url_path(face_link)
    face = Face(face_type, face_value, face_link)
    return face

async def parse_face(url):
    inputImg = url_to_image(url)
    h, w = inputImg.shape[:2]
    scale = 1
    if h > 600 or w > 800:
        scale = 600 / max(h, w)
    dims = (int(w * scale), int(h * scale))
    interpln = cv2.INTER_LINEAR if scale > 1.0 else cv2.INTER_AREA
    inputImg = cv2.resize(inputImg, dims, interpolation=interpln)
    faces = fd.detect_faces_dnn(inputImg)
    face = faces[0]
    x = face[0]
    y = face[1]
    w = face[2]
    h = face[3]
    img = inputImg[y:y + h, x:x + w]
    faceImg = img.copy()

    img_encode = cv2.imencode('.jpg', faceImg)[1]
    # print(type(img_encode))
    blob = img_encode.tobytes()
    return blob

async def url_to_image(url):
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
    # return the image
    return image
