#encoding:utf8
import base64
import random
from Crypto.Cipher import AES


def get_key(key_len=32,begin_char=33,end_char=126):
    """
    key_len 16 24 32
    生产随机key
    默认只用ascii的指定字符以实现可读
    """
    return "".join(map(lambda i : chr(random.randint(begin_char,end_char)) ,range(key_len)))


def aes_encrypt(data,key):  
    """
    加密
    """
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)    #在尾部补上字符指定补的长度
    cipher = AES.new(key)
    encrypted = cipher.encrypt(pad(data))  #aes加密
    result = base64.b64encode(encrypted)   #base64 encode
    return result


def aes_decrypt(en_data,key):
    """
    解密
    """
    unpad = lambda s : s[0:-ord(s[-1])]     #通过最后一个字符确定补的长度，截取获取原字符串
    cipher = AES.new(key)
    result2 = base64.b64decode(en_data)
    decrypted = unpad(cipher.decrypt(result2))
    return  decrypted
