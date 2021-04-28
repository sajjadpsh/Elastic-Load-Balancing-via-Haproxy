import psutil
import numpy as np
import subprocess
import json
js = subprocess.run(['mpstat', '-o', 'JSON'], stdout=subprocess.PIPE)



max_len = 24

try:
    pr_memory = np.loadtxt('/var/www/html/memory.txt', dtype=float)
except:
    pr_memory = np.array([])
try:
    pr_cpu = np.loadtxt('/var/www/html/cpu.txt', dtype=float)
except:
    pr_cpu = np.array([])

pr_memory = np.insert(pr_memory, 0, psutil.virtual_memory().percent)
pr_cpu = np.insert(pr_cpu, 0, 100 - json.loads(js.stdout)['sysstat']['hosts'][0]['statistics'][0]['cpu-load'][0]['idle'])

pr_memory = pr_memory[:max_len if len(pr_memory) > max_len else len(pr_memory)]
pr_cpu = pr_cpu[:max_len if len(pr_cpu) > max_len else len(pr_cpu)]


np.savetxt('/var/www/html/memory.txt', pr_memory)
np.savetxt('/var/www/html/cpu.txt', pr_cpu)
