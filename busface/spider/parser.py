'''
html parser to extract data
'''
import re
from collections import namedtuple
from requests_html import HTML
from aspider.routeing import get_router
from busface.util import logger, APP_CONFIG, str2bool
from busface.spider.faceParser import parse_faces


router = get_router()




Tag = namedtuple('Tag', ['type', 'value'])
Face = namedtuple('Face', ['type', 'value', 'link'])


MORE_SAMPLES = str2bool(APP_CONFIG['sample.more_samples'])




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

    if MORE_SAMPLES:
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

