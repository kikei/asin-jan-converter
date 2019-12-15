import datetime

class Identifier(object):
  """
  EAN can contain EAN, JAN, ISBN, etc.
  """
  SUCCESS = 0
  FAILED = 1
  NEW = 2

  OBJ_EAN = 'ean'
  OBJ_ASIN = 'asin'
  OBJ_STATUS = 'status'
  OBJ_UPDATED = 'updated'
  OBJ_TITLE = 'title'
  
  def __init__(self, ean=None, asin=None,
               status=None, updated=None, title=None):
    assert ean is not None or asin is not None
    self.ean = ean
    self.asin = asin
    if status is None:
      self.status = Identifier.NEW
    else:
      self.status = status
    if updated is None:
      self.updated = timestamp()
    else:
      self.updated = updated
    self.title = title

  def __str__(self):
    return ('Identifier(asin={a}, ean={e}, status={s}, title={t})'
            .format(a=self.asin, e=self.ean, s=self.status, t=self.title))

  @staticmethod
  def from_obj(obj):
    assert obj is not None
    if Identifier.OBJ_STATUS not in obj:
      status = Identifier.NEW
    else:
      status = obj[Identifier.OBJ_STATUS]
    if Identifier.OBJ_UPDATED not in obj:
      updated = timestamp()
    else:
      updated = obj[Identifier.OBJ_UPDATED]
    if Identifier.OBJ_TITLE not in obj:
      title = None
    else:
      title = obj[Identifier.OBJ_TITLE]
    return Identifier(ean=obj[Identifier.OBJ_EAN],
                      asin=obj[Identifier.OBJ_ASIN],
                      status=status,
                      updated=updated,
                      title=title)

  @staticmethod
  def filter_asin(asin):
    assert isinstance(asin, str)
    return {
      Identifier.OBJ_ASIN: asin
    }

  @staticmethod
  def filter_ean(ean):
    assert isinstance(ean, str)
    return {
      Identifier.OBJ_EAN: ean
    }

  @staticmethod
  def filter_intersection(ean=None, asin=None):
    assert ean is not None or asin is not None
    filters = []
    if ean is not None:
      filters.append(Identifier.filter_ean(ean=ean))
    if asin is not None:
      filters.append(Identifier.filter_asin(asin=asin))
    assert len(filters) > 0
    if len(filters) == 1:
      return filters[0]
    else:
      return {'$or': filters}

  @staticmethod
  def extend(a, b):
    if b.status == Identifier.SUCCESS:
      # SUCCESS, SUCCESS
      # FAILED , SUCCESS
      # NEW    , SUCCESS
      status = Identifier.SUCCESS
    elif a.status == Identifier.SUCCESS:
      # SUCCESS, FAILED
      # SUCCESS, NEW
      a, b = b, a
      status = Identifier.SUCCESS
    elif a.status == Identifier.FAILED and b.status == Identifier.FAILED:
      # FAILED , FAILED
      status = Identifier.FAILED
    elif b.status == Identifier.NEW:
      # FAILED , NEW
      # NEW    , NEW
      status = Identifier.NEW
    elif a.status == Identifier.NEW:
      # NEW    , FAILED
      status = b.status
      a, b = b, a
    ean = b.ean or a.ean
    asin = b.asin or a.asin
    title = b.title or a.title
    updated = max(b.updated, a.updated)
    return Identifier(asin=asin, ean=ean,
                      status=status, title=title, updated=updated)
                        

  def to_obj(self):
    return {
      Identifier.OBJ_EAN: self.ean,
      Identifier.OBJ_ASIN: self.asin,
      Identifier.OBJ_STATUS: self.status,
      Identifier.OBJ_UPDATED: self.updated,
      Identifier.OBJ_TITLE: self.title
    }

  def asin_available(self):
    if self.status == Identifier.SUCCESS:
      return self.asin
    else:
      return None

  def ean_available(self):
    if self.status == Identifier.SUCCESS:
      return self.ean
    else:
      return None

def timestamp():
  return datetime.datetime.now().timestamp()

