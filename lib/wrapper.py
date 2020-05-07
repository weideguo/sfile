#coding:utf8
import os
from traceback import format_exc

from .logger import logger_err
from .aes_lib import AesCrypt
from .rsa_lib import RsaCrypt


def error_capture(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger_err.error(format_exc())
        
    return _wrapper


def get_aes_crypt(sc):
    """
    获取aes加密对象
    如果配置文件存在key/iv，则使用；否则新生成
    """
    aes_crypt=AesCrypt()
    #初始化加密对象的key iv
    #需要为byte格式
    _key=sc.read("key").encode("utf8") 
    _iv=sc.read("iv").encode("utf8") 
    if aes_crypt.is_valid(_key,_iv):
        #从配置文件读取的key有效
        aes_crypt.key = _key
        aes_crypt.iv = _iv
    else:
        #从配置文件读取的key无效，生成key并回写
        _key=aes_crypt.key
        _iv=aes_crypt.iv
        sc.write("key",_key.decode("utf8"))
        sc.write("iv",_iv.decode("utf8"))
    
    return aes_crypt,_key,_iv


def get_rsa_crypt(sc):
    """
    获取rsa加密对象
    如果配置文件存在私钥/公钥，则使用；否则新生成
    """
    rsa_crypt=RsaCrypt()
    
    def set_key_file(key_name,key_default,file_content):
        _key=sc.read(key_name)
        if not _key:
            _key=key_default
            sc.write(key_name,key_default)

        _key=os.path.join(sc.path,_key)
        _path=os.path.dirname(_key)
        if not os.path.exists(_path):
            os.makedirs(_path)

        try:
            if key_name=="private_key":
                rsa_crypt.private_key = open(_key,"rb").read()
            else:
                rsa_crypt.public_key = open(_key,"rb").read()
        except:
            with open(_key,"wb") as f:
                f.write(file_content)
        
        return _key
    
    _private_key=set_key_file("private_key","rsa/key.pem",rsa_crypt.private_key)
    _public_key=set_key_file("public_key","rsa/key.pub",rsa_crypt.public_key)
    
    return rsa_crypt,_private_key,_public_key