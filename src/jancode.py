import getopt
import logging
import re
import time

from models import Models
from classes.Identifier import Identifier
from services.YahooShopping import YahooShopping
from services.AmazonScraper import AmazonScraper, AccessBlocked
from utils.common import get_db_instance, get_yahoo_appid, \
  get_amazon_scraping_proxy, get_logger

INTERVAL_AMAZON_REQUEST = 10

class JANCodeFinder(object):
  def __init__(self, logger=None):
    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger
    # Model
    db = get_db_instance()
    models = Models(db)
    model_caches = models.getCaches()
    self.model_identifiers = models.getIdentifiers()
    # Yahoo
    yahoo_appid = get_yahoo_appid()
    self.yahoo_api = YahooShopping(appid=yahoo_appid, cache=model_caches,
                                   logger=self.logger)
    # Amazon
    proxies = get_amazon_scraping_proxy()
    self.amazon_api = AmazonScraper(cache=model_caches, proxies=proxies,
                                    logger=self.logger)

  def yahoo_query(self, keyword):
    url = self.yahoo_api.build_query_url(query=keyword)
    content = self.yahoo_api.query(query=keyword)
    return content

  def keyword_to_jan(self, keyword):
    """
    Returns dictionary with guessed jan and accuracy.
    """
    xml = self.yahoo_query(keyword)
    counts = {}
    #root = ET.fromstring(xml)
    #for tag in root.iter('{urn:yahoo:jp:itemSearch}JanCode'):
      #if tag.text is not None:
      #  jan = tag.text
    for m in re.finditer(r'\D(\d{13})\D', xml):
      jan = m.group(1)
      if jan not in counts:
        counts[jan] = 0
      counts[jan] += 1
    unit = sum(counts.values())
    counts = counts.items()
    counts = sorted(counts, key=lambda x:-x[1])
    counts = [(k, v / unit) for k, v in counts]
    return counts

  def jan_to_asin(self, jan):
    """
    """
    result = self.amazon_api.get_asin(jan)
    asins = [i['asin'] for i in result['items']]
    return asins

  def asin_to_jan(self, asin, save_byproduct=True):
    """
    """
    # Return existing JAN if it has been paired with given asin.
    result = self.model_identifiers.load(asin=asin)
    if result.ean_available() is not None:
      jan = result.ean_available()
      self.logger.info('JAN found in storage, jan={j}.'.format(j=jan))
      return jan
    # Fetch JAN from Internet.
    product = self.amazon_api.get_product(asin)
    # JAN sometimes occurs in Amazon product page.
    assert 'jan' in product and 'title' in product
    if product['jan'] is not None and product['jan'] != '':
      jan = product['jan']
      self.logger.info('JAN found in product page, jan={j}.'.format(j=jan))
      save = Identifier(ean=jan, asin=asin,
                        status=Identifier.SUCCESS, title=product['title'])
      self.model_identifiers.save(save, extend=True)
      return jan
    # Use title for searching JAN codes in Yahoo Shopping.
    if product['title'] is None or product['title'] == '':
      self.logger.warn('No title found by the asin {asin}.'.format(asin=asin))
      return None
    name = product['title']
    jans = self.keyword_to_jan(name)
    found = []
    def save_id(**args):
      if save_byproduct:
        self.model_identifiers.save(Identifier(**args), extend=True)
    self.logger.debug('JANs={j}.'.format(j=jans))
    for jan, accuracy in jans:
      # Skip JAN as it has been found.
      if jan in found:
        continue
      # Use ASIN if it has been already paired with JAN.
      result = self.model_identifiers.load(ean=jan)
      if result is not None:
        asin_ = result.asin_available()
        if asin_ is not None and asin != asin_:
          found.append(jan)
          continue
      # Fetch ASIN code list by searching JAN in Amazon.
      self.logger.debug('Sleeping {s} seconds before requesting to Amazon.'
                        .format(s=INTERVAL_AMAZON_REQUEST))
      time.sleep(INTERVAL_AMAZON_REQUEST)
      # JAN code -> Amazon product list
      result = self.amazon_api.get_asin(jan)
      items = result['items']
      if len(items) == 0:
        save_id(ean=jan, status=Identifier.FAILED, title=name)
      elif len(items) == 1:
        save_id(ean=jan, asin=items[0]['asin'],
                status=Identifier.SUCCESS, title=items[0]['name'])
      else:
        for p in items:
          save_id(asin=p['asin'], status=Identifier.NEW, title=p['name'])
      self.logger.debug('Products for JAN {j}: {ps}.'.format(j=jan, ps=items))
      asins = [p['asin'] for p in items]
      if asin in asins:
        found.append(jan)
    # Found
    if len(found) == 0:
      save_id(asin=asin, status=Identifier.FAILED, title=name)
    elif len(found) == 1:
      save_id(ean=found[0], asin=asin, status=Identifier.SUCCESS, title=name)
    else:
      for e in found: save_id(ean=e, status=Identifier.NEW)
    return found

def search_by_query(query, logger):
  finder = JANCodeFinder(logger=logger)
  jans = finder.keyword_to_json(query)
  print(jans)

def search_by_asin(asin, logger):
  finder = JANCodeFinder(logger=logger)
  jans = finder.asin_to_jan(asin)
  print(jans)

def usage():
  script = 'main.py jancode'
  print('''{script} [options]

Options:
  -h, --help                   Display this help.
  -Q <query>, --query=<query>  Search JAN code by given query.
  -A <asin>, --asin=<asin>     Search JAN code by given ASIN code.
  -v, --verbose                Display verbose log.
'''.format(script=script))

def exit_usage():
  usage()
  exit(1)

def get_options(argv):
  options = {
    'verbose': False
  }
  try:
    opts, args = getopt.getopt(argv, 'hQA:v',
                               ['help',
                                'query=',
                                'asin=',
                                'verbose'])
    for o, a in opts:
      if o in ['-h', '--help']:
        exit_usage()
      elif o in ['-q', '--query']:
        options['query'] = a
      elif o in ['-A', '--asin=']:
        options['asin'] = a
      elif o in ['-v', '--verbose']:
        options['verbose'] = True
      else:
        print('Unsupported option: {option}.'.format(option=o))
        exit_usage()
    return options
  except getopt.GetoptError as e:
    print(e)
    exit_usage()

def main(argv):
  options = get_options(argv)
  logger = get_logger(log_name='webapp.log', verbose=options['verbose'])
  if 'query' in options:
    search_by_query(options['query'], logger)
  elif 'asin' in options:
    try:
      search_by_asin(options['asin'], logger)
    except AccessBlocked as e:
      print('Error access blocked by Amazon: {e}.'.format(e=e))
      exit(1)
  else:
    print('Invalid options.')
    exit_usage()

