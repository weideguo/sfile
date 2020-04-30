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


def encrypt_send(sock,data):
    """
    加密传输
    文件的加密每次加密1024字节，然后传输   分块数\r\n\密文长度\r\n密文\r\n ... 密文长度\r\n密文\r\n
    """
    pass




def decrypt_recv(sock):
    """
    获取数据并解密
    """
    pass