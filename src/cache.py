import getopt
from signal import signal, SIGPIPE, SIG_DFL

from classes.Cache import Cache
from models import Models
from utils.common import get_db_instance

class CacheControl(object):
  def __init__(self):
    db = get_db_instance()
    models = Models(db)
    self.model_caches = models.getCaches()

  def load_cache(self, key):
    return self.model_caches.load(key)

  def delete_cache(self, key):
    return self.model_caches.delete(key)


def usage():
  script = 'main.py cache'
  print('''{script} [options]

Options:
  -h, --help                  Display this help.
  -l, --load                  Load cache with key.
  -d, --delete                Delete cache with key.
  -k <key>, --key=<key>       Set key for cache item.
'''.format(script=script))

def exit_usage():
  usage()
  exit(1)

def get_options(argv):
  command = None
  options = {}
  try:
    opts, args = getopt.getopt(argv, 'hldk:',
                               ['help',
                                'load',
                                'delete',
                                'key='])
    for o, a in opts:
      if o in ['-h', '--help']:
        exit_usage()
      elif o in ['-l', '--load']:
        command = 'load'
      elif o in ['-d', '--delete']:
        command = 'delete'
      elif o in ['-k', '--key=']:
        options['key'] = a
      else:
        print('Unsupported option: {option}.'.format(option=o))
    if command is None:
      print('Command must be given.')
      exit_usage()
    return command, options
  except getopt.GetoptError as e:
    print(e)
    exit_usage()

def load_cache(key):
  cache = CacheControl()
  result = cache.load_cache(key)
  if result is None:
    print('No cache found.')
  else:
    content = result.data.decode('utf-8', errors='ignore')
    signal(SIGPIPE, SIG_DFL)
    print(content)

def delete_cache(key):
  cache = CacheControl()
  result = cache.delete_cache(key)
  print('Delete {result}.'.format(result='success' if result else 'failed'))


def main(argv):
  command, options = get_options(argv)
  if command == 'load':
    if 'key' not in options:
      print('Key must be given.')
      exit_usage()
    load_cache(options['key'])
  elif command == 'delete':
    if 'key' not in options:
      print('Key must be given.')
      exit_usage()
    delete_cache(options['key'])
  else:
    print('Invalid options.')
    exit_usage()
