import atexit
import fcntl

from flask import jsonify
from flask_apscheduler import APScheduler

from app import create_app
from app.utils.common import ResultHandle, RemoteControl

app, api = create_app("product")

# 首先打开（或创建）一个scheduler.lock文件，并加上非阻塞互斥锁。成功后创建scheduler并启动。
f = open("scheduler.lock", "wb")
try:
    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    scheduler = APScheduler()
    scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()
    print("开启APScheduler成功")
    app.remote_control.remote_init()
except Exception as e:
    # 如果加文件锁失败，说明scheduler已经创建，就略过创建scheduler的部分。
    # logging.warning(f"定时任务启动错误:{str(ex)}")
    print(e)


# 最后注册一个退出事件，如果这个flask项目退出，则解锁并关闭scheduler.lock文件的锁。
def unlock():
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()


atexit.register(unlock)


# 创建两个数据获取进程
for _ in range(2):
    result_handle = ResultHandle(app.result_queue, app.remote_control.host_dict)
    result_handle.start()


# 统一404处理
@app.errorhandler(404)
def page_not_not_found(error):
    return jsonify({"code": 404, "msg": "this page is not exists"})


# 统一异常处理
@api.errorhandler
def default_error_handler(exception):
    # 异常栈写入
    return jsonify({"code": 500, "msg": "server error"})


@app.route('/map')
def route_map():
    """
    主视图，返回所有视图网址
    """
    rules_iterator = app.url_map.iter_rules()
    return jsonify({rule.endpoint: rule.rule for rule in rules_iterator if rule.endpoint not in ('route_map', 'static')})

