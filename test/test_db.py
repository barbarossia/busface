from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
from datetime import date
from busface.spider.parser import parse_face, url_to_image
import busface.model.faceDetector as fd
import cv2
import traceback


def test_save():
    item_url = 'https://www.cdnbus.bid/MADM-116'
    item_title = 'test item'
    item_fanhao = 'MADM-116'
    item_release_date = date(2019, 7, 19)
    item_meta_info = '{"cover_img_url": "https://pics.javcdn.pw/cover/7btq_b.jpg", "length": "120", "tags": {"star": ["\u6df1\u7530\u3048\u3044\u307f"], "genre": ["\u9ad8\u756b\u8cea", "DMM\u7368\u5bb6", "\u55ae\u9ad4\u4f5c\u54c1", "\u6deb\u8a9e", "\u5993\u5973", "\u53e3\u4ea4", "\u8569\u5a66", "\u5973\u751f"], "\u88fd\u4f5c\u5546:": ["kira\u2606kira"], "\u767c\u884c\u5546:": ["kira\u2606kira BLACK GAL"]}}'
    item = Item(title=item_title, url=item_url, fanhao=item_fanhao,
                release_date=item_release_date, meta_info=item_meta_info)
    item.save()

    blob1 = convert_binary_data('../test/6rfl_b.jpg')
    blob2 = convert_binary_data('../test/6ewu_b.jpg')
    blob3 = convert_binary_data('../test/798z_b.jpg')

    face1 = Face.create(type_='genre', value=blob1,
                      url='https://www.cdnbus.bid/genre/s1')
    face2 = Face.create(type_='star', value=blob2,
                      url='https://www.cdnbus.bid/star/dbd')
    tag3 = Face.create(type_='genre', value=blob3,
                      url='https://www.cdnbus.bid/genre/x1')
    ItemFace.create(item=item, face=face1)
    ItemFace.create(item=item, face=face2)

    ItemRate.saveit(RATE_TYPE.USER_RATE, RATE_VALUE.LIKE, item.fanhao)
    LocalItem.saveit('MADM-116', '/Download/MADM-116.avi')


def test_get_items():
    rate_type = RATE_TYPE.USER_RATE
    rate_value = RATE_VALUE.LIKE
    page = None
    items, page_info = get_items(
        rate_type=rate_type, rate_value=rate_value, page=page)
    assert len(items) > 0
    print(f'item count:{len(items)}')
    print(
        f'total_items: {page_info[0]}, total_page: {page_info[1]}, current_page: {page_info[2]}, page_size:{page_info[3]}')


def test_get_items2():
    rate_type = None
    rate_value = None
    page = None
    items, page_info = get_items(
        rate_type=rate_type, rate_value=rate_value, page=page)
    assert len(items) > 0
    print(f'item count:{len(items)}')
    print(
        f'total_items: {page_info[0]}, total_page: {page_info[1]}, current_page: {page_info[2]}, page_size:{page_info[3]}')


def test_getit():
    id = 1
    item = Item.getit(id)
    print(repr(item))
    assert item is not None


def test_tags_list():
    fanhao = 'LD-012'
    item = Item.get_by_fanhao(fanhao)
    Item.loadit(item)
    tags_dict = item.tags_dict
    tags = ['genre', 'star']
    limit = 10
    for t in tags:
        tags_dict[t] = tags_dict[t][:limit]
    print(tags_dict)


def test_download_face():
    rate_type = RATE_TYPE.USER_RATE
    rate_value = RATE_VALUE.LIKE
    page = None
    items, _ = get_items(
        rate_type=rate_type, rate_value=rate_value, page=page)
    assert len(items) > 0

    item = items[0]
    face = item.faces_dict[0]
    face_url = face.url


    inputImg = url_to_image(face_url)

    h, w = inputImg.shape[:2]
    scale = 1
    if h > 600 or w > 800:
        scale = 600 / max(h, w)
    dims = (int(w * scale), int(h * scale))
    interpln = cv2.INTER_LINEAR if scale > 1.0 else cv2.INTER_AREA
    inputImg = cv2.resize(inputImg, dims, interpolation=interpln)
    faces = fd.detect_faces_dnn(inputImg)
    faces

def test_save_download_image():
    face_url = 'https://pics.javcdn.pw/cover/798z_b.jpg'
    inputImg = url_to_image(face_url)
    img_encode = cv2.imencode('.jpg', inputImg)[1]
    print(type(img_encode))
    blob = img_encode.tobytes()
    face= Face.create(type_='genre', value=blob,
                        url=face_url)
    face

def test_save_detect_face():
    face_url = 'https://pics.javcdn.pw/cover/798z_b.jpg'

    blob = parse_face(face_url)
    created = Face.create(type_='genre', value=blob,
                       url=face_url)
    created

def test_update_face():
    id = 407
    face_info = Face.getit(id)
    face_info.value = parse_face(face_info.url)
    face_info = Face.updateit(face_info)
    face_info

def test_download_items():
    rate_type = RATE_TYPE.USER_RATE
    rate_value = RATE_VALUE.LIKE
    page = None
    items, _ = get_items(
        rate_type=rate_type, rate_value=rate_value, page=page)
    assert len(items) > 0
    try:
        for item in items:
            for face in item.faces_dict:
                if face.value == None:
                    face.value = parse_face(face.url)
                    face = Face.updateit(face)
                    print('update face')
    except Exception as e:
        print('system error')
        traceback.print_exc()