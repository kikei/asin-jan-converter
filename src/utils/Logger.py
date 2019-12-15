import logging
import os

#logging.getLogger('requests').setLevel(logging.ERROR)

LOG_FORMAT_DEFAULT = '%(asctime)s [%(levelname)s] %(message)s'

def get_logger(base_level=logging.WARN,
               stream_level=None,
               file_level=logging.INFO,
               file_path=None,
               format=None):
  # Build formatter
  if format is None:
    format = LOG_FORMAT_DEFAULT
  formatter = logging.Formatter(format)
  # Base logger
  logger = logging.getLogger()
  logger.setLevel(base_level)
  # Logging to console
  stream_handler = get_stream_handler(level=stream_level, formatter=formatter)
  if stream_handler is not None:
    logger.addHandler(stream_handler)
  # Logging to log file
  file_handler = get_file_handler(path=file_path, level=file_level,
                                  formatter=formatter)
  if file_handler is not None:
    logger.addHandler(file_handler) 
  return logger

def get_stream_handler(level=None, formatter=None):
  if level is None:
    return None
  handler = logging.StreamHandler()
  handler.setLevel(level)
  if formatter is not None:
    handler.setFormatter(formatter)
  return handler

def get_file_handler(path=None, level=None, formatter=None):
  if path is None or level is None:
    return None
  from logging.handlers import RotatingFileHandler
  mkdir(path)
  handler = RotatingFileHandler(filename=path,
                                maxBytes=1024 * 1024, backupCount=9)
  handler.setLevel(level)
  if formatter is not None:
    handler.setFormatter(formatter)
  return handler

def mkdir(logfile):
  from pathlib import Path
  dirname = os.path.dirname(logfile)
  if not os.path.exists(dirname):
    path = Path(dirname)
    path.mkdir(parents=True)
