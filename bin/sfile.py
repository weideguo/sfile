#!/bin/env python
#coding:utf8
#start server from here
#simple sync file server
#by weideguo in 20200415
import os
import sys
import time

base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from core.sfile_server import SfileServer
from lib.file_lib import SimpleConfig


if __name__ == "__main__":
    """
    使用socket同步信息
    
    同步主从
    同步md5信息
    下拉文件
    """
    """
    主之间有优先级，优先级低的主如果发现文件不同，则要更改自己的文件
    高低优先级同时存在的配置信息，以高的为准，低的抛弃
    优先级为负数则说明是slave
    """
    priority=int(time.time())
    #priority=-1
    """
    主之间完全同步信息，即一个主向其他所有主询问，自己也回应信息
    从只从任意一个主获取信息，从只能下拉文件，不回应信息
    主/从均对比信息，发现不同则下载到本地
    """
    
    bind="127.0.0.1:9010"
    
    #文件的默认根目录
    default_path="/tmp/b"
    
    
    config_path=os.path.join(base_dir,"conf")

    file_key=os.path.join(config_path,"key.conf")
    sc=SimpleConfig(file_key)
    
    #不设置则不需要认证
    #auth="123456"
    auth=sc.read("auth")
    #auth=""
    
    print("listening at: \033[1;32m %s \033[0m" % bind)
    print("auth: \033[1;32m %s \033[0m" % auth)

    socket_type=2

    if socket_type==1:
        #使用aes加密socket
        from lib.aes_lib import AesCrypt
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
        crypt=aes_crypt
        print("key: \033[1;32m %s \033[0m ,iv: \033[1;32m %s \033[0m" % (_key,_iv))
    
    elif socket_type==2:
        #使用rsa加密socket
        from lib.rsa_lib import RsaCrypt
        rsa_crypt=RsaCrypt()

        def set_key_file(key_name,key_default,file_content):
            _key=sc.read(key_name)
            if not _key:
                _key=key_default
                sc.write(key_name,key_default)
            try:
                _key=os.path.join(config_path,_key)
                _path=os.path.dirname(_key)
                if not os.path.exists(_path):
                    os.makedirs(_path)
                
                rsa_crypt.private_key = open(_key,"rb").read()
            except:
                with open(_key,"wb") as f:
                    f.write(file_content)
            
            return _key

        _private_key=set_key_file("private_key","rsa/key.pem",rsa_crypt.private_key)
        _public_key=set_key_file("public_key","rsa/key.pub",rsa_crypt.public_key)

        crypt=rsa_crypt
        print("private_key: \033[1;32m %s \033[0m ,public_key: \033[1;32m %s \033[0m" % (_private_key,_public_key))
    else:
        crypt=None
    
    #ss=SfileServer(priority,bind,default_path,config_path,crypt,auth=auth)
    
    #ss.init_md5()
    #ss.start()

    
    

    
