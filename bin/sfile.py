#!/bin/env python
#coding:utf8
#start server from here
#simple sync file server
#by weideguo in 20200415
import os
import sys
import time

import optparse

base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from core.sfile_server import SfileServer
from lib.file_lib import SimpleConfig
from lib.wrapper import get_aes_crypt,get_rsa_crypt
from lib import file_lib


config_path=os.path.join(base_dir,"conf")
file_key=os.path.join(config_path,"key.conf")
sc=SimpleConfig(file_key)

file_conn="master.conf"
_file_conn=os.path.join(config_path,file_conn)

file_md5="md5.txt"

sc=SimpleConfig(file_key)


"""
主之间有优先级，越小则代表更高的优先级
优先级为负数则说明是slave，slave不会监听端口与文件变化只接受文件
优先级低的主如果发现文件不同，则要更改自己的文件
高先级低的主如果接收同文件但不同md5，则以先接收的为准，之后的会被抛弃；因此文件的变化最好在最高优先级的主进行
"""

def arg_parse():
    """
    命令行参数解析
    """
    usage = "Usage: %prog [options]"
    usage += "\n\nstart with following options:"


    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-p", "--priority", type="int", default=int(time.time()), help=u"优先级")
    parser.add_option("-b", "--bind", default="127.0.0.1:9010", help=u"监听的 ip:端口，不要绑定0.0.0.0")
    parser.add_option("-d", "--default_path", default="/tmp", help=u"监听文件的根目录")

    parser.add_option("-c", "--conn_master", help=u"要连接的主的信息 ip:port,ip1:port1（默认从配置文件读取）")
    parser.add_option("-s", "--socket_type", type="int", default=2, help=u"socket加密类型 0 aes; 1 rsa; 其他则没有加密（默认2）")

    parser.add_option("--master", action="store_const", const=int(time.time()), dest="priority", help=u"以master启动，不用再设置优先级")
    parser.add_option("--slave", action="store_const", const=-1, dest="priority", help=u"以slave启动，不用再设置优先级")

    """
    if len(sys.argv)<=1:
        parser.print_help()
        sys.exit(1)
    """
    return parser.parse_args()


if __name__ == "__main__":

    options, args = arg_parse()

    priority      = options.priority     
    bind          = options.bind  
    default_path  = options.default_path
    conn_master   = options.conn_master
    socket_type   = options.socket_type
    
    print(priority, bind, default_path, conn_master, socket_type)

    if conn_master:
        file_lib.rewrite(_file_conn, conn_master.split(","))

    #不设置则不需要认证
    #auth="123456"
    auth=sc.read("auth")
    #auth=""
    
    print("priority: \033[1;32m %s \033[0m ,bind: \033[1;32m %s \033[0m ,path: \033[1;32m %s \033[0m" % (priority,bind,default_path))
    print("auth: \033[1;32m %s \033[0m" % auth)

    

    if socket_type==0:
        #使用aes加密socket
        crypt,_key,_iv=get_aes_crypt(sc)
        print("key: \033[1;32m %s \033[0m ,iv: \033[1;32m %s \033[0m" % (_key,_iv))
    elif socket_type==1:
        #使用rsa加密socket
        #性能问题比较严重
        crypt,_private_key,_public_key=get_rsa_crypt(sc)
        print("private_key: \033[1;32m %s \033[0m ,public_key: \033[1;32m %s \033[0m" % (_private_key,_public_key))
    else:
        crypt=None
    
    ss=SfileServer(priority,bind,default_path,config_path,file_md5=file_md5,file_conn=file_conn,crypt=crypt,auth=auth)
    ss.init_md5()
    ss.start()

   