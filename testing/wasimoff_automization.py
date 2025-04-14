import os
import subprocess as sb
import time
import random

def main():
    try:
        os.chdir("./prototype/client")
    except OSError:
        raise SystemExit("Start script while being in ~/Slurm-Wasioff-Container-Setup")

    random.seed(42)
    call_list = []
    running_calls = 0
    i = 0
    towns = 0
    dt = 0
    endtime = 0
    dts = [0.5, 1.0, 2.0, 4.0]
    endtimes = [500, 1000, 2000, 5000, 10000]
    while True:
        while running_calls < 50:
            if randint(1,2) == 1:
                # tsp
                towns = randint(10,13)
                call_list.append(sb.Popen(["go", "run", "client.go", "-exec", "tsp.wasm", "rand", "f{towns}"]))
            else:
                # proxels
                dt = randint(0,3)
                endtime = randint(0,4)
                call_list.append(sb.Popen(["go", "run", "client.go", "-exec", "proxels.wasm", "-dt", "f{dt}", "-endtime", "f{endtime}"]))
            running_calls = running_calls + 1
        for call in call_list:
            if call.poll() != None:
                running_calls = running_calls - 1

if __name__ == "__main__":
    main()