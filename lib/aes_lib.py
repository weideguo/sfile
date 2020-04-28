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
    return ("".join(map(lambda i : chr(random.randint(begin_char,end_char)) ,range(key_len)))).encode('latin1') 


def aes_encrypt(data,key,mode=AES.MODE_CBC,iv=""):  
    """
    加密
    """
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS).encode('latin1')    #在尾部补上字符指定补的长度
    if mode==AES.MODE_ECB:
        cipher = AES.new(key, mode)
    else:
        cipher = AES.new(key, mode, iv)
    encrypted = cipher.encrypt(pad(data))  #aes加密
    result = base64.b64encode(encrypted)   #base64 encode
    return result


def aes_decrypt(en_data,key,mode=AES.MODE_CBC,iv=None):
    """
    解密
    """
    #通过最后一个字符确定补的长度，截取获取原字符串
    def unpad(s):
        try:
            return s[0:-ord(s[-1])] 
        except:
            return s[0:-s[-1]]
    if mode==AES.MODE_ECB:
        cipher = AES.new(key, mode)
    else:
        cipher = AES.new(key, mode, iv)
    result2 = base64.b64decode(en_data)
    decrypted = unpad(cipher.decrypt(result2))
    return  decrypted


if __name__ == "__main__":
    data=b"xxx"
    key=get_key()
    en_data=aes_encrypt(data,key,AES.MODE_ECB)
    print(en_data)
    
    aes_decrypt(en_data,key,AES.MODE_ECB)

if __name__ == "__main__":
    #iv=b"1234567890123456"
    iv=get_key(16)
    data=b"xxx"
    key=get_key()
    en_data=aes_encrypt(data,key,iv=iv)
    print(en_data)
    aes_decrypt(en_data,key,iv=iv)
