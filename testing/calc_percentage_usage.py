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
    provider_active_jobs = 0
    provider_active_jobs_last = 0
    active_periods = []
    total_active = 0

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
        else:
            periods[-1]["end"] = datetime.strptime(f"2025 {firstline_split[0]} {firstline_split[1]} {firstline_split[2]}",
                        "%Y %b %d %H:%M:%S")

        for line in ([firstline] + list(logfile)):
            provider_active_jobs_last = provider_active_jobs
            line_split = line.split()
            if state:
                if "Job completed" in line:
                    num_succesful_jobs = num_succesful_jobs + 1
                    provider_active_jobs = provider_active_jobs - 1
                elif "Start Job" in line:
                    provider_active_jobs = provider_active_jobs + 1
                elif "Stopping wasimoff_provider.service" in line:
                    provider_active_jobs = 0
                    state = False
                    periods[-1]["end"] = datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")
            elif "[Wasimoff Provider] started in Window" in line:
                    state = True
                    periods.append({"start" : datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")})
                    active_periods.append([])
            
            if provider_active_jobs_last == 0 and provider_active_jobs > provider_active_jobs_last:
                active_periods[-1].append({"start" : datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")})
            elif provider_active_jobs == 0 and provider_active_jobs_last > provider_active_jobs:
                active_periods[-1][-1]["end"] = datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")

    if not "end" in periods[-1].keys():
        periods[-1]["end"] = observation_end

    # TODO Add active periods to get usage
    with open(f"{args.log}.csv", 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['period','start','end','duration','duration_perc','active','active_perc']
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()
        for i in range(0,len(periods)):
            period_duration = (periods[i]["end"] - periods[i]["start"]).total_seconds()
            duration_perc = period_duration / observation_duration
            wasimoff_usage = wasimoff_usage + duration_perc
            active_duration = 0 
            for j in len(active_periods[i]):
                active_duration = active_duration + (active_duration[i][j]["end"] - active_duration[i][j]["start"]).total_seconds()
            active_duration_perc = active_duration / observation_duration
            total_active = total_active + active_duration
            csvwriter.writerow({'period' : i+1,
                'start' : periods[i]["start"].strftime('%d/%m/%Y %H:%M:%S'),
                'end' : periods[i]["end"].strftime('%d/%m/%Y %H:%M:%S'),
                'duration' : period_duration,
                'duration_perc' : duration_perc,
                'active' : active_duration,
                'active_perc' : active_duration_perc})
        
        writer = csv.writer(csvfile)
        writer.writerow(["total duration of observation in s", observation_duration])
        writer.writerow(["wasimoff node active in %", wasimoff_usage])
        writer.writerow(["wasimoff node running in %", total_active / observation_duration])
        writer.writerow(["slurm node active in %", 1.0 - wasimoff_usage])
        writer.writerow(["number of succesful wasimoff tasks", num_succesful_jobs])
        writer.writerow(["wasimoff throughput in job/s", num_succesful_jobs/observation_duration])


if __name__ == '__main__':
    main()