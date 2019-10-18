import sys
from aspider import aspider
from busface.util import logger, APP_CONFIG
from aspider.routeing import get_router
from busface.spider.parser import parse_item
from busface.spider.db import save, Item, ItemRate, RATE_TYPE, RATE_VALUE
from busface.util import APP_CONFIG, get_full_url, logger
from busface.app.local import add_local_fanhao
from busface.spider import bus_spider
from busface.app.schedule import start_scheduler, add_download_job
import threading
import traceback
import re


router = get_router()
MAXPAGE = 30

root_url = ['https://www.busdmm.work/YSN-484', 'https://pics.javcdn.pw']


@router.route('/cover/<img>')
def process_image(text, path, img):
    '''
    process item page
    '''
    logger.debug(f'process image {text}')
    logger.debug(f'process image {path}')
    logger.debug(f'process image {img}')
    print(f'image {img} is processed')

@router.route('/<fanhao:[\w]+-[\d]+>')
def process_item(text, path, fanhao):
    '''
    process item page
    '''
    print(f'item {fanhao} is processed')


def test_download_fanhao():
    print('start download')
    roots = root_url
    extra_args = {
        'roots': roots,
        'no_parse_links': False,
        'count': 10
    }
    stats = aspider.download(extra_args=extra_args)
    stats.report()


def test_match():
    pattern = '[\w]+_b.jpg'
    path = '79te_b.jpg'
    match = re.match(pattern, path)
    match


