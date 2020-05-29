import json
from collections import namedtuple


class CodeMsg(object):
    CM = namedtuple("CM", "code, msg")
    SUCCESS = CM(200, "success")
    ERROR = CM(500, "error")
    FORBIDDEN = CM(403, "args is not incomplete")


def create_respose(ret_cm, msg=None, data=None):
    ret = CommonJsonRet(code=ret_cm.code, msg=ret_cm.msg if msg is None else msg, data=data)
    return ret.to_json()


class CommonJsonRet(object):
    def __init__(self, code, msg, data):
        self.code = code
        self.msg = msg
        self.data = data

    def to_str(self):
        return json.dumps(self.__dict__)

    def to_json(self):
        return self.__dict__


if __name__ == '__main__':
    print(create_respose(CodeMsg.SUCCESS))