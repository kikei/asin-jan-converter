import getopt
import sys

import jancode
import amazon
import yahoo
import cache
import identifiers

def usage():
  script = 'main.py'
  print('''Usage: {script} [options] <command> [<args>]

Options:
  -h, --help   Display this help.

Following commands are supported. See {script} <command> --help to show more detail.
  amazon       Get items on amazon.co.jp.
  yahoo        Get items on yahoo.co.jp.
  jancode      Get JAN code.
  cache        Control cache.
  id           List identifiers.

'''.format(script=script))

def exit_usage():
  usage()
  exit(1)

def get_options(argv):
  try:
    opts, args = getopt.getopt(argv, 'h', ['help'])
    for o, a in opts:
      if o in ['-h', '--help']:
        exit_usage()
      else:
        print('Unsupported option: {option}.'.format(option=o))
        exit_usage()
    if len(args) == 0:
      print('Command is required.')
      exit_usage()
    command = args.pop(0)
    options = {
      'command': command
    }
    return options, args
  except getopt.GetoptError as e:
    print(e)
    exit_usage()

def main(argv):
  options, args = get_options(argv)
  command = options['command']
  if command == 'amazon':
    amazon.main(args)
  elif command == 'yahoo':
    yahoo.main(args)
  elif command == 'jancode':
    jancode.main(args)
  elif command == 'cache':
    cache.main(args)
  elif command == 'id':
    identifiers.main(args)


if __name__ == '__main__':
  main(sys.argv[1:])
