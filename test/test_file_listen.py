#coding:utf8

from watchdog.observers import Observer
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.file_listen import FileEventHandler

if __name__ == "__main__":
    file_md5="/tmp/xxx"
    listen_path = "/tmp/a"
    
    observer = Observer()
    event_handler = FileEventHandler(file_md5=file_md5,listen_path=listen_path)
    observer.schedule(event_handler, listen_path, True)
    observer.start()
    
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()