import getopt

from classes.Cache import Cache
from models import Models
from services.YahooShopping import YahooShopping
from utils.common import get_db_instance, get_yahoo_appid

def usage():
  script = 'main.py yahoo'
  print('''{script} [-s] [-h|-Q <query>]

Options:
  -h, --help                   Display this help.
  -s, --search                 Search items.
  -Q <query>, --query=<query>  Search goods by given query.
'''.format(script=script))

def exit_usage():
  usage()
  exit(1)

def get_options(argv):
  command = 'search'
  options = {}
  try:
    opts, args = getopt.getopt(argv, 'hsQ:',
                               ['help',
                                'search',
                                'query='])
    for o, a in opts:
      if o in ['-h', '--help']:
        exit_usage()
      elif o in ['-s', '--search']:
        command = 'search'
      elif o in ['-Q', '--query=']:
        options['query'] = a
      else:
        print('Unsupported option: {option}.'.format(option=o))
        exit_usage()
    if command == 'search' and \
       ('query' not in options or options['query'] == ''):
      print('Query must given.')
      exit_usage()
    return command, options
  except getopt.GetoptError as e:
    print(e)
    exit_usage()

def search(query):
  assert isinstance(query, str)
  # Model
  db = get_db_instance()
  models = Models(db)
  model_caches = models.getCaches()
  # Yahoo shopping API
  appid = get_yahoo_appid()
  assert appid is not None
  # Run
  y = YahooShopping(appid=appid, cache=model_caches)
  content = y.query(query=query, ignoreCache=False)
  print(content)


def main(argv):
  command, options = get_options(argv)
  if command == 'search':
    search(options['query'])
  else:
    print('Invalid options.')
    exit_usage()


