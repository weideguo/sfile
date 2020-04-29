#coding:utf8
import sys

def get_length(sock):
    """
    获取首部的长度字段
    """
    s_length=""
    while True:
        r_str=sock.recv(1)
        if not r_str:
            return 0
        if sys.version_info>(3,0):
            r_str=r_str.decode("utf8")
        #"\r\n" 分割
        if  r_str == "\r":
            sock.recv(1)  #"\n"
            break
        s_length=s_length+r_str
    
    return int(s_length)

      
def get_file_info(sock):
    """
    获取文件的内容，文件名
    """
    _len=get_length(sock)
    filename=sock.recv(_len)
    
    sock.recv(2) #"\r\n"
    md5=sock.recv(32)
    sock.recv(2) #"\r\n"
    
    #内容可能过长，需要分块获取
    content_len=get_length(sock)
    
    return filename,md5,content_len


def get_info(sock):
    """
    获取主信息，md5信息并格式化
    """
    _len=get_length(sock)
    info_str=sock.recv(_len)
    #一行以"\n"分割（linux默认）
    return info_str.decode("utf8").split("\n")





def readline(sock):
    """
    获取一行数据，通过"\n"划分
    """
    l=b""
    while True:
        c=sock.recv(1)
        if (not c) or c.decode("latin1") == "\n" :
            break
        l=l+c
    
    l=l
    return l

