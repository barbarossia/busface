from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
from datetime import date
from busface.spider.parser import download_face, url_to_image
import busface.model.faceDetector as fd
import cv2


def test_save():
    item_url = 'https://www.cdnbus.bid/MADM-116'
    item_title = 'test item'
    item_fanhao = 'MADM-116'
    item_release_date = date(2019, 7, 19)
    item_meta_info = '{"cover_img_url": "https://pics.javcdn.pw/cover/7ben_b.jpg", "length": "170"}'
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
    fanhao = 'DOCP-176'
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









