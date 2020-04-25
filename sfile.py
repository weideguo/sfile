#!/bin/env python
#coding:utf8
#start server from here
#simple sync file server
#by weideguo in 20200415
import os
import time


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
    """
    priority=int(time.time())

    """
    主之间完全同步信息，即一个主向其他所有主询问，自己也回应信息
    从只从任意一个主获取信息，从只能下拉文件，不回应信息
    主/从均对比信息，发现不同则下载到本地
    """
    roles=["master","slave"]
    role=roles[0]
    
    bind="127.0.0.1:9010"
    
    #文件的默认根目录
    default_path="/tmp/b"

    from core.sfile_server import SfileServer
    config_path=os.path.dirname(os.path.abspath(__file__))
    ss=SfileServer(priority,role,bind,default_path,config_path)
    ss.start()
    

    
