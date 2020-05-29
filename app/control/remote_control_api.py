from flask_restplus import Namespace, Resource, reqparse
from flask import current_app

from app.utils.code_msg import create_respose, CodeMsg

control_ns = Namespace("control")


@control_ns.route("/delete_remote_config")
class DeleteRemoteConfig(Resource):
    @control_ns.doc(
        params={"Host": "某一个具体主机或者 all"},
        description="删除远程主机的配置文件"
    )
    def delete(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("Host", type=str, location="args")
        params = _parse.parse_args()
        host = params["Host"]

        if "all" in host:
            hosts = "all"
        elif isinstance(host, str):
            hosts = [host]
        else:
            return create_respose(CodeMsg.FORBIDDEN)

        try:
            current_app.remote_control.delete_remote_conf(hosts)
        except AssertionError:
            return create_respose(CodeMsg.ERROR, data=str("host error"))
        return create_respose(CodeMsg.SUCCESS)


@control_ns.route("/delete_remote_masscan")
class DeleteRemoteMasscan(Resource):
    @control_ns.doc(
        params={"Host": "某一个具体主机或者 all"},
        description="删除远程主机的masscan"
    )
    def delete(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("Host", type=str, location="args")
        params = _parse.parse_args()
        host = params["Host"]
        if "all" in host:
            hosts = "all"
        elif isinstance(host, str):
            hosts = [host]
        else:
            return create_respose(CodeMsg.FORBIDDEN)

        try:
            ret = current_app.remote_control.delete_remote_masscan(hosts)
        except AssertionError:
            return create_respose(CodeMsg.ERROR, data=str("host error"))
        return create_respose(CodeMsg.SUCCESS, msg=ret)


@control_ns.route("/install_remote_masscan")
class DeleteRemoteMasscan(Resource):
    @control_ns.doc(
        params={"Host": "某一个具体主机或者 all"},
        description="安装远程主机的masscan"
    )
    def delete(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("Host", type=str, location="args")
        params = _parse.parse_args()
        host = params["Host"]
        if "all" in host:
            hosts = "all"
        elif isinstance(host, str):
            hosts = [host]
        else:
            return create_respose(CodeMsg.FORBIDDEN)

        try:
            ret = current_app.remote_control.install_remote_masscan(hosts)
        except AssertionError:
            return create_respose(CodeMsg.ERROR, data=str("host error"))
        return create_respose(CodeMsg.SUCCESS, msg=ret)


@control_ns.route("/delete_local_config")
class DeleteLocalConfig(Resource):
    @control_ns.doc(
        params={"Host": "某一个具体主机或者 all"},
        description="删除本地配置文件"
    )
    def delete(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("Host", type=str, location="args")
        params = _parse.parse_args()
        host = params["Host"]

        if "all" in host:
            hosts = "all"
        elif isinstance(host, str):
            hosts = [host]
        else:
            return create_respose(CodeMsg.FORBIDDEN)

        try:
            current_app.localOP.clean_conf(hosts)
        except Exception as e:
            return create_respose(CodeMsg.ERROR, msg=str(e))
        return create_respose(CodeMsg.SUCCESS)


@control_ns.route("/put_config")
class PutConfig(Resource):
    def get(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("Host", type=str, location="args")
        params = _parse.parse_args()
        host = params["Host"]

        if "all" in host:
            hosts = "all"
        elif isinstance(host, str):
            hosts = [host]
        else:
            return create_respose(CodeMsg.FORBIDDEN)

        try:
            current_app.remote_control.put_config(hosts)
        except Exception as e:
            return create_respose(CodeMsg.ERROR, msg=str(e))
        return create_respose(CodeMsg.SUCCESS)


@control_ns.route("/reset_remote")
class ResetRemote(Resource):
    @control_ns.doc(
        params={"Host": "某一个具体主机地址或者 all"},
        description="重置远程主机, 删除masscan、本地配置文件"
    )
    def get(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("Host", type=str, location="args")
        params = _parse.parse_args()
        host = params["Host"]

        if "all" in host:
            hosts = "all"
        elif isinstance(host, str):
            hosts = [host]
        else:
            return create_respose(CodeMsg.FORBIDDEN)

        try:
            current_app.remote_control.reset_remote(hosts)
        except Exception as e:
            return create_respose(CodeMsg.ERROR, msg=str(e))
        return create_respose(CodeMsg.SUCCESS)


@control_ns.route("/start")
class StartJob(Resource):
    def get(self):
        _parse = reqparse.RequestParser()
        _parse.add_argument("Host", type=str, location="args")
        params = _parse.parse_args()
        host = params["Host"]

        if "all" in host:
            hosts = "all"
        elif isinstance(host, str):
            hosts = [host]
        else:
            return create_respose(CodeMsg.FORBIDDEN)
        ret_data = current_app.job.start_job(hosts)
        return create_respose(CodeMsg.SUCCESS, data=ret_data)
