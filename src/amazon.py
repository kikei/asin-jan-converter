import getopt
import logging

from classes.Cache import Cache
from models import Models
from services.AmazonScraper import AmazonScraper
from utils.common import get_db_instance, get_amazon_scraping_proxy, get_logger

class AmazonSearch(object):
  def __init__(self, logger=None):
    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger
    # Model
    db = get_db_instance()
    models = Models(db)
    model_caches = models.getCaches()
    # Proxy
    proxies = get_amazon_scraping_proxy()
    # Run
    self.amazon_scraper = AmazonScraper(cache=model_caches, proxies=proxies,
                                        logger=self.logger)

  def get_product_by_asin(self, asin):
    result = self.amazon_scraper.get_product(asin)
    return result

  def find_asin(self, query):
    result = self.amazon_scraper.get_asin(query)
    return result

def usage():
  script = 'main.py amazon'
  print('''{script} [-h|-p|-a] [-Q <query>|-A <asin>]

Options:
  -h, --help                   Display this help.
  -p, --product                Show product data.
  -a, --asin                   Show related ASIN codes.
  -Q <query>, --query=<query>  Search by given query.
  -A <asin>, --asin=<asin>     Find product page of given asin code.
  -v, --verbose                Display verbose log.
'''.format(script=script))

def exit_usage():
  usage()
  exit(1)

def get_options(argv):
  command = None
  options = {
    'verbose': False
  }
  try:
    opts, args = getopt.getopt(argv, 'hpaQ:A:v',
                               ['help',
                                'product',
                                'asin',
                                'query=',
                                'asin=',
                                'verbose'])
    for o, a in opts:
      if o in ['-h', '--help']:
        exit_usage()
      elif o in ['-p', '--product']:
        command = 'product'
      elif o in ['-a', '--asin']:
        command = 'asin'
      elif o in ['-Q', '--query=']:
        options['query'] = a
      elif o in ['-A', '--asin=']:
        options['asin'] = a
      elif o in ['-v', '--verbose']:
        options['verbose'] = True
      else:
        print('Unsupported option: {option}.'.format(option=o))
        exit_usage()
    if command is None:
      print('Command must be given.')
      exit_usage()
    return command, options
  except getopt.GetoptError as e:
    print(e)
    exit_usage()

def get_product_by_asin(asin, logger):
  amazon = AmazonSearch(logger=logger)
  product = amazon.get_product_by_asin(asin)
  print(product)

def get_asin_by_query(query, logger):
  amazon = AmazonSearch(logger=logger)
  product = amazon.find_asin(query)
  print(product)


def main(argv):
  command, options = get_options(argv)
  logger = get_logger(log_name='webapp.log', verbose=options['verbose'])
  if command == 'product':
    if 'query' in options:
      print('Not supported.')
    elif 'asin' in options:
      get_product_by_asin(options['asin'], logger)
    else:
      print('Either of Query or ASIN must be given.')
  elif command == 'asin':
    if 'query' in options:
      get_asin_by_query(options['query'], logger)
    elif 'asin' in options:
      print('Not supported.')
    else:
      print('Either of Query or ASIN must be given.')
  else:
    print('Invalid option.')
    exit_usage()

