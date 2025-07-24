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
  i = 0
  towns = 0
  dt = 0
  endtime = 0
  dts = [0.5, 1.0, 2.0, 4.0]
  endtimes = [500, 1000, 2000, 5000]
  while True:
    while running_calls < 50:
      if random.randint(1,2) == 1:
        # tsp
        towns = random.randint(9,12)
        call_list.append(sb.Popen(["./client", "-exec", "tsp.wasm", "rand", f"{towns}"]))
      else:
        # proxels
        dt = random.randint(0,3)
        endtime = random.randint(0,3)
        call_list.append(sb.Popen(["./client", "-exec", "proxels.wasm", "-dt", f"{dts[dt]}", "-endtime", f"{endtimes[endtime]}"]))
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