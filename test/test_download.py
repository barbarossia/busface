import asyncio
import pytest
import aiohttp
from busface.spider.parser import parse_face
from aspider.routeing import get_router
from busface.spider.db import get_items, Item, RATE_TYPE, RATE_VALUE, ItemRate, LocalItem, Face, ItemFace, convert_binary_data
import time
import traceback

async def process(face, blob):
    start = time.perf_counter()
    face.value = blob
    Face.updateit(face)
    end = time.perf_counter() - start
    print(f"-->Chained result took {end:0.2f} seconds).")


async def process_face(face):
    start = time.perf_counter()
    blob = await parse_face(face.url)
    # save = await process(face, blob)
    end = time.perf_counter() - start
    print(f"-->Chained result took {end:0.2f} seconds).")


async def main(face_list):
    await asyncio.gather(process_face(n) for n in face_list)


def test_download_items():
    rate_type = RATE_TYPE.USER_RATE
    rate_value = RATE_VALUE.LIKE
    page = None
    items, _ = get_items(
        rate_type=rate_type, rate_value=rate_value, page=page)
    assert len(items) > 0
    face_list = []
    for item in items:
        for face in item.faces_dict:
            face_list.append(face)
    try:
        asyncio.run(main(face_list))
    except Exception as e:
        print('system error')
        traceback.print_exc()



