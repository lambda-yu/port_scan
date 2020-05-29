import os
from flask import Flask
from flask_restplus import Api

from config import config_dict
from app.utils.SSHOperations import SSHOperating
from app.utils.localOperations import LocalOperations
from app.utils.common import RemoteControl, Jobs, ResultQueue


def create_app(model_name: str):
    app = Flask(__name__)
    app.config.from_object(config_dict[model_name])
    app.base_path = os.path.dirname(os.path.dirname(__file__))

    # 获取本地IP以及开放端口
    ip = os.popen("curl ifconfig.me 2> /dev/null").read()
    app.local_host = ip + ":" + app.config["LOCAL_PORT"]

    # 任务配置
    app.job_dict = {}
    for sub_dic in app.config["SUBS"]:
        app.job_dict.update({sub_dic["host"]: {k: v for k, v in sub_dic.items() if "job" in k}})

    app.running_jobs = dict()

    # 下载数据队列
    app.result_queue = ResultQueue(os.path.join(app.base_path, "result_queue_data"))

    # 本地操作类实例化,本地必要文件夹创建
    app.localOP = LocalOperations(app)
    app.localOP.make_base_dir()

    # 远程控制操作类实例化(远程必要文件夹创建, 推送脚本)
    app.remote_control = RemoteControl(app)

    # 创建任务操作类
    app.job = Jobs(app)

    api = Api(app, version="v1.0.0")

    from app.control.remote_control_api import control_ns
    api.add_namespace(control_ns, "/control")

    from app.health.remote_helth_api import health_ns
    api.add_namespace(health_ns, "/health")

    from app.job.job_control import job_ns
    api.add_namespace(job_ns, "/job")

    return app, api
