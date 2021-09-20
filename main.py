# https://www.opennet.ru/base/net/iptables_treasures.txt.html
from kubernetes import client
from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api

#client_config = Configuration()

config.load_kube_config(r"C:\Users\pstukalo\aws\roles\k8s_user\keys\config")

try:
    c = Configuration().get_default_copy()
    c.cert_file=r"C:\Users\pstukalo\aws\roles\k8s_user\keys\testadmin.crt"
    c.key_file=r"C:\Users\pstukalo\aws\roles\k8s_user\keys\testadmin.key"
    c.assert_hostname = False
except AttributeError:
    c = Configuration()
    c.assert_hostname = False
Configuration.set_default(c)
core_v1 = core_v1_api.CoreV1Api()
ret = core_v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" %
          (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
