import time

localtime = time.asctime( time.localtime(time.time()) )
print(type(localtime))