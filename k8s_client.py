from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes import client, watch
import yaml
import random
from subprocess import Popen, PIPE
import os


class K8sClient:
    id = 31000

    def __init__(self):
        K8sClient.id += 1
        self.id = K8sClient.id
        self.deployed = False
        # ssh -v -N -L 6443:10.0.0.85:6443 ec2-user@18.195.72.99

    def __read_deploy(self):
        with open("nginx-deployment.yaml", "r") as myfile:
            txt = myfile.read()
        formated = txt % ((self.id,) * 8)
        return formated

    def __exec(self, deploy, command):
        my_env = os.environ.copy()
        my_env["NO_PROXY"] = "*"
        cmd = "cat <<EOF | kubectl --kubeconfig config %s --wait -f -\n" % command + deploy + "\nEOF"
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE, encoding='utf8', env=my_env, shell=True)
        p.stdin.write(deploy)
        p.stdin.write("EOF")
        p.stdin.close()
        output = p.stdout.read()
        err = p.stderr.read()
        print(output)
        print(err)

    def wait(self):
        my_env = os.environ.copy()
        my_env["NO_PROXY"] = "*"
        cmd = "kubectl wait --for=condition=available --timeout=60s deployment/nginx-deployment%s -n default" % self.id
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, encoding='utf8', env=my_env, shell=True)
        if p.returncode != 0:
            output = p.stdout.read()
            err = p.stderr.read()
            print(output)
            print(err)
            raise Exception(err, output)

    def deploy(self):
        deploy = self.__read_deploy()
        self.__exec(deploy, "apply")
        self.deployed = True
        self.wait()

    def delete(self):
        deploy = self.__read_deploy()
        self.__exec(deploy, "delete")
        self.deployed = False
