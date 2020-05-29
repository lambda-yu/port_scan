

class Config(object):
    REMOTE_PATH = r"/home/scan"    # 服务器目录工作目录
    REMOTE_RUN_PPS = 10000     # 每台服务器任务的扫描速度
    REMOTE_DATA_SAVE_PATH = r"/home/scan/data"
    LOCAL_DATA_SAVE_PATH = r"/scan_result_data"

    JOBS = [
        {
            'id': 'remote_health_check.job',
            'func': 'app.health.tasks:remote_health_check',
            'args': (),
            'trigger': 'interval',
            'seconds': 180,
            'replace_existing': True,
            'coalesce': True,
            'misfire_grace_time': 20,
        },
        {
            'id': 'ssh_health_check.job',
            'func': 'app.health.tasks:ssh_health_check',
            'args': (),
            'trigger': 'interval',
            'seconds': 300,
            'replace_existing': True,
            'coalesce': True,
            'misfire_grace_time': 100,
        },
        {
            'id': 'jobs_health_check.job',
            'func': 'app.health.tasks:jobs_health_check',
            'args': (),
            'trigger': 'interval',
            'seconds': 60,
            'replace_existing': True,
            'coalesce': True,
            'misfire_grace_time': 20,
        },
    ]


class Product(Config):
    DEBUG = False
    LOCAL_PORT = "8080"
    SUBS = [
        {
            "host": "167.179.75.118",
            "port": 22,
            "user_name": "root",
            "password": "M5v@PFv2B5)Kbv,y",
            "job_port": "80",
            "job_host": "0-5.0.0.0",  # 推荐格式  10-20.0.0.0
        },
        {
            "host": "108.61.187.35",
            "port": 22,
            "user_name": "root",
            "password": "5Gb-ccmEzqS{8xLA",
            "job_port": "80",
            "job_host": "6-10.0.0.0",  # 推荐格式  10-20.0.0.0
        },
        {
            "host": "167.179.81.87",
            "port": 22,
            "user_name": "root",
            "password": "{Pu1K2%kW$q,prmR",
            "job_port": "80",
            "job_host": "11-15.0.0.0",  # 推荐格式  10-20.0.0.0
        },
        {
            "host": "108.61.250.63",
            "port": 22,
            "user_name": "root",
            "password": "5[yP[m.4M+5@KyUH",
            "job_port": "80",
            "job_host": "16-20.0.0.0",  # 推荐格式  10-20.0.0.0
        },
        {
            "host": "207.148.110.60",
            "port": 22,
            "user_name": "root",
            "password": "-z7XdjYw5EdL5*r_",
            "job_port": "80",
            "job_host": "21-25.0.0.0",  # 推荐格式  10-20.0.0.0
        },
        {
            "host": "45.77.182.246",
            "port": 22,
            "user_name": "root",
            "password": "7}GdGwh$K=YN)tac",
            "job_port": "80",
            "job_host": "26-30.0.0.0",  # 推荐格式  10-20.0.0.0
        },
        {
            "host": "198.13.61.242",
            "port": 22,
            "user_name": "root",
            "password": "Lg@4c?aFV_NF@W7W",
            "job_port": "80",
            "job_host": "31-35.0.0.0",  # 推荐格式  10-20.0.0.0
        },

    ]


class Development(Config):
    DEBUG = True
    LOCAL_PORT = "8080"
    SUBS = [
        {
            "host": "45.32.49.64",
            "port": 22,
            "user_name": "root",
            "password": "Rg1=B#UwJb2-tuZm",
            "job_port": "80",
            "job_host": "190-192.0.0.0",  # 推荐格式  10-20.0.0.0
        },
        # {
        #     "host": "45.76.50.199",
        #     "port": 22,
        #     "user_name": "root",
        #     "password": "3W@gC7KGG-[)x$jc",
        #     "job_port": "80",
        #     "job_host": "168-192.0.0.0",
        # },
        # {
        #     "host": "139.180.196.246",
        #     "port": 22,
        #     "user_name": "root",
        #     "password": "cD5)yK6dMhTCz[Nx",
        #     "job_port": "80",
        #     "job_host": "168-192.0.0.0",
        # },
        # {
        #     "host": "167.179.103.216",
        #     "port": 22,
        #     "user_name": "root",
        #     "password": "G4d*nh$dYBREdL-L",
        #     "job_port": "80",
        #     "job_host": "168-192.0.0.0",
        # },
        # {
        #     "host": "139.180.193.192",
        #     "port": 22,
        #     "user_name": "root",
        #     "password": "w+4RpU$b$GRwojE!",
        #     "job_port": "80",
        #     "job_host": "168-192.0.0.0",
        # },
    ]


config_dict = {
    "product": Product,
    "development": Development
}
