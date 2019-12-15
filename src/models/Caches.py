import sys
sys.path.append('..')

import pymongo

from classes.Cache import Cache

class Caches(object):
  def __init__(self, col):
    assert col is not None
    self.col = col
    self.setup()

  def setup(self):
    self.col.create_index([
      (Cache.OBJ_KEY, pymongo.TEXT),
      (Cache.OBJ_DATE_UPDATED, pymongo.DESCENDING)
    ])

  def save(self, cache):
    assert isinstance(cache, Cache)
    fil = Cache.build_filter(cache.key)
    obj = cache.to_obj()
    res = self.col.replace_one(fil, obj, upsert=True)
    if res.upserted_id is None and res.matched_count == 0:
      return None
    else:
      return res

  def load(self, key):
    assert isinstance(key, str)
    fil = Cache.build_filter(key)
    res = self.col.find_one(fil)
    if res is None:
      return None
    else:
      return Cache.from_obj(res)

  def delete(self, key):
    # cf. https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.delete_one
    assert isinstance(key, str)
    fil = Cache.build_filter(key)
    res = self.col.delete_one(fil)
    return res.deleted_count == 1
