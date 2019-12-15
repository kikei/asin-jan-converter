import datetime
import getopt

from models import Models
from classes.Identifier import Identifier

from utils.common import get_db_instance

def list_identifiers(status=[], first=0, max_size=0, order_by=None):
  db = get_db_instance()
  models = Models(db)
  model_identifiers = models.getIdentifiers()
  items = model_identifiers.all(status=status, skip=first, limit=max_size,
                                order_by=('updated', 1))
  i = 0
  def show(x, alt, f=lambda a:a):
    return f(x) if x is not None else alt
  def isodate(t):
    return datetime.datetime.fromtimestamp(t).isoformat()
  for item in items:
    ean = show(item.ean, '-')
    asin = show(item.asin, '-')
    status = show(item.status, '-', str)
    updated = show(item.updated, '-', isodate)
    print('#{i}\tasin:{asin}\tean:{ean}\tstatus:{status}\tupdated:{updated}'
          .format(i=i, asin=asin, ean=ean, status=status, updated=updated))
    i += 1

def usage():
  script = 'main.py identifiers'
  print('''{script} [options]

Options:
  -h, --help                      Display this help.
  -l, --list                      List identifiers.
  -s [0,1,2] --status=[0,1,2]     Select items with given status.
  -f <N>, --first=<N>             Skip first N items.
  -m <N>, --max=<M>               Limit the number of items to select.
  -o <key:direction>              Sort items by key for the direction.
  -v, --verbose                   Display verbose log.
'''.format(script=script))

def exit_usage():
  usage()
  exit(1)

def get_options(argv):
  command = None
  options = {
    'status': [],
    'first': None,
    'max': 100,
    'verbose': False
  }
  try:
    opts, args = getopt.getopt(argv, 'hls:f:m:',
                               ['help',
                                'list',
                                'status=',
                                'first=',
                                'max=',
                                'order='])
    for o, a in opts:
      if o in ['-h', '--help']:
        exit_usage()
      elif o in ['-l', '--list']:
        command = 'list'
      elif o in ['-s', '--status']:
        options['status'] = [int(t) for t in a.split(',')]
      elif o in ['-f', '--first']:
        option['first'] = int(a)
      elif o in ['-m', '--max=']:
        options['max'] = int(a)
      elif o in ['-o', '--order=']:
        kv = a.split(':')
        if len(kv) != 2 or kv[1] not in ['asc', 'desc']:
          print('Order must be given by format of "<key>:[asc,desc]".')
          exit_usage()
        options['order'] = k, (+1 if kv[1] == 'asc' else -1)
      else:
        print('Unsupported option: {option}.'.format(option=o))
        exit_usage()
  except getopt.GetoptError as e:
    print(e)
    exit_usage()
  if command is None:
    print('Command is required.')
    exit_usage()
  return command, options

def main(argv):
  command, options = get_options(argv)
  if command == 'list':
    list_identifiers(status=options['status'],
                     first=options['first'],
                     max_size=options['max'])
  else:
    print('Invalid options.')
    exit_usage()

