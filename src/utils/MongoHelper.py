import pymongo

def build_address(hostname=None, port=None, username=None, password=None):
  # mongodb://{user}:{password}@{host}:{port}
  server = 'mongodb://'
  if username is not None:
    server += username
  if password is not None:
    server += ':{password}'.format(password=password)
    server += '@'
  server += hostname
  if port is not None:
    server += ':{port}'.format(port=port)
  return server

def get_instance(address):
  instance = pymongo.MongoClient(host=address)
  return instance

