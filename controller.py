import numpy as np
import subprocess as subprocess
import shlex
import os
import requests
import time
import pandas as pd

total_len = 24

SERVERS_LIST = [{'name': 'myweb1', 'ip': 'http://172.20.10.2/'},
                {'name': 'myweb2', 'ip': 'http://172.20.10.5/'},
                {'name': 'myweb3', 'ip': 'http://172.20.10.7/'}]

ACL_LIST = {'cpu_restricted_on': lambda cpu, memory: cpu > 40,
            'vm1_vm2_on': lambda cpu, memory: cpu > 40,
            'vm1_vm2_vm3_off': lambda cpu, memory: cpu < 50,
            'pass_cpu': lambda cpu, memory: cpu > 100,
            'vm1_vm2_off': lambda cpu, memory: cpu < 40,
            'memory_restricted_on': lambda cpu, memory: memory > 80,
            'weighted_restricted_on': lambda cpu, memory: cpu * 2 + memory > 100,
            'weighted_restricted_off': lambda cpu, memory: cpu * 2 + memory < 100}

SERVER_ON_ACL = [['cpu_restricted_on'],['vm1_vm2_on']]
SERVER_OFF_ACL = [['vm1_vm2_off'], ['vm1_vm2_vm3_off']]
SERVER_POINTER = 0


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def parse_request(request):
    content = request.content.decode("utf-8").split('\n')
    content = content[:len(content) - 1]
    return np.array([m for m in content]).astype(float)


def get_data():
    memory_array = np.array([])
    cpu_array = np.array([])
    out_of_service = False
    for i in range(SERVER_POINTER + 1):
        try:
            memory_data = requests.get(SERVERS_LIST[i]['ip'] + 'memory.txt', timeout=30)
            print(memory_data)
            cpu_data = requests.get(SERVERS_LIST[i]['ip'] + 'cpu.txt', timeout=30)
            print(cpu_data)
        except requests.exceptions.Timeout:
            out_of_service = True
            continue
        memory_array = np.concatenate((memory_array, parse_request(memory_data)))
        cpu_array = np.concatenate((cpu_array, parse_request(cpu_data)))
    return memory_array, cpu_array, out_of_service


def check_ACL(cpu, memory, acls):
    ans = True
    for acl in acls:
        ans = ans and ACL_LIST[acl](cpu, memory)
    return ans


config_info = "Servers info: \n"
for s in SERVERS_LIST:
    config_info += s['name'] + "   IP: " + s['ip'] + "\n"
config_info += "ACL list: \n"
for r in list(ACL_LIST.keys()):
    config_info += r + "\n"
print(f"{bcolors.OKGREEN} {config_info} {bcolors.ENDC}")
path = 'C:\Program Files\Oracle\VirtualBox'
os.chdir(path)
while True:
    info = ""
    memory_data, cpu_data, out_of_service = get_data()
    print("out of service:")
    print(out_of_service)
    if out_of_service and SERVER_POINTER < len(SERVERS_LIST) - 1:
        info += "Server " + SERVERS_LIST[SERVER_POINTER]['name'] + " is out of service\n"
        start = shlex.split("VBoxManage startvm") + shlex.split(str(SERVERS_LIST[SERVER_POINTER + 1]['name']))  + shlex.split(" -type headless")
        process = subprocess.Popen(start, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout = str(stdout).encode("utf-8")
        print(stdout.decode("unicode_escape"))
        stderr = str(stderr).encode("utf-8")
        print(stderr.decode("unicode_escape"))
        info += "Info: server " + str(SERVER_POINTER + 1) + " turned on\n"
        SERVER_POINTER += 1
        print(f"{bcolors.HEADER} {info} {bcolors.ENDC}")
        continue

    if len(memory_data) < total_len or len(cpu_data) < total_len:
        continue

    info += "Info: There are enough data to analyze \n"
    memory = np.mean(memory_data)
    cpu = np.mean(cpu_data)
    if SERVER_POINTER > 0:
        if check_ACL(cpu, memory, SERVER_OFF_ACL[SERVER_POINTER]):
            stop = shlex.split("VBoxManage controlvm") + shlex.split(str(SERVERS_LIST[SERVER_POINTER]['name'])) + shlex.split("poweroff")
            process = subprocess.Popen(stop, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            stdout = str(stdout).encode("utf-8")
            print(stdout.decode("unicode_escape"))
            stderr = str(stderr).encode("utf-8")
            print(stderr.decode("unicode_escape"))
            info += "Info: server " + str(SERVER_POINTER) + " turned off\n"
            SERVER_POINTER -= 1

    if SERVER_POINTER >= len(SERVERS_LIST):
        continue

    if check_ACL(cpu, memory, SERVER_ON_ACL[SERVER_POINTER]):
        start = shlex.split("VBoxManage startvm") + shlex.split(
            str(SERVERS_LIST[SERVER_POINTER + 1]['name'])) + shlex.split(" -type headless")
        process = subprocess.Popen(start, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout = str(stdout).encode("utf-8")
        print(stdout.decode("unicode_escape"))
        stderr = str(stderr).encode("utf-8")
        print(stderr.decode("unicode_escape"))
        print("hiiiiiii")
        info += "Info: server " + str(SERVER_POINTER + 1) + " turned on\n"
        SERVER_POINTER += 1
    info += "\n"
    print(f"{bcolors.HEADER} {info} {bcolors.ENDC}")

    time.sleep(5)
