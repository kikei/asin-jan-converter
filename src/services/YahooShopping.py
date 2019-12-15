import logging
import sys
sys.path.append('..')

import datetime
import requests
import urllib.parse

from classes.Cache import Cache

URL_ITEM_SEARCH = 'https://shopping.yahooapis.jp/ShoppingWebService/V1/itemSearch'

"""
curl -v -A 'Yahoo AppID {appId}' 'https://shopping.yahooapis.jp/ShoppingWebService/V1/itemSearch?appid={appid}&query=%E3%83%AC%E3%82%B4+%28LEGO%29+%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%BB%E3%82%A6%E3%82%A9%E3%83%BC%E3%82%BA+%E3%83%8A%E3%83%96%E3%83%BC%E3%83%BB%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%95%E3%82%A1%E3%82%A4%E3%82%BF%E3%83%BC+75092'
"""

class YahooShopping(object):
  def __init__(self, appid, cache=None, logger=None):
    assert appid is not None
    if cache is not None:
      assert cache.save is not None
      assert cache.load is not None
    self.cache = cache
    self.appid = appid
    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger

  @staticmethod
  def build_cache_key(query=None):
    if isinstance(query, str):
      return 'yahooshopping_query={k}'.format(k=query)
    return 'yahooshopping'


  def build_query_url(self, query,
                      type=None, hits=None, offset=None, sort=None):
    assert isinstance(query, str)
    if type is not None:
      assert isinstance(type, str) and type in ['all', 'any']
    if hits is not None:
      assert isinstance(hits, int) and hits < 51
    if offset is not None:
      assert isinstance(offset, int) and offset >= 0
    if sort is not None:
      assert isinstance(sort, str) and sort in ['price', 'score', 'review_count']
    url_base = URL_ITEM_SEARCH
    q = {
      'appid': self.appid
    }
    q['query'] = query
    if type is not None:
      q['type'] = type
    if hits is not None:
      q['hits'] = hits
    if offset is not None:
      q['offset'] = offset
    if sort is not None:
      q['sort'] = sort
    qs = urllib.parse.urlencode(q)
    url = url_base + '?' + qs
    return url

  def load_cache(self, key):
    assert self.cache is not None
    c = self.cache.load(key)
    if c is None:
      return None
    else:
      return c.data

  def save_cache(self, key, data):
    assert self.cache is not None
    assert isinstance(key, str)
    assert isinstance(data, bytes)
    c = Cache(key=key, data=data,
              date_updated=datetime.datetime.now().timestamp())
    success = self.cache.save(c)
    return success

  def query(self, query, ignoreCache=False, **args):
    content = None
    if self.cache is not None and not ignoreCache:
      # Try to load data from cache when it's enabled.
      cache_key = YahooShopping.build_cache_key(query)
      content = self.load_cache(cache_key)
      if content is None:
        self.logger.debug('Cache HIT during YahooShopping search, key={k}.'
                          .format(k=cache_key))
    if content is None or ignoreCache:
      # Request search
      url = self.build_query_url(query, **args)
      headers = {
        'User-Agent': 'Yahoo AppID {appid}'.format(appid=self.appid)
      }
      r = requests.get(url, headers=headers)
      content = r.content
      if self.cache is not None:
        # Save response to cache when it's enabled.
        cache_key = YahooShopping.build_cache_key(query)
        success = self.save_cache(cache_key, content)
        self.logger.debug(('Saved response from YahooShopping query ' +
                           'as cache "{key}": success={ok}.')
                          .format(key=cache_key, ok=(success is not None)))
    return content.decode('utf-8', errors='ignore')

    
    
