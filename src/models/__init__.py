from .Caches import Caches
from .Identifiers import Identifiers

class Models(object):
  def __init__(self, mongo_client):
    self.db_cache = mongo_client.cache_db
    self.db_reseller = mongo_client.reseller_db
    self.model_caches = None
    self.model_identifiers = None

  def getCaches(self):
    if self.model_caches is not None:
      return self.model_caches
    else:
      model = Caches(self.db_cache.caches)
      self.model_caches = model
      return model

  def getIdentifiers(self):
    if self.model_identifiers is not None:
      return self.mode_identifiers
    else:
      model = Identifiers(self.db_reseller.identifiers)
      self.model_identifiers = model
      return model
