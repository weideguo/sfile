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
    #priority=int(time.time())
    priority=-1
    """
    主之间完全同步信息，即一个主向其他所有主询问，自己也回应信息
    从只从任意一个主获取信息，从只能下拉文件，不回应信息
    主/从均对比信息，发现不同则下载到本地
    """
    
    bind="127.0.0.1:9010"
    
    #文件的默认根目录
    default_path="/tmp/b"

    config_path=os.path.join(base_dir,"conf")
    ss=SfileServer(priority,bind,default_path,config_path)
    ss.start()
    

    
