#coding:utf8
#socket解密测试
import os
import sys
import socket

base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from lib.socket_lib import AesSocket
from lib.file_lib import SimpleConfig
from lib.aes_lib import aes_crypt

"""
ac=aes_crypt
data=""
en_data=ac.aes_encrypt(data,ac.key,iv=ac.iv)
print(en_data)

en_data=""
ac.aes_decrypt(en_data,ac.key,iv=ac.iv)
"""
if __name__ == "__main__":
    config_path=os.path.join(base_dir,"conf")

    file_key=os.path.join(config_path,"key.conf")
    sc=SimpleConfig(file_key)

    _key=sc.read("key").encode("utf8") 
    _iv=sc.read("iv").encode("utf8") 
    aes_crypt.key = _key
    aes_crypt.iv = _iv

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(('127.0.0.1',9010))
    sock=AesSocket(s)

    sock.sendall(b"auth 123456www\n")
    sock.sendall(b"getfile 20200415.txt\n")

    sock.recv(4)


