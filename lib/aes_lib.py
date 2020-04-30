#encoding:utf8
import base64
import random
from Crypto.Cipher import AES

class AesCrypt(object):
    def __init__(self):
        self.iv=self.get_key(16)
        self.key=self.get_key()

    @staticmethod
    def get_key(key_len=32,begin_char=33,end_char=126):
        """
        key_len 16 24 32
        生产随机key
        默认只用ascii的指定字符以实现可读
        """
        return ("".join(map(lambda i : chr(random.randint(begin_char,end_char)) ,range(key_len)))).encode('latin1') 


    def aes_encrypt(self,data,key,mode=AES.MODE_CBC,iv=""):  
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


    def aes_decrypt(self,en_data,key,mode=AES.MODE_CBC,iv=None):
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

    #如果配置密钥配置文件存在，从配置文件获取key和iv，否则自动生成并设置配置文件
    def set_config(self,file_key):
        #从配置文件读
        self.key="yyyyyyyyyyyy"    
        self.iv="xxx"  

        if len(self.iv) !=16 or (len(self.key) not in [16,24,32]):
            _key=aes_crypt.key
            _iv=aes_crypt.iv 
            #写配置文件

#单例子模式
aes_crypt=AesCrypt()


if __name__ == "__main__":
    data=b"xxx"
    ac=AesCrypt()
    en_data=ac.aes_encrypt(data,ac.key,AES.MODE_ECB)
    print(en_data)
    
    ac.aes_decrypt(en_data,ac.key,AES.MODE_ECB)

if __name__ == "__main__":
    data=b"xxx"
    ac=AesCrypt()
    """
    ac.key=
    ac.iv=
    """
    en_data=ac.aes_encrypt(data,ac.key,iv=ac.iv)
    print(en_data)
    ac.aes_decrypt(en_data,ac.key,iv=ac.iv)

if __name__ == "__main__":
    aes_crypt.set_config("/tmp/key.conf")
    print(aes_crypt.key, aes_crypt.iv)