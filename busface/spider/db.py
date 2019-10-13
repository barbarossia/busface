'''
persist data to db
'''
from datetime import date
import datetime
import operator
from functools import reduce
import json
from peewee import *
from enum import IntEnum
from collections import defaultdict
from busface.util import logger, get_data_path, format_datetime, get_now_time, get_full_url

DB_FILE = 'bus.db'
db = SqliteDatabase(get_data_path(DB_FILE), pragmas={
    'journal_mode': 'wal'})


class BaseModel(Model):
    class Meta:
        database = db
        legacy_table_names = False


class ExistError(Exception):
    pass


class DBError(Exception):
    pass


class Item(BaseModel):
    '''
    item table
    '''
    title = CharField()
    fanhao = CharField(unique=True)
    url = CharField(unique=True)
    release_date = DateField()
    add_date = DateTimeField(default=datetime.datetime.now)
    meta_info = TextField()

    def __repr__(self):
        return f'<Item:{self.fanhao} {self.title}>'

    @staticmethod
    def saveit(meta_info):
        item_release_date = date.fromisoformat(meta_info.pop('release_date'))
        item_fanhao = meta_info.pop('fanhao')
        item_title = meta_info.pop('title')
        item_url = meta_info.pop('url')
        item_meta = json.dumps(meta_info)
        try:
            item = Item.create(fanhao=item_fanhao, title=item_title, url=item_url,
                               release_date=item_release_date, meta_info=item_meta)
            logger.debug(f'save item:  {item}')
        except IntegrityError:
            logger.debug('Item exists: {item_fanhao}')
            raise ExistError()
        else:
            return item

    @staticmethod
    def loadit(item):
        item.url = get_full_url(item.url)
        meta = json.loads(item.meta_info)
        item.cover_img_url = meta['cover_img_url']
        item.add_date = format_datetime(item.add_date)

    @staticmethod
    def getit(id):
        item = Item.get_by_id(id)
        return item

    @staticmethod
    def get_by_fanhao(fanhao):
        item = Item.get_or_none(Item.fanhao == fanhao)
        return item

    @staticmethod
    def get_faces_dict(item):
        faces_dict = defaultdict(list)
        for t in item.faces_list:
            faces_dict[t.face.type_].append(t.face.value)
        item.tags_dict = faces_dict


class Face(BaseModel):
    '''
    tag table
    '''
    type_ = CharField(column_name='type')
    value = BlobField(null=True)
    url = CharField()

    def __repr__(self):
        return f'<Face {self.value}>'

    @staticmethod
    def saveit(face_info):
        try:
            face = Face.create(type_=face_info.type, value=face_info.value,
                                         url=face_info.link)
            logger.debug(f'save face:  {face}')
        except IntegrityError:
            logger.debug('face exists: {face}')
            raise ExistError()
        else:
            return face


class ItemFace(BaseModel):
    item = ForeignKeyField(Item, field='fanhao', backref='faces_list')
    face = ForeignKeyField(Face, backref='items')

    class Meta:
        indexes = (
            # Specify a unique multi-column index
            (('item', 'face'), True),
        )

    @staticmethod
    def saveit(item, face):
        try:
            item_face = ItemFace.create(item=item, face=face)
            logger.debug(f'save face_item: {item_face}')
        except Exception as ex:
            logger.exception(ex)
        else:
            return item_face

    def __repr__(self):
        return f'<ItemFace {self.item.fanhao} - {self.face.value}>'


class RATE_TYPE(IntEnum):
    NOT_RATE = 0
    USER_RATE = 1
    SYSTEM_RATE = 2


class RATE_VALUE(IntEnum):
    LIKE = 1
    DISLIKE = 0


class ItemRate(BaseModel):
    rate_type = IntegerField()
    rate_value = IntegerField()
    item = ForeignKeyField(Item, field='fanhao',
                           backref='rated_items', unique=True)
    rete_time = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def saveit(rate_type, rate_value, fanhao):
        item_rate = None
        try:
            item_rate = ItemRate.create(
                item=fanhao, rate_type=rate_type, rate_value=rate_value)
            logger.debug(f'save ItemRate: {item_rate}')
        except IntegrityError:
            logger.debug(f'ItemRate exists: {fanhao}')
        else:
            return item_rate

    @staticmethod
    def getit(id):
        item_rate = ItemRate.get_or_none(ItemRate.id == id)
        return item_rate

    @staticmethod
    def get_by_fanhao(fanhao):
        item_rate = ItemRate.get_or_none(ItemRate.item_id == fanhao)
        return item_rate


class LocalItem(BaseModel):
    '''
    local item table
    '''
    item = ForeignKeyField(Item, field='fanhao',
                           backref='local_item', unique=True)
    path = CharField(null=True)
    size = IntegerField(null=True)
    add_date = DateTimeField(default=datetime.datetime.now)
    last_view_date = DateTimeField(null=True)
    view_times = IntegerField(default=0)

    @staticmethod
    def saveit(fanhao, path):
        local_item = None
        try:
            local_item = LocalItem.create(
                item=fanhao, path=path)
            logger.debug(f'save LocalItem: {fanhao}')
        except IntegrityError:
            logger.debug(f'LocalItem exists: {fanhao}')
        else:
            return local_item

    def __repr__(self):
        return f'<LocalItem {self.fanhao}({self.path})>'

    @staticmethod
    def update_play(id):
        nrows = (LocalItem
                 .update({LocalItem.last_view_date: get_now_time(),
                          LocalItem.view_times: LocalItem.view_times + 1})
                 .where(LocalItem.id == id)
                 .execute())
        logger.debug(f'update LocalItem {id} : rows:{nrows}')
        return LocalItem.get_by_id(id)

    @staticmethod
    def loadit(local_item):
        local_item.last_view_date = format_datetime(
            local_item.last_view_date) if local_item.last_view_date else ''


def save(meta_info, faces):
    item_title = meta_info['title']
    face_objs = []
    try:
        item = Item.saveit(meta_info)
    except ExistError:
        logger.debug(f'item exists: {item_title}')
    else:
        with db.atomic():
            for face_info in faces:
                face = Face.saveit(face_info)
                if face:
                    face_objs.append(face)
        with db.atomic():
            for face_obj in face_objs:
                ItemFace.saveit(item, face_obj)


def get_items(rate_type=None, rate_value=None, page=1, page_size=10):
    '''
    get required items based on some conditions
    '''
    items_list = []
    clauses = []
    if rate_type is not None:
        clauses.append(ItemRate.rate_type == rate_type)
    else:
        clauses.append(ItemRate.rate_type.is_null())
    if rate_value is not None:
        clauses.append(ItemRate.rate_value == rate_value)
    q = (Item.select(Item, ItemRate)
         .join(ItemRate, JOIN.LEFT_OUTER, attr='item_rate')
         .where(reduce(operator.and_, clauses))
         .order_by(Item.id.desc())
         )
    total_items = q.count()
    if not page is None:
        q = q.paginate(page, page_size)
    items = get_faces_for_items(q)
    for item in items:
        Item.loadit(item)
        if hasattr(item, 'item_rate'):
            item.rate_value = item.item_rate.rate_value
        else:
            item.rate_value = None
        items_list.append(item)

    total_pages = (total_items + page_size - 1) // page_size
    page_info = (total_items, total_pages, page, page_size)
    return items_list, page_info


def get_local_items(page=1, page_size=10):
    '''
    get local items
    '''
    items = []
    q = (LocalItem.select(LocalItem)
         .where(LocalItem.path.is_null(False))
         .order_by(LocalItem.id.desc())
         )
    total_items = q.count()
    if not page is None:
        q = q.paginate(page, page_size)

    item_query = Item.select()
    item_face_query = ItemFace.select()
    face_query = Face.select()
    items_with_faces = prefetch(q, item_query, item_face_query, face_query)

    for local_item in items_with_faces:
        try:
            Item.loadit(local_item.item)
            Item.get_faces_dict(local_item.item)
            items.append(local_item)
        except Exception:
            pass

    total_pages = (total_items + page_size - 1) // page_size
    page_info = (total_items, total_pages, page, page_size)
    return items, page_info


def get_today_update_count():
    now = get_now_time()
    year, month, day = now.year, now.month, now.day
    q = Item.select().where((Item.add_date.year == year)
                            & (Item.add_date.month == month)
                            & (Item.add_date.day == day)
                            )
    return q.count()


def get_today_recommend_count():
    now = get_now_time()
    year, month, day = now.year, now.month, now.day
    q = ItemRate.select().where((ItemRate.rete_time.year == year)
                                & (ItemRate.rete_time.month == month)
                                & (ItemRate.rete_time.day == day)
                                & (ItemRate.rate_type == RATE_TYPE.SYSTEM_RATE)
                                & (ItemRate.rate_value == RATE_VALUE.LIKE)
                                )
    return q.count()


def get_faces_for_items(items_query):
    item_face_query = ItemFace.select()
    face_query = Face.select()
    items_with_faces = prefetch(items_query, item_face_query, face_query)
    items = []
    for item in items_with_faces:
        Item.get_faces_dict(item)
        items.append(item)

    return items


def convert_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


def init():
    db.connect(reuse_if_open=True)
    db.create_tables([Item, Face, ItemFace, ItemRate, LocalItem])


init()
