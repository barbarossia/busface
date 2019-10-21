import sys
from aspider import aspider
from busface.util import logger, APP_CONFIG
from aspider.routeing import get_router
from busface.spider.parser import parse_item
from busface.spider.db import save, Item, ItemRate, RATE_TYPE, RATE_VALUE, get_items
from busface.util import APP_CONFIG, get_full_url, logger
from busface.app.local import add_local_fanhao
from busface.spider import bus_spider
from busface.app.schedule import start_scheduler, add_download_job
import threading
import os
from busface.util import get_cwd


DATA_PATH = 'data/'
MODEL_PATH = 'model/'
model_path = os.path.join(get_cwd(), DATA_PATH, MODEL_PATH)

router = get_router()
MAXPAGE = 30

root_url = 'https://www.busdmm.work'

def get_url_by_fanhao(fanhao):
    # return full url
    url = get_full_url(fanhao)
    return url


def verify_page_path(path, no):
    logger.debug(f'verify page {path} , args {no}')
    no = int(no)
    if no <= MAXPAGE:
        return True
    else:
        return False


@router.route('/page/<no>', verify_page_path)
def process_page(text, path, no):
    '''
    process list page
    '''
    logger.debug(f'page {no} has length {len(text)}')
    print(f'process page {no}')


def verify_fanhao(path, fanhao):
    '''
    verify fanhao before add it to queue
    '''
    exists = Item.get_by_fanhao(fanhao)
    logger.debug(
        f'verify {fanhao}: , exists:{exists is not None}, skip {path}')
    return exists is None


@router.route('/<fanhao:[\w]+-[\d]+>')
def process_item(text, path, fanhao):
    '''
    process item page
    '''
    logger.debug(f'process item {fanhao}')
    url = path
    meta, faces = parse_item(text)
    meta.update(url=url)
    # logger.debug('meta keys', len(meta.keys()))
    # logger.debug('faces cout', len(faces))
    save(meta, faces)
    print(f'item {fanhao} is processed')

def test_download():
    print('start download')
    roots = ['https://www.cdnbus.bid', ]
    extra_args = {
        'roots': roots,
        'no_parse_links': False,
        'count': 100
    }
    stats = aspider.download(extra_args=extra_args)
    stats.report()


def test_download_fanhao():
    print('start download')
    roots = ['https://www.busdmm.work/YSN-484', ]
    extra_args = {
        'roots': roots,
        'no_parse_links': True
    }
    stats = aspider.download(extra_args=extra_args)
    stats.report()


def test_tagit():
    fanhao = 'UMSO-274'
    # item_rate = ItemRate.get_by_fanhao(fanhao)
    rate_type = RATE_TYPE.USER_RATE
    rate_value = RATE_VALUE.DISLIKE
    ItemRate.saveit(rate_type, rate_value, fanhao)

def test_tagit_all():
    rate_type = None
    rate_value = None
    page = None
    items, _ = get_items(
        rate_type=rate_type, rate_value=rate_value, page=page)
    for item in items:
        fanhao = item.fanhao
        rate_type = RATE_TYPE.USER_RATE
        rate_value = RATE_VALUE.DISLIKE
        ItemRate.saveit(rate_type, rate_value, fanhao)



def test_upload():
    print('start read from file')
    with open('./Tsubasa.txt', 'r') as file:
        fanhao_list = file.read()

    tag_like = RATE_VALUE.LIKE
    missed_fanhao, local_file_count, tag_file_count = add_local_fanhao(
        fanhao_list, tag_like)
    if len(missed_fanhao) > 0:
        print('start download')
        urls = [bus_spider.get_url_by_fanhao(
            fanhao) for fanhao in missed_fanhao]

        extra_args = {
            'roots': urls,
            'no_parse_links': True
        }
        stats = aspider.download(extra_args=extra_args)
        stats.report()



