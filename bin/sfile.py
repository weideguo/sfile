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
from lib.wrapper import get_aes_crypt,get_rsa_crypt


config_path=os.path.join(base_dir,"conf")
file_key=os.path.join(config_path,"key.conf")
sc=SimpleConfig(file_key)

if __name__ == "__main__":
    """
    主之间有优先级，优先级低的主如果发现文件不同，则要更改自己的文件
    高低优先级同时存在的配置信息，以高的为准，低的抛弃
    优先级为负数则说明是slave
    """
    priority=int(time.time())
    #priority=-1

    bind="127.0.0.1:9010"
    
    #监听文件的根目录
    default_path="/tmp/b"

    #不设置则不需要认证
    #auth="123456"
    auth=sc.read("auth")
    #auth=""
    
    print("listening at: \033[1;32m %s \033[0m" % bind)
    print("auth: \033[1;32m %s \033[0m" % auth)

    socket_type=1

    if socket_type==0:
        #使用aes加密socket
        crypt,_key,_iv=get_aes_crypt(sc)
        print("key: \033[1;32m %s \033[0m ,iv: \033[1;32m %s \033[0m" % (_key,_iv))
    elif socket_type==1:
        #使用rsa加密socket
        crypt,_private_key,_public_key=get_rsa_crypt(sc)
        print("private_key: \033[1;32m %s \033[0m ,public_key: \033[1;32m %s \033[0m" % (_private_key,_public_key))
    else:
        crypt=None
    
    ss=SfileServer(priority,bind,default_path,config_path,crypt,auth=auth)
    ss.init_md5()
    ss.start()

    
    

    
