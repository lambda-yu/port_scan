import datetime

import paramiko
from flask import current_app
from app.main import scheduler


def remote_health_check():
    """远程主机状态检查"""
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    with scheduler.app.app_context():
        for _, ssh_name in current_app.remote_control.host_dict.items():
            try:
                ssh_client.connect(hostname=ssh_name["host"], port=ssh_name["port"],
                                   username=ssh_name["user_name"], password=ssh_name["password"], timeout=30)
            except Exception as e:
                print("{} ssh connect error".format(ssh_name["host"]))
            ssh_client.exec_command("bash /home/scan/scripts/remote_test.sh /home/scan/masscan/bin/masscan "
                                    "http://{}/health/test_back > /home/scan/logs/remote_test.log 2>&1 &".format(current_app.local_host))
            ssh_client.close()


def ssh_health_check():
    """ssh连通性检查"""
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    with scheduler.app.app_context():
        temp_list = []
        for _, ssh_name in current_app.remote_control.host_dict.items():
            try:
                ssh_client.connect(hostname=ssh_name["host"], port=ssh_name["port"],
                                   username=ssh_name["user_name"], password=ssh_name["password"], timeout=30)
                status = "connect_success"
                ssh_client.close()
            except Exception as e:
                status = "connect_error"
            temp_list.append({"host": ssh_name["host"], "status": status,
                              "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        current_app.localOP.save_ssh_status(temp_list)  # 保存到本地


def jobs_health_check():
    """任务健康检查"""
    with scheduler.app.app_context():
        # 读取本地pid文件
        pid_dict = current_app.localOP.read_pid("all")
        ret_dict = {}
        for host, pids in pid_dict.items():
            # 创建SSH连接
            ret = {"is_running": False, "completion": "0%"}
            pid_list = [pid["job_pid"] for pid in pids if pid["job_pid"]]
            pid_status, completions = current_app.remote_control.check_job(pid_list, host)
            completion_dict = {data.split(" ")[0].split("_")[0]: data.split(" ")[0] for data in completions}
            for pid in pids:
                if pid["job_pid"] in pid_status:
                    ret.update({"is_running": True, "completion": completion_dict[pid["job_id"]]})
                ret.update({"update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                ret_dict.update({pid["job_id"]: ret})
            current_app.running_jobs.update({host: ret_dict})
