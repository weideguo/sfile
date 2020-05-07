#coding:utf8
import Crypto.Hash.SHA1
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash.SHA1 import digest_size


class RsaCrypt(object):
    """
    RSA 加密/解密
    openssl genrsa -out key.pem                  #私钥
    openssl rsa -in key.pem -pubout > key.pub    #公钥
    """

    def __init__(self,key_len=2048,hashAlgo=Crypto.Hash.SHA1):
        """
        默认使用sha1
        """
        self.hashAlgo=hashAlgo
        
        hLen=self.hashAlgo.digest_size
        
        #key_len 1024 / 2048 / 3072
        self.key_len=key_len
        #明文最大长度 7.1.1 in RFC3447
        # k - 2 * hLen - 2
        self.max_plain=int(key_len/8) - 2*hLen - 2
        
        self.private_key, self.public_key = self.get_key()

        #密文长度的占位数，如果不够，则在前面补0
        self.len_len=3


    def get_key(self):
        """
        生成公钥和私钥
        """
        key = RSA.generate(self.key_len)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key,public_key


    def encrypt(self,data):
        """
        加密
        传入byte格式
        """
        public_key = RSA.import_key(self.public_key)
        cipher = PKCS1_OAEP.new(public_key,hashAlgo=self.hashAlgo)
        
        def assemble(data):
            """
            加密并组装成制定格式
            data 明文
            len_len 密文长度的长度，如256则为3位
            """
            _en_data=cipher.encrypt(data)
            
            _len=str(len(_en_data)).encode("latin1")
            _len_info=b"0"*(self.len_len-len(_len))+_len
            return _len_info+_en_data

        en_data=b""
        while True:
            _len=len(data)
            if _len <= self.max_plain:
                """
                用\r\n填充可能不安全
                en_data = en_data+b"\r\n"+cipher.encrypt(data)
                """
                en_data = en_data+assemble(data)
                break
            else:
                _data=data[:self.max_plain]
                data=data[self.max_plain:]
                #en_data = en_data+b"\r\n"+cipher.encrypt(_data)
                en_data = en_data+assemble(_data)

        return en_data


    def decrypt(self,en_data):
        """
        解密
        返回byte格式
        """
        private_key = RSA.import_key(self.private_key)
        cipher = PKCS1_OAEP.new(private_key,hashAlgo=self.hashAlgo)
        data=b""
        """
        for _en_data in en_data.split(b"\r\n"):
            data = data+cipher.decrypt(_en_data)
        """
        while en_data:
            _len=int(en_data[:self.len_len].decode("latin1"))
            en_data=en_data[self.len_len:]
            _en_data=en_data[:_len]
            en_data=en_data[_len:]
            data = data+cipher.decrypt(_en_data)
            
        return data



if __name__ == "__main__":
    rc=RsaCrypt()
    #print(rc.private_key,rc.public_key)
    data = b"123456"
    en_data=rc.encrypt(data)
    rc.decrypt(en_data)

if __name__ == "__main__":
    """
    openssl genrsa -out key.pem                  #私钥
    openssl rsa -in key.pem -pubout > key.pub    #公钥
    """
    rc=RsaCrypt()
    print(rc.private_key,rc.public_key)
    rc.private_key=open("key.pem","rb").read()
    rc.public_key=open("key.pub","rb").read()
    #print(rc.private_key,rc.public_key)
    data = b"123456"
    
    en_data=rc.encrypt(data)
    rc.decrypt(en_data)
