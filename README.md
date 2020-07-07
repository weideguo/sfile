file sync server  
分布式文件同步。监听指定目录下的文件变化（不支持删），同步到其他服务。  


running
--------------
### version support ###
* python 2.7
* python 3.5

### prerun ###
```shell
#set config or copy from others
vim conf/key.conf 
#install dependency
pip install -r requirements.txt
#set env
export LC_ALL=en_US.UTF-8
```

### start ###
```shell
#show help
python bin/sfile.py --help

#start as master
python bin/sfile.py --default_path=/tmp/a --bind=127.0.0.1:9010 --master
#start as slave
python bin/sfile.py --default_path=/tmp/b --conn_master=127.0.0.1:9010 --slave

#multi master in cluster
python bin/sfile.py --default_path=/tmp/a --bind=127.0.0.1:9010 --conn_master=127.0.0.1:9011,127.0.0.1:9012
python bin/sfile.py --default_path=/tmp/b --bind=127.0.0.1:9011 --conn_master=127.0.0.1:9010,127.0.0.1:9012
python bin/sfile.py --default_path=/tmp/c --bind=127.0.0.1:9012 --conn_master=127.0.0.1:9010,127.0.0.1:9011


```


desc
--------------
### 安全 ###
* 密码认证

* 通信加密  
  aes对称加密通信  
  rsa非对称加密通信  

### 部署架构 ###
可以动态加入与退出，主从信息记录在配置文件，且动态修改，加入时只需要设置另外一个主，其余主信息会自动同步  
主之间完全同步信息，监听端口回应请求，监听文件变化主动发出md5信息以及主信息，同时连接其他主  
从只能下拉文件，不监听端口不回应信息，不监听文件变化，不主动发送配置信息，只连接其他主  

* 单master模式 

* 单master-多slave模式 
  
* 多master模式 

* 多master-多slave模式 

