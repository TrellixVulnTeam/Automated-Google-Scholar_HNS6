import subprocess
res = subprocess.run(['ps', 'aux'], capture_output=True)

if res.returncode != 0:
    print(res)
    raise #something wrong with ps call

for _line in res.stdout.decode().split("\n"):
    #when running, the ps line looks like:
    #python3 run.py https://journals.sagepub.com/doi/abs/10.1177/0885728809346960
    if ("python3" in _line) and ("run.py" in _line):
        #print(_line)
        print("RUNNING")
        break
else:
    print("IDLE")