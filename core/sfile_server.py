#coding:utf8
import os
import re
import sys
import copy
import time
import uuid
import socket
from threading import Thread,Lock
from traceback import format_exc

from watchdog.observers import Observer

import sys
if sys.version_info>(3,0):
    import queue as Queue
else:
    import Queue
    BrokenPipeError=socket.error

from lib import utils
from lib.logger import logger,logger_err
from lib import socket_lib
from lib import file_lib
from lib.safe_type import FileLock
from lib.file_listen import FileEventHandler


class SfileServer(object):
    def __init__(self,priority,bind,default_path,config_path,socket_type,file_md5="md5.txt",file_conn="sfile.conf",auth=""):
        #优先级为负数则说明是slave
        self.priority     = priority    
        self.bind         = bind
        self.default_path = default_path
        self.config_path  = config_path
        self.file_md5     = os.path.join(config_path,file_md5)
        self.file_conn    = os.path.join(config_path,file_conn)        
        
        self.host=self.bind.split(":")[0].strip()
        self.port=int(self.bind.split(":")[1].strip())

        self.auth=auth

        #响应其他连接的操作类型
        self.cmd_type=["quit","exit","getfile","auth"]

        #连接其他服务获得的消息类型，恒为4字节
        self.msg_types=["erro","file","fmd5","info","pror","succ"]

        #内置类型线程安全
        #连接自己的列表
        self.listen_list = {}
        
        #已经连接的列表
        self.conn_list = set()
        #自己要连接别的服务的队列
        self.conn_queue = Queue.Queue()
        #配置文件中的连接信息
        self.conn_file = set()

        #md5的信息列表
        self.md5_list = set()
        #配置文件中的md5信息
        self.md5_file = set()

        file_md5_path=os.path.dirname(self.file_md5)
        file_md5_name="."+os.path.basename(self.file_md5)+".swp"
        #vim的锁文件，确保vim写的安全
        self.lock_file=os.path.join(file_md5_path,file_md5_name)
        #锁目录，用于存储标记文件正在处理（下载/移动/复制）的锁
        self.lock_path= "/tmp"

        #是否严格检查，如下载时检查md5
        self.strict_check = True
        #socket作为服务时使用多个线程发数据，需要确保线程间不相互影响
        self.sock_send_lock = Lock()
        #使用的socket类型 0 未加密；1 aes加密；2 ssl加密
        self.socket_type=socket_type
        self.init()


    def init(self):
        """
        一些初始化操作：连接列表，md5列表
        """
        for l in file_lib.get_content(self.file_conn):
            l=l.strip()
            host=l.split(":")[0].strip()
            port=int(l.split(":")[1].strip())
            if (host,port) != (self.host,self.port):
                self.conn_queue.put((host,port))
                self.conn_file.add((host,port))
        
        for l in file_lib.get_content(self.file_md5):
            l=l.strip()
            md5_str=l.split(" ")[0].strip()
            filename=l.split(md5_str)[1].strip()
            self.md5_list.add((md5_str,filename))
            self.md5_file.add((md5_str,filename))

        if not len(self.conn_file):
            #没有其他主的信息
            raise Exception("at least one master info must set in \"%s\"" % self.file_conn)

        file_list=[x[1] for x in self.md5_list]
        if len(file_list) != len(set(file_list)):
            #md5配置不应该存在重复的文件名
            raise Exception("filename duplicated")
    

    def init_md5(self):
        """
        计算监听目录下所有文件的md5，并更新到md5配置文件。在实例化后可选是否调用该函数
        """
        #清空已有的md5信息，以新读取为准
        self.md5_file = set()
        root_path=self.default_path
        for i in os.walk(root_path):
            if i[2]:
                for j in i[2]:
                    filename=os.path.join(i[0],j)
                    md5_str=utils.my_md5(filename)
                    _filename = filename.split(root_path)[-1][1:]
                    if sys.version_info<(3,0):
                        _filename=_filename.decode("utf8")   
                    self.md5_list.add((md5_str,_filename))
        
        #with FileLock(self.lock_file):
        _line_list=["%s  %s" % (md5_str,filename) for md5_str,filename in self.md5_list]
        file_lib.rewrite(self.file_md5, _line_list)


    def do_request(self,sock,addr,id):
        """
        响应请求
        """
        sock=socket_lib.get_socket(sock, self.socket_type)
        def send_priority():
            #其发送自己的优先级
            pror="%s\r\n%d\r\n%d\r\n" % (self.msg_types[4],len(str(self.priority)),self.priority)
            sock.sendall(pror.encode("utf8"))

        if not self.auth:
            """
            不需要密码认证时
            """
            self.listen_list[id]=(sock,addr) 
            send_priority()

        while True:
            try:
                #逐行读取，即一行以"\n"结尾
                #使用latin1编码，单字节编码，不会丢失数据
                data=socket_lib.readline(sock).decode("latin1").strip()
                
            except:
                logger.error(format_exc())
                break
            
            if data ==self.cmd_type[0] or data ==self.cmd_type[1] or not data:
                """
                接收到 exit quit 则退出
                """
                break
            else:
                if data.split(" ")[0]==self.cmd_type[3]:
                    """
                    处理认证
                    """
                    _auth=data.split(self.cmd_type[3])[-1].strip()
                    if not self.auth:
                        info_data="no auth neeeded"
                        send_data="%s\r\n%d\r\n%s\r\n" % (self.msg_types[5],len(info_data),info_data)
                    elif _auth==self.auth:
                        self.listen_list[id]=(sock,addr) 
                        send_priority()
                        info_data="login success"
                        send_data="%s\r\n%d\r\n%s\r\n" % (self.msg_types[5],len(info_data),info_data)
                    else:
                        error_data="auth failed"
                        send_data="%s\r\n%d\r\n%s\r\n" % (self.msg_types[0],len(error_data),error_data)

                    with self.sock_send_lock:
                        sock.sendall(send_data.encode("latin1"))
                elif (id in self.listen_list) and (self.listen_list[id]==(sock,addr)):
                    #已经登陆
                    if (data.split(" ")[0]==self.cmd_type[2]):
                        """
                        处理文件请求
                        """
                        filename=data.split(self.cmd_type[2])[-1].strip()
                        try:
                            #读取文件时需要转换成utf8，兼容中文
                            filename_r=filename.encode("latin1").decode("utf8")
                            filename_r=os.path.join(self.default_path,filename_r)
                            md5 = utils.my_md5(file=filename_r)

                            c_length=os.path.getsize(filename_r)
                            n_length=len(filename)
                            with self.sock_send_lock:
                                send_data="%s\r\n%d\r\n%s\r\n%s\r\n%d\r\n" % (self.msg_types[1],n_length,filename,md5,c_length)
                                sock.sendall(send_data.encode("latin1")) 
                                #f=open(filename_r,"rb")
                                ##python2没有sendfile？
                                #sock.sendfile(f)
                                #f.close()
                                with open(filename_r,"rb") as f:
                                    d=f.read(1024)
                                    while d:
                                        sock.sendall(d)
                                        d=f.read(1024)
                                
                                sock.sendall("\r\n".encode("latin1")) 
                        except:
                            error_data="\"%s\" read failed" % filename
                            send_data="%s\r\n%d\r\n%s\r\n" % (self.msg_types[0],len(error_data),error_data)

                            with self.sock_send_lock:
                                sock.sendall(send_data.encode("latin1"))
                            logger_err.error(format_exc())

                    else:
                        """
                        其他命令不支持
                        """
                        error_data="\"%s\" is unknown" % data
                        send_data="%s\r\n%d\r\n%s\r\n" % (self.msg_types[0],len(error_data),error_data)
                        #服务端的发送
                        with self.sock_send_lock:
                            #持续发送直至完全完成 而send方法可能只发送部分数据
                            sock.sendall(send_data.encode("latin1"))
                else:
                    #未登陆
                    error_data="auth required"
                    send_data="%s\r\n%d\r\n%s\r\n" % (self.msg_types[0],len(error_data),error_data)
                    with self.sock_send_lock:
                        sock.sendall(send_data.encode("latin1"))

        sock.close()
        #连接关闭则从队列中弹出
        if id in self.listen_list:
            self.listen_list.pop(id)
        logger.info("Connection from %s:%s closed." % addr)
    
    
    def __listen(self):
        """
        监听端口，每个连接创建一个并发
        """
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    #端口复用，否则关闭时端口处于time_wait而不能立即使用

        s.bind((self.host,self.port))
        logger.info("start tcp success, listening at: %s" % self.bind)
        #the number of unaccepted connections that the system will allow before refusing new connections
        s.listen(0)   
        threads=[]
        while True:   
            id = self.priority
            sock,addr=s.accept() 

            #然后后台处理，响应请求        
            t=Thread(target=self.do_request,args=(sock,addr,id))
            t.start()
        
        for t in threads:
            t.join()

        #如果运行到此，说明出现错误
        logger_err.error("tcp server exit")
    
    
    def do_send(self,sock,addr,id):
        """
        发送主信息，md5信息，配置信息必须为utf8编码
        """
        def _socket_send(tag, content_list):
            _content=""
            for s1,s2 in content_list:
                #文件以"\n"分割每一行（linux默认）
                #_content=_content+str(s1)+" "+str(s2)+"\n"
                _content=_content+("%s %s\n" % (s1,s2))

            _content=_content[:-1]  #去除最后一个"\n
            _len=len(_content.encode("utf8"))
            content = "%s\r\n%d\r\n%s\r\n" % (tag,_len,_content)
            #服务端的发送 需要锁防止对发送文件形成干扰
            with self.sock_send_lock:
                sock.sendall(content.encode("utf8"))

        try:
            #logger.debug(self.md5_list)
            _socket_send(self.msg_types[2],self.md5_list)
        
            _conn_list={(self.host,self.port)}
            _conn_list.update(self.conn_list) 
            _socket_send(self.msg_types[3],_conn_list)
        except BrokenPipeError:
            self.listen_list.pop(id)


    def __send(self):
        """
        主动发送，只有master启用
        """
        while True:
            for id in self.listen_list.keys():
                sock,addr = self.listen_list[id]
                t=Thread(target=self.do_send,args=(sock,addr,id))
                t.start()
                logger.debug("send to client: " +str(sock)+" "+str(addr) )
            time.sleep(10)  


    def do_get(self,sock,addr):
        """
        处理获取的信息
        """
        sock=socket_lib.get_socket(sock, self.socket_type)
        if self.auth:
            #需要认证时连接创建后发送认证请求
            send_data="%s %s\n" % (self.cmd_type[3],self.auth)
            sock.sendall(send_data.encode("utf8"))
            logger.debug(str(addr)+" "+send_data)

        #连接的服务的优先级
        priority=0
        while True:
            msg_type=sock.recv(4).decode("utf8")
            sock.recv(2)
            if msg_type==self.msg_types[0]:
                """
                错误返回
                """
                _len=socket_lib.get_length(sock)
                error_info=sock.recv(_len)
                sock.recv(2)
                logger_err.error(str(addr)+" "+error_info.decode("utf8"))

            elif msg_type==self.msg_types[1]:
                """
                请求文件的返回
                """
                filename,md5,content_len = socket_lib.get_file_info(sock)
                
                filename=filename.decode("utf8")
                _filename=os.path.join(self.default_path,filename)
                md5=md5.decode("utf8")
                logger.debug("%s get file info: %s %s %d" % (str(addr),filename,md5,content_len))
                try:
                    _content_len = socket_lib.write(sock,_filename,content_len)
                    
                    host,port = addr
                    if content_len != _content_len:
                        raise Exception("%s:%d %s %d %d download success but file length different" % (host,port,filename,content_len,_content_len))
                    
                    if self.strict_check:
                        _md5=utils.my_md5(file=_filename)
                        if md5 != _md5:
                            raise Exception("%s:%d %s download success but md5 different" % (host,port,filename))

                    self.md5_list.add((md5,filename)) 
                    tmp_lock=file_lib.lock_file(self.lock_path,md5,filename)
                    FileLock().remove_lock(tmp_lock)
                    logger.debug("%s get file done: %s %s %d" % (str(addr),filename,md5,content_len))
                except:
                    if addr in self.md5_list:
                        self.md5_list.remove(addr)
                    logger_err.error(format_exc())

            elif msg_type==self.msg_types[2]:
                """
                获取md5信息
                """
                for l in socket_lib.get_info(sock):
                    md5_str,filename = l.split(" ")

                    if (md5_str,filename) not in self.md5_list:
                        #创建一个锁文件标记已经被处理，其他线程不再处理
                        tmp_lock=file_lib.lock_file(self.lock_path,md5_str,filename)
                        is_opt=True
                        try:
                            FileLock().get_lock(tmp_lock)
                        except:
                            logger.debug(format_exc())
                            is_opt=False

                        if is_opt:
                            _filename=os.path.join(self.default_path,filename)
                            _md5_list=copy.deepcopy(self.md5_list)
                            #self.md5_list.add((md5_str,filename))   

                            if filename in [x[1] for x in _md5_list]:
                                #文件存在，但md5不同
                                if (priority > self.priority) and (self.priority > 0):
                                    #自己的优先级更高，不处理，其他线程继续处理
                                    FileLock().remove_lock(tmp_lock)
                                    logger.debug("skip %s %s cause priority %d > %d" % (md5_str,filename,priority,self.priority)) 
                                else:
                                    #自己的优先级更低，则处理
                                    for m,f in _md5_list:
                                        if f==filename:
                                            self.md5_list.remove((m,f)) 

                                    logger.debug("mv %s %s" % (filename ,"/tmp"))  
                                    try:
                                        #移动本地文件remove
                                        file_lib.move(_filename)
                                        #不必下载文件，标记下次下载
                                        FileLock().remove_lock(tmp_lock)
                                    except:
                                        logger_err.error(format_exc())

                            elif md5_str in [x[0] for x in _md5_list]:   
                                #md5存在，应该复制文件
                                for m,f in _md5_list:
                                    if m==md5_str:
                                        logger.debug("copy %s %s" % (f,filename) )
                                        f=os.path.join(self.default_path,f)
                                        try:
                                            file_lib.copy(f,_filename)
                                            self.md5_list.add((md5_str,filename)) 
                                            FileLock().remove_lock(tmp_lock)
                                        except:
                                            logger_err.error(format_exc())

                                        break
                                    
                            else:
                                #发起下载
                                download="%s %s\n" % (self.cmd_type[2],filename)
                                sock.sendall(download.encode("utf8"))
                                logger.debug(str(addr)+" "+download)
                        else:
                            logger.debug("\"%s\" lock exist, ignore operation" % tmp_lock)
                        
                sock.recv(2)
                logger.debug(self.md5_list)

            elif msg_type==self.msg_types[3]:
                """
                获取主的信息
                """
                for l in socket_lib.get_info(sock):
                    host,port = l.split(" ")
                    port = int(port)
                    if (host,port) != (self.host,self.port):
                        self.conn_queue.put((host,port))
                sock.recv(2)
            
            elif msg_type==self.msg_types[4]:
                """
                获取优先级
                """
                _len=socket_lib.get_length(sock)
                priority=int(sock.recv(_len))
                sock.recv(2)
            elif msg_type==self.msg_types[5]:
                """
                获取一些成功的提示
                """
                _len=socket_lib.get_length(sock)
                info=sock.recv(_len)
                sock.recv(2)
                logger.debug(str(addr)+" "+info.decode("utf8"))
            else:
                """
                未知的请求
                """
                unknown=sock.recv(1024)
                #获取值为空，说明连接已经断开
                if not unknown:
                    logger.debug("%s:%d connect broken" % addr)
                    if addr in self.conn_list:
                        self.conn_list.remove(addr)
                    #连接则重新连接，防止出现与其他服务连接都断开后被隔离
                    self.conn_queue.put(addr)
                    break
                else:
                    logger.debug("%s:%d get unknown info, read 1024 byte:" % addr)
                    logger.debug(unknown)
    
    
    def __conn(self):
        """
        连接其他的服务获取消息（主信息，md5信息）更新于本地/下拉文件
        """
        #等待连接的队列
        _tmp_conn_list=set()
        while True:
            addr = self.conn_queue.get()    
            conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                if addr not in self.conn_list:
                    #没有连接才新创建连接
                    conn.connect(addr)
                    #连接成功再通知其他服务
                    self.conn_list.add(addr)

                    t=Thread(target=self.do_get,args=(conn,addr))
                    t.start()
                    
            except socket.error:
                if addr not in _tmp_conn_list:
                    #对于一个地址，同时只运行一个休眠
                    _tmp_conn_list.add(addr)
                    #连接失败，则重新连接
                    def _sleep(addr,sleep_time=10):
                        logger.debug("%s:%d connect failed, wait and retry later" % addr)
                        time.sleep(sleep_time)   
                        self.conn_queue.put(addr)
                        _tmp_conn_list.remove(addr)

                    t=Thread(target=_sleep,args=(addr,))
                    t.start()
            except:
                logger.error(format_exc())


    def __config_rewrite(self):
        """
        配置文件回写
        md5配置文件重读，通过md5配置文件实现对本地文件的监听
        """
        while True:
            #连接列表未空，则不要改变已有配置（如在关闭时至少保留一条配置）
            if self.conn_list:
                if (self.conn_list-self.conn_file) or (self.conn_file-self.conn_list):
                    _line_list=["%s:%d" % addr for addr in self.conn_list]
                    file_lib.rewrite(self.file_conn, _line_list)
                    self.conn_file=copy.deepcopy(self.conn_list)
                    logger.debug("rewrite conn file")
                else:
                    logger.debug("rewrite conn file skip")
            
            #配置文件不支持减少，如果减少，会被再次同步回来
            #必须使用vim编辑md5配置文件，或者其他在编辑前检查vim锁文件
            #当程序获得锁，vim不能编；反之亦可
            try:
                #os.mknod(self.lock_file)
                with FileLock(self.lock_file):
                    #重新读取md5配置文件，以实现更新以及通知其他服务
                    _md5_file=set()
                    for l in file_lib.get_content(self.file_md5):
                        l=l.strip()
                        md5_str=l.split(" ")[0].strip()
                        filename=l.split(md5_str)[1].strip()
                        _md5_file.add((md5_str,filename))

                    #跟上次读取时对比
                    #配置文件减少（其他服同步时会再次下载并添加配置）
                    minus =  self.md5_file - _md5_file
                    #配置文件新增（通知其他服文件可用 ）
                    add =  _md5_file - self.md5_file
                    self.md5_list.update(add)
                    self.md5_list=self.md5_list - minus

                    self.md5_file=copy.deepcopy(_md5_file)

                    logger.debug("md5 config change add: "+str(add)+"  minus: "+str(minus))
                    
                    if (_md5_file - self.md5_list) or (self.md5_list - _md5_file):
                        _line_list=["%s  %s" % (md5_str,filename) for md5_str,filename in self.md5_list]
                        file_lib.rewrite(self.file_md5, _line_list)
                        self.md5_file=copy.deepcopy(self.md5_list)
                        logger.debug("rewrite md5 file")
                    else:
                        logger.debug("rewrite md5 file skip")

                #移除锁文件
                #os.remove(self.lock_file)   
            except (OSError,FileExistsError):
                #创建vim锁失败，说明有vim在编辑，跳过回写操作一次
                logger.debug("skip rewrite md5 file cause \"%s\" exist" % self.lock_file)
            
            time.sleep(10)

    
    def __file_listen(self):
        """
        主动监目录并更新md5文件
        """
        listen_path = self.default_path
        observer = Observer()
        event_handler = FileEventHandler(file_md5=self.file_md5,listen_path=listen_path)
        observer.schedule(event_handler, listen_path, True)
        observer.start()
        observer.join()


    def start(self):
        t_list=[]
        #从只有两个操作
        t=Thread(target=self.__conn)
        t_list.append(t)
        t=Thread(target=self.__config_rewrite)
        t_list.append(t)

        #以下操作主独有
        if self.priority > 0:
            t=Thread(target=self.__listen)
            t_list.append(t)
            t=Thread(target=self.__send)
            t_list.append(t)
            t=Thread(target=self.__file_listen)
            t_list.append(t)

        for t in t_list:
            t.start()
            
        for t in t_list:
            t.join()
    
