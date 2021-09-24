# https://www.opennet.ru/base/net/iptables_treasures.txt.html
#locust -f locustfile.py
from locust import User, task
from k8s_client import K8sClient
import time


class K8sUser(User):
    def __init__(self, environment):
        super().__init__(environment)
        self.client = K8sClient()

    @task
    def do(self):
        start_time = time.perf_counter()
        request_meta = {
            "request_type": "grpc",
            "name": "Test111",
            "response_length": 0,
            "exception": None,
            "context": None,
            "response": None,
        }

        try:
            self.client.deploy()
            self.client.service()
            self.client.delete()
            request_meta["response"] = "OK"
            request_meta["response_length"] = 2
        except Exception as e:
            request_meta["exception"] = e

        request_meta["response_time"] = (time.perf_counter() - start_time) * 1000
        self.environment.events.request.fire(**request_meta)

    def on_stop(self):
        if self.client.deployed:
            self.client.delete()


#k = K8sClient()
#k.deploy()