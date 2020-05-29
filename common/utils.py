import paramiko
import sys


def test_ssh(app):
    """测试所有SSH连接是否有效！启动项目前检查"""
    ssh_list = app.config["SUB_HOST"]
    err_list = []
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for ssh_data in ssh_list:
        try:
            ssh.connect(hostname=ssh_data["host"], port=ssh_data["port"],
                        username=ssh_data["user_name"], password=ssh_data["password"])
        except Exception as e:
            err_list.append(ssh_data)
            continue

    if err_list:
        for err in err_list:
            print("{} connect error".format(err["host"]))
        sys.exit(1)
    else:
        print("all ssh connect success")
