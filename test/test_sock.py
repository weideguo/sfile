#coding:utf8
#socket解密测试
import os
import sys
import socket

base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from lib.socket_lib import get_socket
from lib.file_lib import SimpleConfig
from lib.wrapper import get_aes_crypt,get_rsa_crypt


config_path=os.path.join(base_dir,"conf")
file_key=os.path.join(config_path,"key.conf")
sc=SimpleConfig(file_key)

if __name__ == "__main__":
    
    crypt,_,_=get_aes_crypt(sc)
    #crypt,_,_=get_rsa_crypt(sc)
    #crypt=None
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(('127.0.0.1',9010))
    
    sock=get_socket(s,crypt)

    sock.sendall(b"auth 123456www\n")
    sock.sendall(b"getfile 20200415.txt\n")

    sock.recv(4)


