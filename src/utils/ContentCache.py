class ContentCache(object):
  def __init__(self, cache_dir):
    assert isinstance(cahce_dir, str)
    self.cache_dir = cache_dir

  def save(self, key, content):
    assert isinstance(key, str)
    assert isinstance(content, str)
    with open


