import json
import os
import time
import paramiko
import signal
from multiprocessing import Process, Queue, Lock

from app.utils.SSHOperations import SSHOperating


class RemoteControl(object):
    host_dict = {}
    _start_job_command = "bash /home/scan/scripts/masscan-scan.sh /home/scan/masscan/bin/masscan {} {} {} > " \
                         "/home/scan/logs/remote_test.log 2>&1 &"   # conf_path, pid_back, result_back
    _install_masscan_command = "bash /home/scan/scripts/install_masscan.sh &> /dev/null"

    def __init__(self, app):
        # 设置远程基础路径
        self._app = app
        dirs = ["data", "config", "logs", "scripts"]
        [self.__setattr__("remote_" + name, os.path.join(app.config["REMOTE_PATH"], name)) for name in dirs]
        self.remote_masscan = os.path.join(app.config["REMOTE_PATH"], "masscan")
        self.job_completion_path = os.path.join(app.config["REMOTE_PATH"], "logs")
        self.ssh = None
        self._pid_back = self._app.local_host + "/health/pid_back"
        self._result_back = self._app.local_host + "/health/result_back"

        # 将配置文加载入host_dict
        for ssh_host in app.config["SUBS"]:
            ssh_dict = {key: value for key, value in ssh_host.items() if "job" not in key}
            self.add_host(**ssh_dict)

    def add_host(self, host, port, user_name, password):
        """添加连接参数到全局字典"""
        self.host_dict.update({host: {
            "host": host,
            "port": port,
            "user_name": user_name,
            "password": password
        }})

    def set_ssh(self, host):
        """设置一个全局ssh"""
        assert host in self.host_dict.keys(), "This host is not in host_dict, please use add_host function to add"
        self.ssh = SSHOperating(**self.host_dict[host])
        return self.ssh

    def delete_remote_conf(self, hosts, ssh=None):
        """删除远程配置文件"""
        if "all" == hosts:
            for host in self.host_dict.values():
                ssh = SSHOperating(**host)
                ssh.rm_file(self.remote_config)
                ssh.mk_dirs(self.remote_config)
            return True
        else:
            for host in hosts:
                assert host in self.host_dict.keys(), "This host is not in host_dict, please use add_host function to add"
                ssh = self._check_ssh(ssh, **self.host_dict[host])
                ssh.rm_file(self.remote_config)
                ssh.mk_dirs(self.remote_config)
            return True

    def check_job(self, pids, host, ssh=None):
        ssh = self._check_ssh(ssh, host)
        pid_status = ssh.pids_is_exists(pids)
        completions = ssh.check_job_completion(self.job_completion_path)
        return pid_status, completions

    def install_remote_masscan(self, hosts, ssh=None):
        if "all" == hosts:
            for host in self.host_dict.values():
                ssh = SSHOperating(**host)
                ret = ssh.exec_command(self._install_masscan_command)
            return True
        else:
            for host in hosts:
                ssh = self._check_ssh(ssh, host)
                ret = ssh.exec_command(self._install_masscan_command)
            return ret

    def get_masscan_speed(self, hosts, ssh=None):
        pass

    def delete_remote_masscan(self, hosts, ssh=None):
        """删除远程masscan文件"""
        if "all" == hosts:
            for host in self.host_dict.values():
                ssh = SSHOperating(**host)
                ret = ssh.rm_file(os.path.join(self.remote_masscan))
            return True
        else:
            for host in hosts:
                ssh = self._check_ssh(ssh, host)
                ret = ssh.rm_file(self.remote_masscan)
            return True

    def check_remote_masscan(self, hosts, ssh=None):
        """检查远程masscan是否安装完成"""
        ret_list = {}
        if "all" == hosts:
            for host in self.host_dict.values():
                ssh = SSHOperating(**host)
                if ssh.is_exists(os.path.join(self.remote_masscan, "bin", "masscan")):
                    ret_list.update({host["host"]: True})
                else:
                    ret_list.update({host["host"]: False})
        else:
            for host in hosts:
                ssh = self._check_ssh(ssh, host)
                ssh.is_exists(os.path.join(self.remote_masscan, "bin", "masscan"))
                ret_list.update({host: True})
        return ret_list

    def check_remote_config(self, hosts, ssh=None):
        """检查远程配置文件是否正确"""
        ret_list = {}
        if "all" == hosts:
            for host in self.host_dict.values():
                ssh = SSHOperating(**host)
                ret_list.update(self._check_remote_config(ssh, host["host"]))
        else:
            for host in hosts:
                ssh = self._check_ssh(ssh, host)
                ret_list.update(self._check_remote_config(ssh, host))
        return ret_list

    def _check_remote_config(self, ssh, host):
        ret_list = {}
        # 获取本地配置文件
        if not os.path.exists(os.path.join(self._app.base_path, "JOBS", "conf", str(host))):
            return []
        local_confs = os.listdir(os.path.join(self._app.base_path, "JOBS", "conf", str(host)))
        # 获取远端配置文件
        remote_confs = ssh.sftp.listdir(self.remote_config)
        # 检查是否一致
        if local_confs.sort() == remote_confs.sort():
            ret_list.update({host: True})
        else:
            ret_list.update({host: False})
        return ret_list

    def put_config(self, hosts, ssh=None):
        """配置文件推送"""
        if "all" == hosts:
            for host in self.host_dict.values():
                ssh = SSHOperating(**host)
                self._put_config(ssh, host["host"])
            return True
        else:
            for host in hosts:
                ssh = self._check_ssh(ssh, host)
                self._put_config(ssh, self.host_dict[host])
            return True

    def put_scripts(self, hosts, ssh=None):
        """脚本推送"""
        if "all" == hosts:
            for host in self.host_dict.values():
                ssh = SSHOperating(**host)
                self._put_script(ssh)
            return True
        else:
            for host in hosts:
                ssh = self._check_ssh(ssh, host)
                self._put_script(ssh)
            return True

    def reset_remote(self, hosts, ssh=None):
        """重置远程主机"""
        if "all" == hosts:
            self.delete_remote_masscan("all")
            self._app.localOP.clean_conf("all")
        else:
            for host in hosts:
                ssh = self._check_ssh(ssh, host)
                self.delete_remote_masscan([host], ssh)
                self._app.localOP.clean_conf([host])

    def start_job(self, host):
        assert host in self.host_dict.keys(), "This host is not in host_dict, please use add_host function to add"
        ssh = SSHOperating(**self.host_dict[host])
        # 获得所有配置文件
        for name in ssh.sftp.listdir(self.remote_config):
            ssh.exec_command(self._start_job_command.format(self.remote_config + "/{}".format(name),
                                                            self._pid_back, self._result_back))

    def _put_config(self, ssh, host):
        ssh.clean_dirs(self.remote_config)
        for name in os.listdir(os.path.join(self._app.base_path, "JOBS", "conf", str(host))):
            remote_name = os.path.join(self.remote_config, name)
            ssh.sftp.put(os.path.join(self._app.base_path, "JOBS", "conf", str(host), name), remote_name)

    def _put_script(self, ssh):
        names = []
        ssh.clean_dirs(self.remote_scripts)
        for name in os.listdir(os.path.join(self._app.base_path, "scripts")):
            remote_name = os.path.join(self.remote_scripts, name)
            ssh.sftp.put(os.path.join(self._app.base_path, "scripts", name), remote_name)
            names.append(remote_name)
        ssh.chmod(*names)

    def remote_init(self):
        for host in self.host_dict.values():
            ssh = SSHOperating(**host)
            # 删除远程脚本文件夹
            ssh.rm_file(self.remote_scripts)
            # 创建远程所需文件夹
            ssh.mk_dirs(*[v for k, v in self.__dict__.items() if "remote_" in k])
            self.put_scripts([host["host"]], ssh)
            self.install_remote_masscan([host["host"]], ssh)
            print(host["host"] + "加载配置成功")

    def _check_ssh(self, ssh, host):
        assert host in self.host_dict.keys(), "This host is not in host_dict, please use add_host function to add"
        return SSHOperating(**self.host_dict[host]) if ssh is None else ssh


class Jobs(object):
    def __init__(self, app):
        self._app = app

    def reset_jobs(self, hosts):
        pass

    def start_job(self, hosts):
        if "all" == hosts:
            # 检查msscan是否安装
            masscan_check_dict = self._app.remote_control.check_remote_masscan("all")
            # 检查配置文件是否推送完成
            config_check_dict = self._app.remote_control.check_remote_config("all")
        else:
            # 检查msscan是否安装
            masscan_check_dict = self._app.remote_control.check_remote_masscan(hosts)
            # 检查配置文件是否推送完成
            config_check_dict = self._app.remote_control.check_remote_config(hosts)

        for key, value in masscan_check_dict.items():
            if value and config_check_dict and config_check_dict[key]:
                # 检查任务是否已经运行
                self._app.remote_control.start_job(key)
            else:
                return {"masscan_check": masscan_check_dict, "config_check": config_check_dict}

    def split_jobs(self, start, stop, num):
        """分割任务"""
        stop = int(stop)
        start = int(start)
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
        return ["{}-{}".format(min(temp), max(temp)) if min(temp) != max(temp) else "{}".format(max(temp)) for temp in temp_array if temp]

    def job_dispatch(self, max_speed: float, remote_addr: str):
        conf_path = os.path.join(self._app.base_path, "JOBS", "conf", remote_addr)
        if os.path.exists(conf_path) and not os.listdir(conf_path):
            return

        # 计算任务数量
        job_num = int(max_speed * 0.8 / 10)
        # 获得配置
        rate = self._app.config["REMOTE_RUN_PPS"]     # 单个任务扫描速度
        job_host = self._app.job_dict[remote_addr]  # 远程主机地址

        # 解析ip,分配ip
        ip = job_host["job_host"]
        ip_array = ip.split(".")
        job_ip = []
        for i in range(len(ip_array)):
            if "-" in ip_array[i]:
                temp = self.split_jobs(ip_array[i].split("-")[0], ip_array[i].split("-")[1], job_num)
                for ip in temp:
                    if "-" in ip:
                        ips = ip.split("-")
                        ip_array_1 = ip_array.copy()
                        ip_array[i] = ips[0]
                        ip_array_1[i] = ips[1]
                        job_ip.append(".".join(ip_array)+"-"+".".join(ip_array_1))
                    else:
                        ip_array[i] = ip
                        job_ip.append(".".join(ip_array)+"/{}".format((i+1)*8))
                break

        for ip in job_ip:
            self._app.localOP.save_conf(run_enable="true", host=ip, rate=rate, remote_addr=remote_addr,
                                        port=self._app.job_dict[remote_addr]["job_port"])
        self._app.remote_control.put_config("all")


class ResultQueue(object):
    def __init__(self, local_path):
        self._queue = Queue()
        self.lock = Lock()
        signal.signal(signal.SIGTERM, self._exit_handle)
        self.local_path = local_path
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)
        self.path = os.path.join(self.local_path, "result_data")
        if os.path.exists(os.path.join(self.local_path, "back_data")):
            self.load_data()

    def result_put(self, data):
        # 进行本地备份
        self.lock.acquire()
        datas = []
        if os.path.exists(self.path):
            with open(os.path.join(self.local_path, "result_data"), "r") as file:
                datas = file.readlines()

        with open(os.path.join(self.local_path, "result_data"), "w") as file:
            datas.append(json.dumps(data) + "\n")
            file.writelines(datas)
        self.lock.release()
        # 推送队列
        self._queue.put(data)

    def result_get(self):
        data = self._queue.get()
        self.lock.acquire()
        datas = []
        if os.path.exists(self.path):
            with open(os.path.join(self.local_path, "result_data"), "r") as file:
                datas = file.readlines()
                datas.remove(json.dumps(data) + "\n")

        with open(os.path.join(self.local_path, "result_data"), "w") as file:
            file.writelines(datas)
        self.lock.release()
        return data

    def load_data(self):
        # 加载本地备份数据, 重启后加载
        with open(os.path.join(self.local_path, "back_data"), "r") as file:
            datas = file.readlines()
        datas = [json.loads(data) for data in datas]
        for data in datas:
            self.result_put(data)

    def _exit_handle(self, signum, frame):
        # 退出处理函数,作数据备份处理
        datas = []
        while True:
            data = self._queue.get_nowait()
            if data is None:
                break
            datas.append(data)
        # 保存到本地
        with open(os.path.join(self.local_path, "back_data"), "w") as file:
            file.writelines([json.dumps(data) + "\n" for data in datas])
        os.remove(os.path.join(self.local_path, "result_data"))


class ResultHandle(Process):
    def __init__(self, queue, host_dict):
        super().__init__()
        self.queue = queue
        self.host_dict = host_dict
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def run(self) -> None:
        """{"host": "", "remote_path": "", "local_path": ""}"""
        while True:
            data = self.queue.result_get()
            host = data["host"]
            try:
                self.ssh_client.connect(hostname=host, port=self.host_dict[host]["port"],
                                        username=self.host_dict[host]["user_name"],
                                        password=self.host_dict[host]["password"])
                self.sftp = self.ssh_client.open_sftp()
            except Exception as e:
                self.queue.result_put(data)
                time.sleep(5)
                continue
            local_path = data["local_path"]
            remote_path = data["remote_path"]
            if not os.path.exists(local_path):
                os.makedirs(local_path)
            file_name = os.path.split(remote_path)[1]

            self.sftp.get(remote_path, os.path.join(local_path, file_name))
            self.ssh_client.close()


if __name__ == '__main__':
    # c = Control()
    # c.init_ssh_client("207.246.125.196", 22, "root", "p4.J#o!UD+Yfg)ds")
    # c.init_ssh_client("45.63.23.164", 22, "root", "=hG3)#],fTq6R5V8")
    # a = c.ssh_client.open_sftp()
    #
    # d = {"c": 2}
    # d.update({"c": 3})
    # print(d)
    # a = SSHOperating("207.246.125.196", 22, "root", "p4.J#o!UD+Yfg)ds")
    # a.test()
    # a,b,c = a.exec_command("ls -l")
    # print(b.read())
    # print(hasattr(a, "test"))
    # test = SSHOperating("207.246.125.196", 22, "root", "p4.J#o!UD+Yfg)ds")
    # test.pid_is_exists("1")
    # {
    #     "host": "45.63.23.164",
    #     "port": 22,
    #     "user_name": "root",
    #     "password": "=hG3)#],fTq6R5V8",
    #     "job_port": "80",
    #     "job_host": "168-192.0.0.0",
    # },
    a = [1,2,3]
    b = [1]
    print(b in a)
    a = "a/b/c/d.txt"
    c = os.path.split(a)
    print(c)