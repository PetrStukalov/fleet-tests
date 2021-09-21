from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes import client, watch
import yaml
import random


class K8sClient:
    def __init__(self):
        self.id = random.randint(0, 10000)
        config.load_kube_config(r"C:\Users\pstukalo\aws\ansible\roles\k8s_user\keys\config")
        c = Configuration().get_default_copy()
        c.assert_hostname = False
        Configuration.set_default(c)
        self.core_v1 = core_v1_api.CoreV1Api()
        self.k8s_apps_v1 = client.AppsV1Api()
        self.deployed = False

    def wait_pods(self, status: str, selector: str):
        """
        Waiting for pods status
        :param status: ADDED, MODIFIED, DELETED, RUNNING
        :param selector: ex: app=nginx
        :return:
        """
        w = watch.Watch()
        try:
            for event in w.stream(func=self.core_v1.list_namespaced_pod,
                                  namespace="default",
                                  label_selector=selector,
                                  timeout_seconds=60):
                if status == "RUNNING":
                    if event["object"].status.phase == "Running":
                        return
                else:
                    # event.type: ADDED, MODIFIED, DELETED
                    if event["type"] == status:
                        return
        finally:
            w.stop()

    def get_pods(self):
        ret = self.core_v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s\t%s\t%s" %
                  (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    def delete(self):
        self.k8s_apps_v1.delete_namespaced_deployment("nginx-deployment%s" % self.id, namespace="default")
        self.deployed = False
        self.wait_pods("DELETED", "app=nginx%s" % self.id)
        print("DELETED %s" % self.id)

    def deploy(self):
        txt = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment%s
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx%s
  template:
    metadata:
      labels:
        app: nginx%s
    spec:
      containers:
      - name: nginx
        image: nginx:1.15.4
        ports:
        - containerPort: 80
"""
        dep = yaml.safe_load(txt % (self.id, self.id, self.id))
        resp = self.k8s_apps_v1.create_namespaced_deployment(
            body=dep, namespace="default")
        print("Deployment created. status='%s'" % resp.metadata.name)
        self.deployed = True
        self.wait_pods("RUNNING", "app=nginx%s" % self.id)
        print("RUNNING %s" % self.id)
