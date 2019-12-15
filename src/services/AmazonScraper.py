import datetime
import logging
import random
import re
import requests
import urllib.parse
from classes.Cache import Cache
from lxml import html

AMAZON_PRODUCT_URL_TEMPLATE = 'https://www.amazon.co.jp/{asin}/dp/{asin}'
AMAZON_SEARCH_URL_TEMPLATE = 'https://www.amazon.co.jp/s'

# List of default Accept values - HTTP | MDN
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Content_negotiation/List_of_default_Accept_values
HTTP_HEADER_LIST = {
  'ACCEPT': [
    'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'image/jpeg, application/x-ms-application, image/gif, application/xaml+xml, image/pjpeg, application/x-ms-xbap, application/x-shockwave-flash, application/msword, */*',
    'text/html, application/xhtml+xml, image/jxr, */*',
    'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1'
  ],
  'ACCEPT_ENCODING': [
    'gzip, deflate'
  ],
  'DNT': [
    None, '0', '1'
  ],
  'USER-AGENT': [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox One) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 Edge/40.15063.0',
    'Mozilla/5.0 (Windows Mobile 10; Android 8.0.0; Microsoft; Lumia 950XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36 Edge/40.15254.369',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136',
    'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
  ]
}

def get_random_http_headers():
  headers = {}
  for key in HTTP_HEADER_LIST:
    values = HTTP_HEADER_LIST[key]
    i = random.randint(0, len(values) - 1)
    v = values[i]
    if v is not None:
      headers[key] = v
  return headers

class AccessBlocked(Exception):
  pass

class AmazonScraper(object):
  def __init__(self, cache=None, http_headers=None, proxies=None, logger=None):
    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger
    # Cache engine
    if cache is not None:
      assert cache.save is not None
      assert cache.load is not None
    self.cache = cache
    if self.cache is not None:
      self.logger.debug('AmazonScraper use cache engine.')
    if http_headers is None:
      self.http_headers = {}
    else:
      self.http_headers = http_headers
    # Proxy
    self.proxies = proxies
    if self.proxies is not None:
      self.logger.debug('AmazonScraper use proxy {p}.'.format(p=self.proxies))

  @staticmethod
  def build_cache_key(url=None):
    if isinstance(url, str):
      return 'amazon_{url}'.format(url=url)

  @staticmethod
  def get_product_url(asin, extra=False):
    if extra:
      return AMAZON_PRODUCT_URL_TEMPLATE.format(asin=asin) + \
        '/ref=sr_1_1?__mk_ja_JP=カタカナ&keywords={asin}'.format(asin=asin)
    else:
      return AMAZON_PRODUCT_URL_TEMPLATE.format(asin=asin)

  @staticmethod
  def get_search_url(query, extra=False):
    if extra:
      extras = {
        '__mk_ja_JP': 'カタカナ',
        'ref': 'nb_sb_noss'
      }
    else:
      extras = {}
    qs = {
      'k': query,
      **extras
    }
    q = urllib.parse.urlencode(qs)
    return AMAZON_SEARCH_URL_TEMPLATE + '?' + q

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

  def test_request(self, url):
    # Use to check if request is configured expectedly.
    headers = {
      **get_random_http_headers(),
      **self.http_headers
    }
    r = requests.get(url, headers=headers, proxies=self.proxies)
    content = r.content
    return content.decode('utf-8', errors='ignore')


  def fetch_cached(self, url, cache_key, ignore_cache=False):
    assert url is not None
    assert cache_key is not None
    content = None
    if self.cache is not None and not ignore_cache:
      # Try to load data from cache when it's enabled.
      content = self.load_cache(cache_key)
      if content is not None:
        self.logger.debug('Cache HIT during Amazon scraping, key={key}.'
                          .format(key=cache_key))
    if content is None or ignore_cache:
      headers = {
        **get_random_http_headers(),
        **self.http_headers
      }
      self.logger.info('Fetching amazon page url={u}, headers={h}...'
                       .format(u=url, h=headers))
      r = requests.get(url, headers=headers, proxies=self.proxies)
      self.logger.info(('Finished to fetch amazon page url={u}, ' +
                        'status={c}, encoding={e}, headers={h}.')
                       .format(u=url, c=r.status_code, e=r.encoding,
                               h=r.headers))
      try:
        r.raise_for_status()
      except requests.exceptions.HTTPError as e:
        self.logger.warn(('Error status was returned from Amazon, ' +
                          'url={u}, headers={h}...')
                         .format(u=url, h=headers))
        raise AccessBlocked('Failed to get page, url={u}, cache_key={c}.'
                            .format(u=url, c=cache_key))

      if scraping_blocked(r.content):
        self.logger.warn('Failed to fetch page, url={u}, headers={h}...'
                         .format(u=url, h=headers))
        raise AccessBlocked('Failed to get page, url={u}, cache_key={c}.'
                            .format(u=url, c=cache_key))
      content = r.content
      if self.cache is not None:
        # Save response to cache when it's enabled.
        success = self.save_cache(cache_key, content)
        self.logger.debug(('Saved response from Amazon ' +
                           'as cache "{key}": success={ok}.')
                          .format(key=cache_key, ok=(success is not None)))
    return content.decode('utf-8', errors='ignore')

  def fetch_product(self, asin, ignore_cache=False):
    url = AmazonScraper.get_product_url(asin, extra=True)
    url_plain = AmazonScraper.get_product_url(asin)
    cache_key = AmazonScraper.build_cache_key(url_plain)
    content = self.fetch_cached(url, cache_key, ignore_cache=ignore_cache)
    return content

  def fetch_search(self, query, ignore_cache=False):
    url = AmazonScraper.get_search_url(query, extra=True)
    url_plain = AmazonScraper.get_search_url(query)
    cache_key = AmazonScraper.build_cache_key(url_plain)
    content = self.fetch_cached(url, cache_key, ignore_cache=ignore_cache)
    return content

  def get_product(self, asin, **args):
    url = AmazonScraper.get_product_url(asin)
    content = self.fetch_product(asin, **args)
    parser = html.fromstring(content)
    product_title = HTMLParser.either([
      (HTMLParser.text, parser.xpath('//*[@id="productTitle"]/text()')),
      (HTMLParser.text, parser.xpath('//*[@id="title"]/text()'))
    ])
    manufacturer = parser.xpath('//*[@id="bylineInfo"]/text()')
    amazon_price = parser.xpath('//*[@id="priceblock_ourprice"]/text()')
    categories = parser.xpath('//*[@id="wayfinding-breadcrumbs_feature_div"]//a/text()')
    description = parser.xpath('//*[@id="productDescription"]//*/text()')
    images_found = re.findall(r'"thumb":"([^"]+)","large":"([^"]+)"', content)
    # Search JAN code
    jan = parser.xpath('//b[contains(text(), " JAN")]/../text()')
    jan = HTMLParser.text(jan)
    if jan is not None:
      jan = extract_jancode(HTMLParser.text(jan))
    # Search images
    images = [
      {'thumb': m[0], 'large': m[1]} for m in images_found
    ]
    return {
      'title': product_title,
      'manufacturer': HTMLParser.text(manufacturer),
      'description': HTMLParser.text(description),
      'images': images,
      'amazon_price': {
        'currency': 'JPY',
        'value': HTMLParser.number(amazon_price)
      },
      'categories': [HTMLParser.text(a) for a in categories],
      'asin': asin,
      'url': url,
      'code': asin,
      'instock': 1,
      'jan': jan
    }

  def get_asin(self, query, **args):
    assert isinstance(query, str) and query != ''
    url = AmazonScraper.get_search_url(query)
    content = self.fetch_search(query, **args)
    parser = html.fromstring(content)
    divs = parser.xpath('//*[@data-asin]')
    items = []
    for div in divs:
      asin = div.xpath('@data-asin')
      name = div.xpath('.//img[@alt]/@alt')
      items.append({
        'asin': HTMLParser.text(asin),
        'name': HTMLParser.text(name)
      })
    return {
      'url': url,
      'items': items 
    }

class HTMLParser:
  @staticmethod
  def either(xs):
    for f, x in xs:
      y = f(x)
      if y != '':
        return y
    return None

  @staticmethod
  def text(x):
    if isinstance(x, list):
      if len(x) == 0:
        return ''
      elif isinstance(x[0], str):
        return ''.join(x).strip()
      else:
        return [HTMLParser.text(a) for a in x]
    else:
      return ''.join(x).strip()

  def number(x):
    x = ''.join(x).strip()
    x = ''.join(re.findall('(\d+)', x))
    try:
      n = int(x)
      return n
    except ValueError as e:
      return None
    

def scraping_blocked(content):
  return (b'Amazon CAPTCHA' in content or
          b'To discuss automated access' in content)

def extract_jancode(text):
  pattern = re.compile(r'(\d{13})')
  m = pattern.search(text)
  if m is None:
    return None
  return m.group()

