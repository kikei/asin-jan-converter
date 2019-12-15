class Cache(object):
  OBJ_KEY = 'k'
  OBJ_DATA = 'd'
  OBJ_METADATA = 'm'
  OBJ_DATE_UPDATED = 'u'

  def __init__(self, key, data, metadata=None, date_updated=None):
    assert isinstance(key, str)
    self.key = key
    self.data = data
    if metadata is not None:
      self.metadata = {}
    else:
      self.metadata = metadata
    self.date_updated = date_updated

  @staticmethod
  def from_obj(obj):
    assert obj is not None
    return Cache(obj[Cache.OBJ_KEY],
                 obj[Cache.OBJ_DATA],
                 obj[Cache.OBJ_METADATA],
                 obj[Cache.OBJ_DATE_UPDATED])

  @staticmethod
  def build_filter(key):
    assert isinstance(key, str)
    return {
      Cache.OBJ_KEY: key
    }

  def to_obj(self):
    return {
      Cache.OBJ_KEY: self.key,
      Cache.OBJ_DATA: self.data,
      Cache.OBJ_METADATA: self.metadata,
      Cache.OBJ_DATE_UPDATED: self.date_updated
    }
