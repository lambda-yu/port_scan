import paramiko

from flask_script import Manager
from app.main import app

manager = Manager(app)


@manager.command
def test_ssh():
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
            print(e)
            err_list.append(ssh_data)
            continue

    if err_list:
        for err in err_list:
            print("{} connect error".format(err["host"]))
    else:
        print("all ssh connect success")


if __name__ == '__main__':
    manager.run()
