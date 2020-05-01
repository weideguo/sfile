#coding:utf8
import re
import time
import os
import shutil
import sys

def get_content(filename):
    """
    读取文件，过滤注释行，逐行组成list
    """
    content_line=[]
    #获取字符串
    with open(filename) as f:
        l=f.readline()
        while l:
            
            if sys.version_info<(3,0):
                l=l.decode("utf8")   #转成unicode，python2需要，python3默认直接转成unicode
            if re.match("^#.*",l) or not l.strip():
                pass
            else:
                content_line.append(l.strip())
                
            l=f.readline()
            
    return content_line

def append_newline(filename,line):
    """
    向文件尾部添加一行
    """
    #print(filename,line)
    with open(filename,"a") as f:
        f.write("\n")
        if sys.version_info<(3,0):
            #python2 需要先由unicode转成字节格式
            line=line.encode("utf8")
        f.write(line)


def rewrite(filename,line_list):
    """
    去除非注释行，向文件尾部添加
    """
    comment_line=[]
    with open(filename) as f:
        l=f.readline()
        while l:
            if re.match("^#.*",l.strip()):
                comment_line.append(l)
            
            l=f.readline()
    
    with open(filename,"w+") as f:
        for l in comment_line:
            f.write(l)

        for line in line_list:
            if sys.version_info<(3,0):
                #python2 需要先由unicode转成字节格式
                line=line.encode("utf8")
            f.write(line)
            f.write("\n")


def copy(srcfile,dstfile):
    """
    复制文件
    """
    if srcfile == dstfile:
        #相同文件则不用进行操作
        pass
    else:
        path=os.path.dirname(dstfile)
        if not os.path.exists(path):
            os.makedirs(path)
            
        shutil.copyfile(srcfile,dstfile) 


def move(srcfile,to_path="/tmp",rename="default"):
    """
    移动文件
    """
    if not os.path.exists(to_path):
        os.makedirs(to_path)
    
    dstfile=os.path.join(to_path,os.path.basename(srcfile))

    if rename=="default":
        rename=str(time.time())
    if rename:
        dstfile=dstfile+"."+rename
        
    shutil.move(srcfile,dstfile) 


def lock_file(default_path,md5_str,filename,dirname="lock"):
    """
    组成一个格式化的锁文件路径
    """
    return os.path.join(default_path,"%s/%s__%s" % (dirname,md5_str,filename.replace("/","__")))


class SimpleConfig(object):
    """
    读取文件获取键值对，同时支持写回文件
    文件格式
    key = value
    """
    def __init__(self,filename):
        self.filename=filename
        self.data = []
        i=0
        with open(filename) as f:
            l=f.readline()
            while l:
                if re.match("^#.*",l.strip()) or not l.strip():
                    self.data.append((i+1,l))
                else:
                    ls=l.strip().split("=")
                    k=ls[0].strip()
                    v="=".join(ls[1:]).strip()   #防止存在多个=
                    if sys.version_info<(3,0):
                        v=v.decode("utf8")

                    self.data.append((i,k,v))
                i=i+1
                l=f.readline()
            
    
    def read(self,key):
        """
        读取对应key的值
        如果存在多个相同key，以最后一个为准
        """
        v=""
        for l in self.data:
            if len(l) == 3 and l[1] == key:
                v=l[2]
        
        return v


    def write(self,key,value):
        """
        写对应的key值
        如果原来key不存在，在最后面添加一行
        """
        i=0
        j=0
        for l in self.data:
            if len(l) == 3 and l[1] == key:
                j=i+1
                self.data[i]=(j,key,value)
            i=i+1
        
        if not j:
            self.data.append((i+1,key,value))

        #写回文件
        with open(self.filename,"w+") as f:
            for l in self.data:
                if len(l)==2:
                    f.write(l[1])
                elif len(l)==3:
                    ln="%s = %s\n" % (l[1],l[2])
                    if sys.version_info<(3,0):
                        ln=ln.encode("utf8")
                    f.write(ln)
