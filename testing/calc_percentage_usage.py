import matplotlib.patches
import os, sys, argparse, csv, matplotlib, pandas, numpy, functools, locale
import matplotlib.pyplot as pyplot
from datetime import datetime, timedelta
import pdb

SLURM_JOBS = 50

# TODO Add epilog and prolog overhead
def analyze_cluster(report_name : str, observation_start : datetime, observation_end : datetime, succesful_tasks_total : int,  node_wasimoff_usage : list,  node_total_active : list):
    total_wasimoff_usage = 0.0
    total_cluster_active = 0.0
    total_idle = 0.0
    num_nodes = len(node_wasimoff_usage)
    observation_duration = (observation_end - observation_start).total_seconds()
    for i in range(0,len(node_wasimoff_usage)):
        total_wasimoff_usage += node_wasimoff_usage[i]
        total_cluster_active += (node_total_active[i] / observation_duration)

    total_idle = (total_wasimoff_usage - total_cluster_active) / num_nodes
    total_wasimoff_usage /= num_nodes
    total_cluster_active /= num_nodes


    with open(f"{report_name}_cluster.txt", 'w', newline='', encoding='utf-8') as report:
        report_str = f"""Report for cluster
Start of observation:                           {observation_start.strftime('%d/%m/%Y %H:%M:%S')}
End of observation:                             {observation_end.strftime('%d/%m/%Y %H:%M:%S')}
Total duration of observation [s]:              {observation_duration}
Succesful wasimoff tasks over whole cluster:    {succesful_tasks_total}
Slurm job throuput [job/s]:                     {(SLURM_JOBS/observation_duration):7f}
Wasimoff task throuput [task/s]:                {(succesful_tasks_total/observation_duration):7f}
Slurm utilization [%]:                          {(1.0 - total_wasimoff_usage):7f}
Wasimoff utilzation [%]:                        {total_cluster_active:7f}
Cluster idle [%]:                               {total_idle:7f}
"""
        report.write(report_str)

def color_of_state(state : str) -> str:
    match state:
        case 'slurm':
            return 'g'
        case 'wasimoff':
            return 'y'
        case 'idle':
            return 'r'

# TODO Add slurm job data and epilog/prolog overhead to chart
def print_activity_chart(report_name : str, observation_start : datetime, observation_end : datetime, node_periods : list, node_active_periods : list):
    fig, ax = pyplot.subplots()

    # data_frame = pandas.DataFrame({ 'node' : ['node_0', 'node_1', 'node_2'], 'start_1' : [observation_start, observation_start, observation_start]})
    data_frame_dict = {}
    nodes_num = len(node_periods)

    # data_frame_dict['start_1'] = [observation_start] * nodes_num
    data_frame_dict['node'] = functools.reduce(lambda x, y: x + [f'Node {y}'], range(0,nodes_num), [])

    complete_table = functools.reduce(lambda x, y: x + [[]], range(0,nodes_num), [])

    for i in range(0,nodes_num):
        if observation_start < node_periods[i][0]["start"]:
            complete_table[i].append({'start' : observation_start, 'end' : node_periods[i][0]["start"], 'state' : 'slurm'})
        for node_period_i in range(0, len(node_periods[i])):
            if node_active_periods[i][node_period_i]:
                if node_periods[i][node_period_i]["start"] < node_active_periods[i][node_period_i][0]["start"]:
                    complete_table[i].append({'start' : node_periods[i][node_period_i]["start"],
                                               'end' : node_active_periods[i][node_period_i][0]["start"],
                                                 'state' : 'idle'})

                for node_active_period_i in range (0, len(node_active_periods[i][node_period_i])):
                    complete_table[i].append({'start' : node_active_periods[i][node_period_i][node_active_period_i]['start'],
                                               'end' : node_active_periods[i][node_period_i][node_active_period_i]['end'],
                                                 'state' : 'wasimoff'})
                    if node_active_period_i < len(node_active_periods[i][node_period_i]) - 1:
                        complete_table[i].append({'start' : node_active_periods[i][node_period_i][node_active_period_i]['end'],
                                               'end' : node_active_periods[i][node_period_i][node_active_period_i + 1]['start'],
                                                 'state' : 'idle'})

                if node_active_periods[i][node_period_i][-1]["end"] < node_periods[i][node_period_i]["end"]:
                    complete_table[i].append({'start' : node_active_periods[i][node_period_i][-1]["end"],
                                               'end' : node_periods[i][node_period_i]["end"],
                                                 'state' : 'idle'})
            else:
                complete_table[i].append({'start' : node_periods[i][node_period_i]["start"],
                                               'end' : node_periods[i][node_period_i]["end"],
                                                 'state' : 'idle'})

            if node_period_i < len(node_periods[i]) - 1:
                complete_table[i].append({'start' : node_periods[i][node_period_i]["end"],
                                           'end' : node_periods[i][node_period_i + 1]["start"],
                                             'state' : 'slurm'})
        
        if node_periods[i][-1]["end"] < observation_end:
            complete_table[i].append({'start' : node_periods[i][-1]["end"], 'end' : observation_end, 'state' : 'slurm'})

    max_intervalls = max(map(len,complete_table))
    for i in range(0,max_intervalls):
        data_frame_dict[f'start_{i}']   = functools.reduce(lambda x, y: x + ([complete_table[y][i]['start']] if i < len(complete_table[y]) else [None]), range(0,nodes_num), [])
        data_frame_dict[f'end_{i}']     = functools.reduce(lambda x, y: x + ([complete_table[y][i]['end']] if i < len(complete_table[y]) else [None]), range(0,nodes_num), [])
        data_frame_dict[f'state_{i}']   = functools.reduce(lambda x, y: x + ([complete_table[y][i]['state']] if i < len(complete_table[y]) else [None]), range(0,nodes_num), [])

    data_frame = pandas.DataFrame(data_frame_dict)
    for i in range(0,max_intervalls):
        data_frame[f'seconds_to_start_{i}'] = (data_frame[f'start_{i}'] - observation_start).dt.total_seconds()
        data_frame[f'seconds_to_end_{i}']   = (data_frame[f'end_{i}'] - observation_end).dt.total_seconds()
        data_frame[f'task_duration_{i}']   = (data_frame[f'end_{i}'] - data_frame[f'start_{i}']).dt.total_seconds()
    
    for index, row in data_frame.iterrows():
        yrange = (index + 1, 0.5)
        xrange = functools.reduce(lambda x, y: x + ([(row[f'seconds_to_start_{y}'], row[f'task_duration_{y}'])] if not pandas.isnull(row[f'start_{y}']) else []), range(0,max_intervalls), [])
        colors = functools.reduce(lambda x, y: x + ([color_of_state(row[f'state_{y}'])] if not pandas.isnull(row[f'state_{y}']) else []), range(0,max_intervalls), [])
        ax.broken_barh(xranges=xrange, yrange=yrange, color=colors)

    ax.set_yticks(list(map(lambda x: x + 1.25, range(0,nodes_num))))
    ax.set_yticklabels(data_frame['node'], fontsize=14)

    patches = []
    for state in ['slurm', 'wasimoff', 'idle']:
        patches.append(matplotlib.patches.Patch(color=color_of_state(state)))

    ax.legend(handles=patches, labels=['slurm', 'wasimoff', 'idle'], fontsize=12, bbox_to_anchor=(1.0, 0.81))

    pyplot.xticks(fontsize=14)
    pyplot.xlabel('Zeit in s', loc='right', fontsize=16)

    pyplot.gca().invert_yaxis()
    # pyplot.show()
    # fig.set_figheight(6)
    fig.set_figwidth(10)
    pyplot.savefig(report_name + '_plot.png', dpi=500)
    # pyplot.savefig(report_name + '_plot.png')

# TODO Add handling of slurm output files
def analyze_node(observation_start : datetime, observation_end : datetime, observation_duration : timedelta, log : str) -> tuple:
    # initialize objects
    periods = []
    state = False
    wasimoff_active = False
    succesful_jobs = 0
    wasimoff_usage = 0.0
    total_duration = 0
    active_periods = [[]]
    total_active = 0

    periods.append({"start" : observation_start})

    with open(log, 'r', encoding='utf-8') as logfile:
        firstline = logfile.readline()
        firstline_split = firstline.split()
        
        # check if provider is currently active
        if "deno" in firstline_split[4] or ("systemd" in firstline_split[4] and "Start" in firstline_split[5]):
            state = True
        else:
            periods[-1]["end"] = datetime.strptime(f"2025 {firstline_split[0]} {firstline_split[1]} {firstline_split[2]}",
                        "%Y %b %d %H:%M:%S")

        for line in ([firstline] + list(logfile)):
            line_split = line.split()
            if state:
                if "Job completed" in line:
                    succesful_jobs += 1
                elif "Start running tasks" in line and wasimoff_active == False:
                    wasimoff_active = True
                    active_periods[-1].append({"start" : datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")})
                elif "Returning to idle" in line:
                    wasimoff_active = False
                    active_periods[-1][-1]["end"] = datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")
                elif "Stopping wasimoff_provider.service" in line:
                    state = False
                    if wasimoff_active:
                        wasimoff_active = False
                        active_periods[-1][-1]["end"] = datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")
                    periods[-1]["end"] = datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")
            elif "[Wasimoff Provider] started in Window" in line:
                    state = True
                    periods.append({"start" : datetime.strptime(f"2025 {line_split[0]} {line_split[1]} {line_split[2]}",
                        "%Y %b %d %H:%M:%S")})
                    active_periods.append([])    

    if wasimoff_active:
        active_periods[-1][-1]["end"] = observation_end
    if not "end" in periods[-1].keys():
        periods[-1]["end"] = observation_end

    with open(f"{log}.csv", 'w', newline='', encoding='utf-8') as csvfile:
        max_num_active_periods = max(map(len, active_periods))
        fieldnames = ['period','start','end','duration','duration_perc','active','active_perc']
        for j in range(0,max_num_active_periods):
            fieldnames.append(f"active_start_{j}")
            fieldnames.append(f"active_end_{j}")
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()
        for i in range(0,len(periods)):
            row = {'period' : i+1,
                'start' : periods[i]["start"].strftime('%d/%m/%Y %H:%M:%S'),
                'end' : periods[i]["end"].strftime('%d/%m/%Y %H:%M:%S')}
            period_duration = (periods[i]["end"] - periods[i]["start"]).total_seconds()
            total_duration += period_duration
            duration_perc = period_duration / observation_duration
            # wasimoff_usage += duration_perc
            active_duration = 0 
            for j in range(0,len(active_periods[i])):
                row[f"active_start_{j}"] = active_periods[i][j]["start"].strftime('%d/%m/%Y %H:%M:%S')
                row[f"active_end_{j}"] = active_periods[i][j]["end"].strftime('%d/%m/%Y %H:%M:%S')
                active_duration += (active_periods[i][j]["end"] - active_periods[i][j]["start"]).total_seconds()
            active_duration_perc = active_duration / observation_duration
            total_active += active_duration
            row.update({'duration' : period_duration,
                'duration_perc' : duration_perc,
                'active' : active_duration,
                'active_perc' : active_duration_perc})
            csvwriter.writerow(row)
        
        wasimoff_usage = total_duration / observation_duration
        writer = csv.writer(csvfile)
        writer.writerow(["total duration of observation in s", observation_duration])
        writer.writerow(["wasimoff node active in %", f"{wasimoff_usage:7f}"])
        writer.writerow(["wasimoff node running in %", f"{(total_active / observation_duration):7f}"])
        writer.writerow(["slurm node active in %", f"{(1.0 - wasimoff_usage):7f}"])
        writer.writerow(["number of succesful wasimoff tasks", succesful_jobs])
        writer.writerow(["wasimoff throughput in job/s", f"{(succesful_jobs/observation_duration):7f}"])

    return succesful_jobs, periods, active_periods, wasimoff_usage, total_active

# Add handling for slurm output
def main():
    locale.setlocale(locale.LC_ALL,'')
    parser = argparse.ArgumentParser(
        prog="",
        description="Analyse usage of compute node and cluster",
        epilog="Break down usage of individual compute nodes to percentage of non-utilization, usage via wasimoff and usage via slurm"
    )
    parser.add_argument("-t", required=True, help="set file which contains timestamps of observation", metavar="timestamp file", dest="timestamp_file")
    parser.add_argument("-l", required=True, help="set logfiles of observed compute nodes", metavar="com node log files", dest="logs", nargs='+')
    # parser.add_argument("-s", required=True, help="set slurm output files of observed compute nodes", metavar="com node slurm output files", dest="slurm_file", nargs='+')
    args = parser.parse_args()

    # initialize timestamp objects
    observation_start = 0
    observation_end = 0
    observation_duration = 0
    
    # succesful_jobs, periods, active_periods, wasimoff_usage, total_active
    # initialize objects for cluster
    succesful_tasks_total = 0
    node_periods = []
    node_active_periods = []
    node_wasimoff_usage = []
    node_total_active = []

    # Create datetime objects from timestamps
    with open(args.timestamp_file, 'r', encoding='utf-8') as timestamps:
        tmp = timestamps.readline().strip()
        observation_start = datetime.strptime(tmp, "%Y-%m-%d %H:%M:%S")
        tmp = timestamps.readline().strip()
        observation_end = datetime.strptime(tmp, "%Y-%m-%d %H:%M:%S")
        observation_duration = (observation_end - observation_start).total_seconds()

    for log in args.logs:
        succesful_tasks, periods, active_periods, wasimoff_usage, total_active = analyze_node(observation_start, observation_end, observation_duration, log)
        succesful_tasks_total += succesful_tasks
        node_periods.append(periods)
        node_active_periods.append(active_periods)
        node_wasimoff_usage.append(wasimoff_usage)
        node_total_active.append(total_active)

    analyze_cluster(args.timestamp_file.split('.')[0], observation_start, observation_end, succesful_tasks_total, node_wasimoff_usage, node_total_active)
    print_activity_chart(args.timestamp_file.split('.')[0], observation_start, observation_end, node_periods, node_active_periods)


if __name__ == '__main__':
    main()