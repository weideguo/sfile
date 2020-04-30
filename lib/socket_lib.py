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



def get_socket(sock, sock_type=0):
    """
    由传入的套接字获取封装的套接字
    """
    if sock_type==0:
        #最基本socket
        return sock

    elif sock_type==1:
        #使用aes加密传输的socket

        return AesSocket(sock)
    
    elif sock_type==2:
        #使用ssl加密传输的socket
        return None


class AesSocket(object):
    data=""

    def __init__(self,sock):
        self.sock=sock

    def sendall(self,data):
        """
        加密传输
        """
        pass

    def sendfile(self,file):
        """
        加密传输文件
        传入二进制打开的文件流
        """
        pass


    def recv(self,buffersize):
        """
        获取指定解密后的长度
        """
        if self.data:
            _data = self.data[:buffersize]
            self.data = self.data[buffersize:]
            return _data
        _len=get_length(self.sock)
        self.sock.recv(2)
        #获取一个加密单元并解密
        #data=decrypt(self.sock,_len)
        self.data=""
        _date = self.data[:buffersize]
        self.data = self.data[buffersize:]
        return _data


    def close(self):
        self.sock.close()
