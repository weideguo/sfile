# -*- coding: utf-8 -*- 
import os
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import utils
from . import file_lib
from .safe_type import BlockFileLock
from .wrapper import error_capture


ignore_postfix=[".swp", ".swx",".swpx"]

class FileEventHandler(FileSystemEventHandler):
    """
    监听文件增/删/改/移
    """
    
    def __init__(self,file_md5, listen_path):
        FileSystemEventHandler.__init__(self)
        
        self.file_md5=file_md5
        self.listen_path=listen_path
                
        file_md5_path=os.path.dirname(self.file_md5)
        file_md5_name="."+os.path.basename(self.file_md5)+".swp"
        #vim的锁文件，确保vim写的安全
        self.lock_file=os.path.join(file_md5_path,file_md5_name)

    @error_capture
    def on_moved(self, event):
        #移动 删除旧的md5 添加新的md5(删除+创建)
        if (not event.is_directory) and (not self.is_ignore(event.src_path)):
            md5,_path = self.get_info(event.dest_path)
            with BlockFileLock(self.lock_file):
                self.delete_md5(event.src_path)
                self.add_md5(md5,_path)
    
    @error_capture
    def on_modified(self, event):
        #修改 删除旧的md5 添加新的md5(删除+创建)
        if (not event.is_directory) and (not self.is_ignore(event.src_path)):
            md5,_path = self.get_info(event.src_path)
            with BlockFileLock(self.lock_file):
                self.delete_md5(event.src_path)
                self.add_md5(md5,_path)
    
    @error_capture
    def on_created(self, event):
        #创建 添加新的md5
        if (not event.is_directory) and (not self.is_ignore(event.src_path)):
            md5,_path = self.get_info(event.src_path)
            with BlockFileLock(self.lock_file):
                self.add_md5(md5,_path)

    @error_capture
    def on_deleted(self, event):
        #删除 从md5文件移除
        if (not event.is_directory) and (not self.is_ignore(event.src_path)):
            with BlockFileLock(self.lock_file):
                self.delete_md5(event.src_path)


    def is_ignore(self, path):
        postfix=os.path.splitext(path)[-1]
        return (postfix in ignore_postfix)

    
    def add_md5(self, md5, path):
        """
        处理文件添加的实际操作 往md5文件添加
        """
        if sys.version_info<(3,0):
            #python2 需要由字节码转成unicode
            path=path.decode("utf8")
        #print("add: %s %s" % (md5,path))
        md5_list=self.get_md5_list()
        md5_list.add((md5,path))
        _line_list=["%s  %s" % (md5_str,filename) for md5_str,filename in md5_list]
        file_lib.rewrite(self.file_md5, _line_list)
    
    def delete_md5(self, path):
        """
        处理文件删除的实际操作 往md5文件删除
        """
        if sys.version_info<(3,0):
            #python2 需要由字节码转成unicode
            path=path.decode("utf8")
        #获取相对目录
        _path = self.get_info(path,True)
        #print("remove: %s" % (_path))
        
        md5_list=self.get_md5_list()
        _md5_list=set()
        for md5_str,filename in md5_list:
            if filename==_path:
                _md5_list.add((md5_str,filename))
        
        #print(md5_list)
        md5_list=md5_list-_md5_list
        #print(md5_list)
        _line_list=["%s  %s" % (md5_str,filename) for md5_str,filename in md5_list]
        file_lib.rewrite(self.file_md5, _line_list)
    

    def get_md5_list(self):
        md5_list=set()
        for l in file_lib.get_content(self.file_md5):
            l=l.strip()
            md5_str=l.split(" ")[0].strip()
            filename=l.split(md5_str)[1].strip()
            md5_list.add((md5_str,filename))
        
        return md5_list


    def get_info(self, path, ignore_md5=False):
        _path = path.split(self.listen_path)[-1][1:]
        if not ignore_md5:
            md5 = utils.my_md5(file=path)
            return md5,_path
        else:
            return _path



