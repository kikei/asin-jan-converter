import sys
sys.path.append('..')

import os
import utils.MongoHelper as MongoHelper
import utils.Logger as Logger
import logging

def get_db_instance():
  mongo_hostname = os.environ['MONGO_HOSTNAME']
  mongo_username = os.environ['MONGO_USERNAME']
  mongo_password = os.environ['MONGO_PASSWORD']
  if 'MONGO_PORT' in os.environ:
    mongo_port = os.environ['MONGO_PORT']
  else:
    mongo_port = '27019'
  db_address = MongoHelper.build_address(hostname=mongo_hostname,
                                         username=mongo_username,
                                         password=mongo_password)
  db = MongoHelper.get_instance(db_address)
  return db

def get_yahoo_appid():
  return os.environ['YAHOO_APP_ID']

def get_amazon_scraping_proxy():
  addr = os.environ['AMAZON_SCRAPE_PROXY']
  return {
    'http': addr,
    'https': addr
  }

def get_logger(log_name, verbose=False):
  log_dir = os.environ['LOG_DIR']
  log_path = os.path.join(log_dir, log_name)
  if verbose:
    stream_level = logging.DEBUG
  else:
    stream_level = logging.INFO
  file_level = logging.DEBUG
  return Logger.get_logger(base_level=stream_level,
                           stream_level=stream_level,
                           file_level=file_level,
                           file_path=log_path)



