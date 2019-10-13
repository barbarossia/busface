import sys
from aspider import aspider
from busface.util import logger, APP_CONFIG
from aspider.routeing import get_router
from busface.spider.parser import parse_item
from busface.spider.db import save, Item
from busface.util import APP_CONFIG, get_full_url, logger
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


@router.route('/<fanhao:[\w]+-[\d]+>', verify_fanhao)
def process_item(text, path, fanhao):
    '''
    process item page
    '''
    logger.debug(f'process item {fanhao}')
    url = path
    meta, faces = parse_item(text)
    meta.update(url=url)
#     logger.debug('meta keys', len(meta.keys()))
#     logger.debug('tag count', len(tags))
    save(meta, faces)
    print(f'item {fanhao} is processed')

def test_download():
    print('start download')
    roots = ['https://www.busdmm.work', ]
    extra_args = {
        'roots': roots,
        'no_parse_links': False,
        'count': 100
    }
    stats = aspider.download(extra_args=extra_args)
    stats.report()

