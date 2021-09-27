import requests

from k8s_client import K8sClient



client = K8sClient()
client.deploy()
client.delete()
#client.service()
# client.delete()

