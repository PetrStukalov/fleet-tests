# https://www.opennet.ru/base/net/iptables_treasures.txt.html
# locust -f locustfile.py
from locust import User, task, between
from locust.clients import HttpSession
import os

from k8s_client import K8sClient
import time


class K8sUser(User):
    wait_time = between(1, 30)

    def __init__(self, environment):
        super().__init__(environment)
        self.client = K8sClient()
        self.session = HttpSession(
            base_url="http://%s:%s/" % (self.host, self.client.id),
            request_event=self.environment.events.request,
            user=self
        )

    def deploy(self):
        is_ok = True
        start_time = time.perf_counter()
        request_meta = {
            "request_type": "K8S",
            "name": "Deploy",
            "response_length": 0,
            "exception": None,
            "context": None,
            "response": None,
        }

        try:
            self.client.deploy()
            request_meta["response"] = "OK"
            request_meta["response_length"] = 2
        except Exception as e:
            request_meta["exception"] = e
            is_ok = False

        request_meta["response_time"] = (time.perf_counter() - start_time) * 1000
        self.environment.events.request.fire(**request_meta)
        return is_ok

    def delete(self):
        is_ok = True
        start_time = time.perf_counter()
        request_meta = {
            "request_type": "K8S",
            "name": "Delete",
            "response_length": 0,
            "exception": None,
            "context": None,
            "response": None,
        }

        try:
            self.client.delete()
            request_meta["response"] = "OK"
            request_meta["response_length"] = 2
        except Exception as e:
            request_meta["exception"] = e
            is_ok = False

        request_meta["response_time"] = (time.perf_counter() - start_time) * 1000
        self.environment.events.request.fire(**request_meta)
        return is_ok

    @task
    def do(self):
        self.deploy()
        for x in range(1000):
            r = self.session.get("/", name="Test")
            if r.ok:
                break
        self.delete()

    def on_stop(self):
        if self.client.deployed:
            self.client.delete()

# k = K8sClient()
# k.deploy()
