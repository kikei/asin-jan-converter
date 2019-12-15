import sys
sys.path.append('..')

import pymongo

from classes.Identifier import Identifier

class Identifiers(object):
  def __init__(self, col):
    assert col is not None
    self.col = col
    self.setup()

  def setup(self):
    self.col.create_index([('ean', pymongo.ASCENDING)])
    self.col.create_index([('asin', pymongo.ASCENDING)])

  def save(self, item, extend=False):
    assert isinstance(item, Identifier)
    assert item.ean is not None or item.asin is not None
    fil = Identifier.filter_intersection(ean=item.ean, asin=item.asin)
    if extend:
      a = self.col.find_one(fil)
      if a is not None:
        item = Identifier.extend(Identifier.from_obj(a), item)
    obj = item.to_obj()
    res = self.col.replace_one(fil, obj, upsert=True)
    if res.upserted_id is None and res.matched_count == 0:
      return None
    else:
      return res

  def save_all(self, items, extend=False):
    assert isinstance(items, list)
    ops = []
    for item in items:
      assert isinstance(item, Identifier)
      assert item.ean is not None or item.asin is not None
      fil = Identifier.filter_intersection(ean=item.ean, asin=item.asin)
      if extend:
        a = self.col.find_one(fil)
        if a is not None:
          item = Identifier.extend(Identifier.from_obj(a), item)
      obj = item.to_obj()
      print('Save obj={o}.'.format(o=obj))
      ops.append(pymongo.ReplaceOne(fil, obj, upsert=True))
    if len(ops) == 0:
      return None
    else:
      res = self.col.bulk_write(ops)
      #print(result.bulk_api_result)
      return res

  def load(self, ean=None, asin=None):
    assert ean is not None or asin is not None
    fil = Identifier.filter_intersection(ean=ean, asin=asin)
    res = self.col.find_one(fil)
    if res is None:
      return None
    else:
      return Identifier.from_obj(res)

  def all(self, status=[], skip=None, limit=None, order_by=None):
    assert status is None or isinstance(status, list)
    assert skip is None or isinstance(skip, int)
    assert limit is None or isinstance(limit, int)
    if status is None or len(status) == 0:
      fil = {}
    else:
      if Identifier.NEW in status:
        status.append(None)
      fil = {'status': {'$in': status}}
    options = {}
    if skip is not None:
      options['skip'] = skip
    if limit is not None:
      options['limit'] = limit
    objs = self.col.find(fil, **options)
    print(order_by)  
    if order_by is not None:
      objs.sort([order_by])
    for obj in objs:
      yield Identifier.from_obj(obj)
