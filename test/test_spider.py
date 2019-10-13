from busface.spider.bus_spider import process_item
from aspider.routeing import get_router
from requests_html import HTMLSession
import logging


def test_process_item():
    root_path = 'https://www.busdmm.work'
    url = 'https://www.busdmm.work/LD-012'
    session = HTMLSession()
    router = get_router()
    router.add_root_path(root_path)
    fanhao = 'LD-012'
    r = session.get(url)
    process_item(r.text, url, fanhao)
