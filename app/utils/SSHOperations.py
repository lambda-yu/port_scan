import paramiko


class SSHOperating(object):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __init__(self, host, port, user_name, password):
        self.ssh_client.connect(host, port, user_name, password)
        self.sftp = self.ssh_client.open_sftp()

    def __getattr__(self, item):
        return self.ssh_client.__getattribute__(item)

    def is_exists(self, path):
        """检查文件是否存在"""
        return self._exec_command("ls {}".format(path))

    def is_file(self, path):
        """判断路径是否为文件"""
        flag = str(self.sftp.stat(path))[:1]
        return False if flag == "d" else True

    def pids_is_exists(self, pids: list):
        """判断任务是否存活"""
        _, out, err = self.exec_command("for pid in {} ;do ps aux | awk '{{print $2}}' | grep -w $pid ;done".format(
            " ".join(pids)))
        return [data.decode("utf-8") for data in out.read().split("\n")] if not err else []

    def check_job_completion(self, path):
        """任务进度检测，该目录下的所有进度一次性检测"""
        _, out, err = self.exec_command(r"for name in  `ls {}/*_status`; do echo $name  `cat $name | tr '\r\n' '\n'| "
                                        r"cat | grep remaining | sort -rn -k 3| head -1 | "
                                        r"awk '{{print $3}}'`; done".format(path))
        return [data.decode("utf-8") for data in out.read().split(b"\n")] if not err.read() else None

    def rm_file(self, *path):
        """删除文件夹或者文件"""
        return self._exec_command("rm -rf {}".format(" ".join(path)))

    def kill_jobs(self, *pid):
        """杀死某个任务"""
        return self._exec_command("kill -9 {}".format(" ".join(pid)))

    def like_kill_job(self, keywords):
        """模糊清理任务, 会杀死所有含有关键字的任务!!!"""
        return self._exec_command("ps aux | grep -w {} | grep -v grep | awk '{{print $2}}' | xargs kill -9"
                                  .format(keywords))

    def mk_dirs(self, *dirs):
        """批量创建多级文件夹"""
        return self._exec_command("for name in {};do `mkdir -p $name`; done".format(" ".join(dirs)))

    def chmod(self, *path):
        """更改文件的可执行权限"""
        return self._exec_command("for name in {};do `chmod +x $name`; done".format(" ".join(path)))

    def clean_dirs(self, *path):
        return self._exec_command("for name in {};do `rm -rf $name` `mkdir -p $name`; done".format(" ".join(path)))

    def _exec_command(self, command):
        _, _, err = self.exec_command(command)
        return False if err.read() else True


if __name__ == '__main__':
    a = SSHOperating(host="45.32.49.64", port=22, user_name="root", password="Rg1=B#UwJb2-tuZm")
    print(a.check_job_completion("/root/scan/logs/68234ce5-a447-4d5b-b7eb-85df9f1fb5e7_status"))

    # print("b" if b'123' else "a")