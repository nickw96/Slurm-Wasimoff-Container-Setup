import os, sys, argparse, csv
from datetime import datetime
import pdb

def main():
    # try:
    #     arg = sys.argv[1]
    # expect IndexError:
    #     raise SystemExit(f"Usage: {sys.argv[0]} <com node log file>")

    # if not len(sys.argv) > 2:
    #     raise SystemExit(f"Usage: {sys.argv[0]} <timestamp file> <com node log file>")

    parser = argparse.ArgumentParser(
        prog="",
        description=""
    )
    parser.add_argument("-t", required=True, help="set file which contains timestamps of observation", metavar="timestamp file", dest="timestamp_file")
    parser.add_argument("-l", required=True, help="set logfile of observed compute node", metavar="com node log file", dest="log")

    args = parser.parse_args()

    # initialize objects
    observation_start = 0
    observation_end = 0
    observation_duration = 0
    periods = []
    state = False
    num_succesful_jobs = 0
    wasimoff_usage = 0.0

    # Create datetime objects from timestamps
    with open(args.timestamp_file, 'r', encoding='utf-8') as timestamps:
        tmp = timestamps.readline().strip()
        observation_start = datetime.strptime(tmp, "%Y-%m-%d %H:%M:%S")
        tmp = timestamps.readline().strip()
        observation_end = datetime.strptime(tmp, "%Y-%m-%d %H:%M:%S")
        observation_duration = (observation_end - observation_start).total_seconds()

        periods.append({"start" : observation_start})

    with open(args.log, 'r', encoding='utf-8') as logfile:
        firstline = logfile.readline()
        firstline_split = firstline.split()
        
        # check if provider is currently active
        if "deno" in firstline_split[4] or ("systemd" in firstline_split[4] and "Start" in firstline_split[5]):
            state = True

        for line in ([firstline] + list(logfile)):
            line_split = line.split()
            if state:
                if "[RPCHandler] connect/" in line:
                    num_succesful_jobs = num_succesful_jobs + 1
                elif "Stopping wasimoff_provider.service" in line:
                    state = False
                    periods[-1]["end"] = datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")
            elif "[Wasimoff Provider] started in Window" in line:
                    state = True
                    periods.append({"start" : datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")})

    if not "end" in periods[-1].keys():
        periods[-1]["end"] = observation_end

    with open(f"{args.log}.csv", 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['period','start','end','duration','proc_duration']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(0,len(periods)):
            period_duration = (periods[i]["end"] - periods[i]["start"]).total_seconds()
            proc_duration = period_duration / observation_duration
            wasimoff_usage = wasimoff_usage + proc_duration
            writer.writerow({'period' : i+1,
                'start' : periods[i]["start"].strftime('%d/%m/%Y %H:%M:%S'),
                'end' : periods[i]["end"].strftime('%d/%m/%Y %H:%M:%S'),
                'duration' : period_duration,
                'proc_duration' : proc_duration})
        
        # TODO: maybe use another file writer instead
        writer.writerow({'period' : "total duration of observation",
                'start' : observation_duration})
        writer.writerow({'period' : "wasimoff node usage",
                'start' : wasimoff_usage})
        writer.writerow({'period' : "slurm node usage",
                'start' : 1.0 - wasimoff_usage})


if __name__ == '__main__':
    main()