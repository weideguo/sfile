#coding:utf8

from traceback import format_exc

from .logger import logger_err


def error_capture(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger_err.error(format_exc())
        
    return _wrapper
