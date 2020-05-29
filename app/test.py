# import paramiko
#
#
# # ssh = paramiko.SSHClient()
# # #把要连接的机器添加到known_hosts文件中
# # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# # ssh.connect(hostname="139.196.78.228", port=22, username="root", password="YUliuguang0624?")
# # # _, a, _ = ssh.exec_command("pwd")
# # # print(a.read())
# try:
#     transport = paramiko.Transport("139.196.78.229", 22)
#     transport.connect(username="root", password="YUliuguang0624?")
#     sftp = paramiko.SFTPClient.from_transport(transport)
#
# except Exception as e:
#     print(e)
# import uuid
#
# print(uuid.uuid4())
# a = {"1":1, "2":2}
# for key, value in a.items():
#     print(key, value)
import datetime
import json
import os
import time
from multiprocessing import Process, Queue
from math import ceil

import paramiko


def split_jobs(start, stop, num):
    a = int((stop-start+1) / num)
    c = int((stop-start+1) % num)
    flag = 0
    temp_array = []
    for i in range(num):
        if i < c:
            temp_array.append(list(range(start, stop+1))[flag:flag+a+1])
            flag += a + 1
        else:
            temp_array.append(list(range(start, stop+1))[flag:flag+a])
            flag += a
    return ["{}-{}".format(min(temp), max(temp)) if min(temp) != max(temp) else "{}".format(max(temp)) for temp in temp_array]





if __name__ == '__main__':
    # a = ["a"]
    # print(" ".join(a))
    # a = os.popen("curl ifconfig.me 2> /dev/null").read()
    # print(a)
    # os.makedirs("/root/scan/test", exist_ok=True)
    # os.makedirs("/root/scan/test", exist_ok=True)
    q = Queue()
    a = Result_handle(q, "a")
    a.start()
    b = Result_handle(q, "a")
    b.start()
    time.sleep(5)
    q.put({"a": 1})
    q.put("2")