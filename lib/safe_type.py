#coding:utf8
#一些类型的封装以保证并发的安全
import os
import time

class FileLock(object):
    """
    文件锁
    """
    def __init__(self,lock_file=None):
        self.f = lock_file
    
    def __enter__(self):
        self.get_lock(self.f)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove_lock(self.f)
    
    @staticmethod
    def get_lock(lock_file):
        #兼容python2，需要由unicode转成字节格式
        lock_file=lock_file.encode("utf8")
        path=os.path.dirname(lock_file)
        if not os.path.exists(path):
            os.makedirs(path)
        
        os.mknod(lock_file)
    
    @staticmethod
    def remove_lock(lock_file):
        lock_file=lock_file.encode("utf8")
        os.remove(lock_file)  


class BlockFileLock(FileLock):
    """
    阻塞式文件锁，获取失败时循环重试
    """
    def __enter__(self):
        self.get_lock(self.f)
    
    @staticmethod
    def get_lock(lock_file,sleep_gap=1,retry=60*5):
        i=0
        while True:
            try:
                FileLock.get_lock(lock_file)
                break
            except:
                i = i+1
                if (i > retry):
                    raise Exception("\"%s\" get lock file timeout, retry %d " % (lock_file,retry))
                    break
                print("lock failed and sleep")
                time.sleep(sleep_gap)


if __name__ == "__main__":
    with FileLock("/tmp/aaa1"):
        print(1111)

    while BlockFileLock("/tmp/aaa111"):
        print(11111)