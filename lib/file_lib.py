#coding:utf8
import re
import time
import os
import shutil

def get_content(filename):
    """
    读取文件，过滤注释行，逐行组成list
    """
    content_line=[]
    #获取字符串
    with open(filename) as f:
        l=f.readline()
        while l:
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
        f.write(line)


def rewrite(filename,line_list):
    """
    去除非注释行，向文件尾部添加
    """
    comment_line=[]
    with open(filename) as f:
        l=f.readline()
        while l:
            if re.match("^#.*",l):
                comment_line.append(l)
            
            l=f.readline()
    
    with open(filename,"w+") as f:
        for l in comment_line:
            f.write(l)

        for line in line_list:
            f.write(line)
            f.write("\n")


def write(filename,sock,content_len,max_len=1024):
    """
    从sock获取指定长度写入文件
    """
    path=os.path.dirname(filename)
    if not os.path.exists(path):
        os.makedirs(path)
    
    with open(filename,"wb") as f:
        while True:
            if not content_len:
                sock.recv(2)
                break
            else:
                #取小值
                get_len =  max_len if (max_len<content_len) else content_len
                #获取大量数据出现长度不匹配？
                content=sock.recv(get_len)
                f.write(content)
                f.flush()
                content_len=content_len-len(content)

    return os.path.getsize(filename)



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
