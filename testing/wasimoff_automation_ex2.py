import os
import subprocess as sb
import time
import random

def main():
    try:
        os.chdir("./Slurm-Wasimoff-Container-Setup/prototype/client")
    except OSError:
        raise SystemExit("Start script while being in ~")

    random.seed(42)
    call_list = []
    new_list = []
    running_calls = 0
    towns = 0
    while True:
        while running_calls < 50:
            # tsp
            # set towns from 10 to 12
            towns = 10
            call_list.append(sb.Popen(["./client", "-exec", "tsp.wasm", "rand", f"{towns}"]))
            running_calls = running_calls + 1
        for call in call_list:
            if call.poll() != None:
                running_calls = running_calls - 1
            else:
                new_list.append(call)
        call_list = [call for call in call_list if call in new_list]
        new_list = []
        time.sleep(random.randint(1,10))

if __name__ == "__main__":
    main()