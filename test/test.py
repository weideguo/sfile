"""
getfile   /tmp/中文.txt
getfile    /tmp/aaa.txt
/data/python3.5.7/bin/python3.5
ps -ef | grep ython | grep "sfile.py" | awk '{print $2}' | xargs kill -9
"""
import socket
import sys

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('127.0.0.1',9010))

cmd="getfile /tmp/20200415.txt\n".encode("utf8")
cmd="getfile /tmp/h.gif\n".encode("utf8")
cmd="getfile /tmp/中文.txt\n".encode("utf8")

if sys.version_info<(3,0):
    cmd="getfile /tmp/中文.txt\n"
s.send(cmd)

cmd.encode("utf8")
s.recv(6)

f=open("/tmp/20200415.txt","rb")
f.read()


