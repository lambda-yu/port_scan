import json
import os
import shutil
import uuid
from datetime import datetime
from itertools import chain


class LocalOperations(object):
    def __init__(self, current_app):
        self.pid_path = os.path.join(current_app.base_path, "JOBS", "pid")
        self.status_path = os.path.join(current_app.base_path, "JOBS", "status")
        self.conf_path = os.path.join(current_app.base_path, "JOBS", "conf")
        self.remote_save = current_app.config["REMOTE_DATA_SAVE_PATH"]  # 远程数据存储地址

    @staticmethod
    def make_dirs(*paths):
        """批量创建文件夹"""
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)

    def make_base_dir(self):
        self.make_dirs(*[v for k, v in self.__dict__.items() if "path" in k])

    def clean_conf(self, hosts):
        if "all" == hosts:
            shutil.rmtree(self.conf_path)
            self.make_dirs(self.conf_path)
        else:
            for host in hosts:
                shutil.rmtree(os.path.join(self.conf_path, str(host)))
                self.make_dirs(os.path.join(self.conf_path, str(host)))

    def save_pid(self, host, job_id, job_pid, masscan_pid=None):
        pid_dict = {
            "job_id": job_id,
            "job_pid": job_pid,
            "masscan_pid": masscan_pid if masscan_pid is None else str(int(masscan_pid)),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if os.path.exists(os.path.join(self.pid_path, host)):
            datas_dict = self.read_pid(host)
            for host, pids in datas_dict.items():
                for pid in pids:
                    if job_id == pid["job_id"]:
                        pids.remove(pid)
                        pid_dict.update({"job_pid": pid["job_pid"] if job_pid is None else job_pid})
                datas = [json.dumps(pid)+"\n" for pid in pids]
                datas.append(json.dumps(pid_dict)+"\n")
                self._write_file(os.path.join(self.pid_path, host), datas)
        else:
            self._write_file(os.path.join(self.pid_path, host), json.dumps(pid_dict) + "\n")
        return pid_dict

    def read_pid(self, host):
        if host == "all":
            ret_dict = {}
            names = os.listdir(self.pid_path)
            for name in names:
                datas = self._read_file(os.path.join(self.pid_path, name))
                datas = [json.loads(data) for data in datas]
                ret_dict.update({name: datas})
            return ret_dict
        else:
            if host in os.listdir(self.pid_path):
                datas = self._read_file(os.path.join(self.pid_path, host))
                datas = [json.loads(data) for data in datas]
                return {host: datas}
            else:
                return {}

    def save_job_status(self):
        pass

    def read_job_status(self):
        pass

    def save_conf(self, run_enable=None, host=None, port=None, rate=None, remote_addr=None, job_id=None):
        conf_dict = {
            "run_enable": run_enable,
            "host": host,
            "port": port,
            "rate": rate,
            "save_path": self.remote_save,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        os.makedirs(os.path.join(self.conf_path, str(remote_addr)), exist_ok=True)

        if job_id is None:
            # 生成配置文件
            job_id = uuid.uuid4()
            path = os.path.join(self.conf_path, str(remote_addr), "{}.conf".format(job_id))
            data = self._write_file(path, ["=".join([key, str(value)+"\n"]) for key, value in conf_dict.items()])
            return data

        else:
            # 更新配置文件
            for name in os.listdir(os.path.join(self.conf_path, str(remote_addr))):
                if job_id in name:
                    datas = self._read_file(os.path.join(self.conf_path, str(remote_addr), name))
                    data_dict = {data.split(": ")[0]: data.split(": ")[1] if conf_dict[data.split(": ")[0]] is None else
                                 str(conf_dict[data.split(": ")[0]])+"\n" for data in datas}
                    data = self._write_file(os.path.join(self.conf_path, str(remote_addr), name), data_dict)
                    return data
            else:
                return None

    def read_conf(self, job_id=None, host=None):
        ret_list = []
        for name in os.listdir(self.conf_path):
            if job_id or host in name:
                datas = self._read_file(os.path.join(self.conf_path, name))
                data_dict = {data.split(": ")[0]: data.split(": ")[1] for data in datas}
                ret_list.append(data_dict)
        return ret_list

    def save_detail(self, remote_addr, data_dict):
        data_dict["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if os.path.exists(os.path.join(self.status_path, "{}_detail".format(remote_addr))):
            with open(os.path.join(self.status_path, "{}_detail".format(remote_addr)), "r") as file:
                old_data = [data.replace("\n", "") for data in file.readlines()]
                temp_dict = dict([tuple(data.split(": ")) for data in old_data])
        else:
            temp_dict = data_dict.copy()

        with open(os.path.join(self.status_path, "{}_detail".format(remote_addr)), "w") as file:
            datas = [[key, ": ", value or temp_dict[key], "\n"] for key, value in data_dict.items()]
            data = [data for data in chain(*datas)]
            file.writelines(data)
        return data

    def read_detail(self, hosts):
        host_str = "".join(hosts)
        detail_list = []
        for file_name in os.listdir(self.status_path):
            if "_detail" in file_name:
                file_host = file_name.split("_")[0]
                if file_host in host_str:
                    with open(os.path.join(self.status_path, file_name), "r") as file:
                        detail_dict = {data.split(": ")[0]: data.split(": ")[1].replace("\n", "") for data in
                                       file.readlines() if data not in ("\n", "")}
                        detail_dict.update({"host": file_host})
                        detail_list.append(detail_dict)
        return detail_list

    def save_ssh_status(self, data_list):
        with open(os.path.join(self.status_path, 'remote_ssh_status'), "w") as file:
            [file.writelines([json.dumps(status), "\n"]) for status in data_list]

    def read_ssh_status(self):
        files = self._read_file(os.path.join(self.status_path, 'remote_ssh_status'))
        return [json.loads(file) for file in files]

    @staticmethod
    def _read_file(path):
        with open(path, "r") as file:
            return file.readlines()
    
    @staticmethod
    def _write_file(path, data):
        with open(path, "w") as file:
            file.writelines(data)
            return data
