#coding:utf8
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP



class RsaCrypt(object):
    """
    RSA 加密/解密
    openssl genrsa -out key.pem                  #私钥
    openssl rsa -in key.pem -pubout > key.pub    #公钥
    """

    def __init__(self):
        self.private_key, self.public_key = self.get_key()


    def get_key(self,key_len=2048):
        """
        生成公钥和私钥
        key_len 1024 / 2048 / 3072
        """
        key = RSA.generate(key_len)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key,public_key


    def encrypt(self,data):
        """
        加密
        传入byte格式
        """
        public_key = RSA.import_key(self.public_key)
        cipher = PKCS1_OAEP.new(public_key)
        en_data = cipher.encrypt(data)
        return en_data


    def decrypt(self,en_data):
        """
        解密
        返回byte格式
        """
        private_key = RSA.import_key(self.private_key)
        cipher = PKCS1_OAEP.new(private_key)
        data = cipher.decrypt(en_data)

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
    