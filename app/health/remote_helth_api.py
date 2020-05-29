import json

from flask import request, current_app
from flask_restplus import Namespace, Resource, reqparse
from concurrent.futures import ThreadPoolExecutor

from app.utils.code_msg import create_respose, CodeMsg

health_ns = Namespace("health")

execute = ThreadPoolExecutor(max_workers=10)


@health_ns.route("/test_back")
class TestBack(Resource):
    def post(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("cpu", type=str, location="json")
        _parse.add_argument("memory_free", type=str, location="json")
        _parse.add_argument("disk_free", type=str, location="json")
        _parse.add_argument("masscan", type=str, location="json")
        _parse.add_argument("max_speed", location="json")
        data = _parse.parse_args()
        remote_addr = request.remote_addr

        if not all([v for k, v in data.items() if k != "max_speed"]):
            return create_respose(CodeMsg.FORBIDDEN)

        max_speed = data["max_speed"]
        if max_speed:
            max_speed = float(max_speed.split("-")[0])
            if max_speed > 0:
                current_app.job.job_dispatch(max_speed, remote_addr)  # 需要做异步处理, 进程
        data = current_app.localOP.save_detail(remote_addr, data)
        return create_respose(CodeMsg.SUCCESS, data)


@health_ns.route("/pid_back")
class PidBack(Resource):
    def post(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("job_id", type=str, location="json")
        _parse.add_argument("job_pid", type=str, location="json")
        _parse.add_argument("masscan_pid", type=str, location="json")
        data = _parse.parse_args()
        remote_addr = request.remote_addr
        job_id = data["job_id"]
        job_pid = data["job_pid"]
        masscan_pid = data["masscan_pid"]
        if job_id is None:
            return create_respose(CodeMsg.FORBIDDEN)

        data = current_app.localOP.save_pid(remote_addr, job_id, job_pid, masscan_pid)

        return create_respose(CodeMsg.SUCCESS, data=data)

    def get(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("Host", type=str, location="args")
        params = _parse.parse_args()
        host = params["Host"]
        return create_respose(CodeMsg.SUCCESS, data=current_app.localOP.read_pid(host))


@health_ns.route("/job_status")
class PidBack(Resource):
    def get(self):
        return create_respose(CodeMsg.SUCCESS, data=current_app.running_jobs)


@health_ns.route("/result_back")
class JobResultBack(Resource):
    def post(self):
        request_data = json.loads(request.data.decode("utf-8"))
        remote_addr = request.remote_addr
        status = request_data.get("status")
        if status != "success":
            return create_respose(CodeMsg.FORBIDDEN)

        data_dict = {
            "host": remote_addr,
            "remote_path": request_data["data_path"],
            "local_path": current_app.config["LOCAL_DATA_SAVE_PATH"]
        }

        current_app.result_queue.result_put(data_dict)

        return create_respose(CodeMsg.SUCCESS)


@health_ns.route("/ssh_status")
class SubsStatus(Resource):
    def get(self):
        datas = current_app.localOP.read_ssh_status()
        return create_respose(CodeMsg.SUCCESS, data=datas)


@health_ns.route("/remote_detail")
class SubsDetail(Resource):
    def get(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("Host", type=str, location="args")
        params = _parse.parse_args()
        host = params["Host"]

        if host is None:
            return create_respose(CodeMsg.FORBIDDEN)
        if "all" in host:
            hosts = current_app.remote_control.host_dict.keys()
        else:
            hosts = [host]

        detail_list = current_app.localOP.read_detail(hosts)

        return create_respose(CodeMsg.SUCCESS, data=detail_list)
