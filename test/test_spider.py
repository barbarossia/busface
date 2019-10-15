from busface.spider.bus_spider import process_item
from aspider.routeing import get_router
from requests_html import HTMLSession
from aspider import aspider
from busface.util import logger

router = get_router()

def test_process_item():
    root_path = 'https://www.busdmm.work'
    url = 'https://www.busdmm.work/LD-012'
    session = HTMLSession()
    router = get_router()
    router.add_root_path(root_path)
    fanhao = 'LD-012'
    r = session.get(url)
    process_item(r.text, url, fanhao)

def test_routing1():
    '''
    pass roots to aspider
    '''

    @router.route('/\w+\.jpg', no_parse_links=True)
    def parse_item(text, path):
        logger.debug('parse_item')
        print(path)

    roots = ['https://pics.javcdn.pw/cover/7btq_b.jpg']
    extra_args = {
        'roots': roots,
        'no_parse_links': True
    }
    stats_report = aspider.download(extra_args=extra_args)
    stats_report.report()
