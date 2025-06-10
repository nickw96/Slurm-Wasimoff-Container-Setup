import matplotlib.patches
import os, sys, argparse, csv, matplotlib, pandas, numpy, functools, locale
import matplotlib.pyplot as pyplot
from datetime import datetime, timedelta
import pdb

TIMESTAMP_READ_FORMAT='%Y-%m-%d %H:%M:%S'

def analyse_cluster(report_name : str, observation_start : datetime, observation_end : datetime, succesful_tasks_total : int,
                    node_wasimoff_usage : list, node_slurm_usage : list, node_prolog_usage : list, node_epilog_usage : list, node_idle_usage : list, num_slurm_jobs : int):
    total_wasimoff_usage = 0.0
    total_slurm_usage = 0.0
    total_prolog = 0.0
    total_epilog = 0.0
    total_idle = 0.0
    num_nodes = len(node_wasimoff_usage)
    observation_duration = (observation_end - observation_start).total_seconds()
    for i in range(0,len(node_wasimoff_usage)):
        total_wasimoff_usage += node_wasimoff_usage[i]
        total_slurm_usage += node_slurm_usage[i]
        total_prolog += node_prolog_usage[i]
        total_epilog += node_epilog_usage[i]
        total_idle += node_idle_usage[i]

    total_prolog /= num_nodes
    total_epilog /= num_nodes
    total_idle /= num_nodes
    total_wasimoff_usage /= num_nodes
    total_slurm_usage /= num_nodes

    with open(f"{report_name}_cluster.txt", 'w', newline='', encoding='utf-8') as report:
        report_str = f"""Report for cluster
Start of observation:                           {observation_start.isoformat(timespec='microseconds')}
End of observation:                             {observation_end.isoformat(timespec='microseconds')}
Total duration of observation [s]:              {observation_duration}
Succesful wasimoff tasks over whole cluster:    {succesful_tasks_total}
Slurm job throuput [job/s]:                     {(num_slurm_jobs/observation_duration):7f}
Wasimoff task throuput [task/s]:                {(succesful_tasks_total/observation_duration):7f}
Slurm utilization in %:                         {total_slurm_usage*100:5f}
Wasimoff utilzation in %:                       {total_wasimoff_usage*100:5f}
Cluster in prolog in %:                         {total_prolog*100:5f}
Cluster in epilog in %:                         {total_epilog*100:5f}
Cluster idle in %:                              {total_idle*100:5f}
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
        case 'prolog':
            return 'c'
        case 'epilog':
            return 'b'

def print_activity_chart(report_name : str, observation_start : datetime, observation_end : datetime, node_time_lines : list):
    fig, ax = pyplot.subplots()
    data_frame_dict = {}
    nodes_num = len(node_time_lines)

    data_frame_dict['node'] = functools.reduce(lambda x, y: x + [f'Node {y}'], range(0,nodes_num), [])

    max_intervalls = max(map(len,node_time_lines))
    for i in range(0,max_intervalls):
        data_frame_dict[f'start_{i}']   = functools.reduce(lambda x, y: x + ([node_time_lines[y][i]['start']] if i < len(node_time_lines[y]) else [None]), range(0,nodes_num), [])
        data_frame_dict[f'end_{i}']     = functools.reduce(lambda x, y: x + ([node_time_lines[y][i]['end']] if i < len(node_time_lines[y]) else [None]), range(0,nodes_num), [])
        data_frame_dict[f'state_{i}']   = functools.reduce(lambda x, y: x + ([node_time_lines[y][i]['state']] if i < len(node_time_lines[y]) else [None]), range(0,nodes_num), [])

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
    for state in ['slurm', 'wasimoff', 'idle', 'prolog', 'epilog']:
        patches.append(matplotlib.patches.Patch(color=color_of_state(state)))

    ax.legend(handles=patches, labels=['slurm', 'wasimoff', 'idle', 'prolog', 'epilog'], fontsize=12, bbox_to_anchor=(1.13, 0.81))

    pyplot.xticks(fontsize=14)
    pyplot.xlabel('Zeit in s', loc='right', fontsize=16)

    pyplot.gca().invert_yaxis()
    # pyplot.show()
    # fig.set_figheight(6)
    fig.set_figwidth(11)
    pyplot.savefig(report_name + '_plot.png', dpi=500)
    # pyplot.savefig(report_name + '_plot.png')

def read_slurm_data(dir : str, num_com_nodes : int) -> dict:
    nodes_slurm_jobs = {}
    node_names = []
    for i in range(0, num_com_nodes):
        nodes_slurm_jobs[f'com{i}'] = []
        node_names.append(f'com{i}')

    with os.scandir(dir) as entries:
        for entry in entries:
            mapping = {}
            with open(entry.path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                lines = filter(lambda x: not x.startswith('srun: '), lines)
                num_nodes_in_job = 0 
                for i in range(0,len(lines)):
                    split_line = lines[i].split()
                    if len(split_line) > 1 and split_line[1] in node_names and not split_line[1] in mapping.values():
                        num_nodes_in_job += 1
                        mapping[split_line[0]] = split_line[1]
                assert num_com_nodes >= num_nodes_in_job
                for i in range(0,num_nodes_in_job):
                    split_line = lines[i].split()
                    nodes_slurm_jobs[mapping[split_line[0]]].append({'start' : datetime.fromisoformat(split_line[1][:26] + split_line[1][29:]), 'state' : 'slurm'})
                for i in range(-num_nodes_in_job,0):
                    split_line = lines[i].split()
                    nodes_slurm_jobs[mapping[split_line[0]]][-1]['end'] = datetime.fromisoformat(split_line[1][:26] + split_line[1][29:])

    return nodes_slurm_jobs

def analyse_node(observation_start : datetime, observation_end : datetime, observation_duration : timedelta, log : str, slurm_data : list) -> tuple:
    # initialize objects
    periods = []
    state = False
    wasimoff_active = False
    succesful_tasks = 0
    wasimoff_usage = 0.0
    slurm_usage = 0.0
    prolog_usage = 0.0
    epilog_usage = 0.0
    idle_usage = 0.0
    wasimoff_total_duration = 0
    slurm_total_duration = 0
    prolog_total_duration = 0
    epilog_total_duration = 0
    idle_total_duration = 0
    active_periods = [[]]
    wasimoff_index = 0
    time_line = []
    prologs = []
    epilogs = []

    with open(log, 'r', encoding='utf-8') as logfile:
        firstline = logfile.readline()
        firstline_split = firstline.split()
        
        # check if provider is currently active
        if "deno" in firstline_split[2]:
            state = True

        for line in ([firstline] + list(logfile)):
            line_split = line.split()
            if state:
                if "Job completed" in line:
                    succesful_tasks += 1
                elif "Start running tasks" in line and wasimoff_active == False:
                    wasimoff_active = True
                    active_periods[-1].append({"start" : datetime.fromisoformat(line_split[0]), 'state' : 'wasimoff'})
                elif "Returning to idle" in line:
                    wasimoff_active = False
                    active_periods[-1][-1]["end"] = datetime.fromisoformat(line_split[0])
                elif "Stopping wasimoff_provider.service" in line:
                    state = False
                    if wasimoff_active:
                        wasimoff_active = False
                        active_periods[-1][-1]["end"] = datetime.fromisoformat(line_split[0])
                    if len(periods) > 0:
                        periods[-1]["end"] = datetime.fromisoformat(line_split[0])
                    else:
                        periods.append({"start" : observation_start,
                                        "end" : datetime.fromisoformat(line_split[0]),
                                        'state' : 'wasimoff_period'})
                    epilogs.append({"start" : datetime.fromisoformat(line_split[0]), 'state' : 'epilog'})
            elif "Stopping wasimoff_provider.service" in line:
                epilogs.append({"start" : datetime.fromisoformat(line_split[0]), 'state' : 'epilog'})
            elif "Stopped wasimoff_provider.service" in line:
                if len(epilogs) > 0:
                    epilogs[-1]['end'] = datetime.fromisoformat(line_split[0])
                else:
                    epilogs.append({"start" : observation_start,
                        'end' : datetime.fromisoformat(line_split[0]),
                        'state' : 'epilog'})
            elif "Starting wasimoff_provider.service" in line:
                prologs.append({"start" : datetime.fromisoformat(line_split[0]), 'state' : 'prolog'})
            elif "Started wasimoff_provider.service" in line:
                if len(epilogs) > 0:
                    prologs[-1]['end'] = datetime.fromisoformat(line_split[0])
                else:
                    prologs.append({"start" : observation_start,
                        'end' : datetime.fromisoformat(line_split[0]),
                        'state' : 'prolog'})
            elif "[Wasimoff] starting Provider in Deno" in line:
                    state = True
                    periods.append({"start" : datetime.fromisoformat(line_split[0]), 'state' : 'wasimoff_period'})
                    active_periods.append([])    

    if wasimoff_active:
        active_periods[-1][-1]["end"] = observation_end
    if not "end" in periods[-1].keys():
        periods[-1]["end"] = observation_end
    elif not "end" in prologs[-1].keys():
        prologs[-1]["end"] = observation_end
    elif not "end" in epilogs[-1].keys():
        epilogs[-1]["end"] = observation_end

    tmp = sorted(slurm_data + prologs + periods + epilogs, key=lambda dic: (dic['start'], dic['end']))
    for slice in tmp:
        if len(time_line) > 1 and (slice['start'] - time_line[-1]['end']).total_seconds() > 0:
                time_line.append({'start' : time_line[-1]['end'],
                                  'end' : slice['start'],
                                  'state' : 'idle'})
                time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()
        if slice['state'] == 'wasimoff_period':
            if len(active_periods[wasimoff_index]) > 0:
                if (active_periods[wasimoff_index][0]['start'] - slice['start']).total_seconds() > 0:
                    time_line.append({'start' : slice['start'],
                                      'end' : active_periods[wasimoff_index][0]['start'],
                                      'state' : 'idle'})
                    time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()
                for active_period in active_periods[wasimoff_index]:
                    if len(time_line) > 1 and (active_period['start'] - time_line[-1]['end']).total_seconds() > 0:
                        time_line.append({'start' : time_line[-1]['end'],
                                      'end' : active_period['start'],
                                      'state' : 'idle'})
                        time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()
                    time_line.append(active_period)
                    time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()
                if (slice['end'] - active_periods[wasimoff_index][-1]['end']).total_seconds() > 0:
                    time_line.append({'start' : active_periods[wasimoff_index][-1]['end'],
                                      'end' : slice['end'],
                                      'state' : 'idle'})
                    time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()
            # no check necessary, since len(periods)==len(active_periods)
            wasimoff_index += 1
        else:
            if (slice['end'] - slice['start']).total_seconds() != 0.0:
                time_line.append(slice)
                time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()

    if time_line[-1]['end'] < observation_end:
        time_line.append({'start' : time_line[-1]['end'],
                                      'end' : observation_end,
                                      'state' : 'idle'})
        time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()

    # TODO remove periods of 0 and posiblly merge periods of same state

    with open(f"{log}.csv", 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['intervall','state','start','end','duration','duration_perc']
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()
        time_line_index = 0
        for time_slot in time_line:
            csvwriter.writerow({
                'intervall' : time_line_index,
                'state' : time_slot['state'],
                'start' : time_slot['start'].isoformat(timespec='microseconds'),
                'end' : time_slot['end'].isoformat(timespec='microseconds'),
                'duration' : time_slot['duration'],
                'duration_perc' : time_slot['duration'] / observation_duration
            })
            match time_slot['state']:
                case 'wasimoff' :
                    wasimoff_total_duration += time_slot['duration']
                case 'slurm' :
                    slurm_total_duration += time_slot['duration']
                case 'epilog' :
                    epilog_total_duration += time_slot['duration']
                case 'prolog' :
                    prolog_total_duration += time_slot['duration']
                case 'idle' :
                    idle_total_duration += time_slot['duration']
            time_line_index += 1

        # assert (wasimoff_total_duration + slurm_total_duration + prolog_total_duration + epilog_total_duration + idle_total_duration) <= observation_duration
        wasimoff_usage = wasimoff_total_duration / observation_duration
        slurm_usage = slurm_total_duration / observation_duration
        prolog_usage = prolog_total_duration / observation_duration
        epilog_usage = epilog_total_duration / observation_duration
        idle_usage = idle_total_duration / observation_duration

        writer = csv.writer(csvfile)
        writer.writerow(["total duration of observation run in s", observation_duration])
        writer.writerow(["wasimoff node usage in %", f"{wasimoff_usage * 100:5f}"])
        writer.writerow(["slurm node usage in %", f"{slurm_usage * 100:5f}"])
        writer.writerow(["time in prolog on node relative to observation %", f"{prolog_usage * 100:5f}"])
        writer.writerow(["time in epilog on node relative to observation %", f"{epilog_usage * 100:5f}"])
        writer.writerow(["time in idle on node relative to observation %", f"{idle_usage * 100:5f}"])
        writer.writerow(["number of succesful wasimoff tasks", succesful_tasks])
        writer.writerow(["wasimoff throughput on node in job/s", f"{(succesful_tasks/observation_duration):7f}"])
        writer.writerow(["slurm throughput on node in job/s", f"{(len(slurm_data)/observation_duration):7f}"])

    return succesful_tasks, time_line, wasimoff_usage, slurm_usage, prolog_usage, epilog_usage, idle_usage

def main():
    num_slurm_jobs = 0
    num_nodes = 0
    locale.setlocale(locale.LC_ALL,'')
    parser = argparse.ArgumentParser(
        prog="",
        description="Analyse usage of compute node and cluster",
        epilog="Break down usage of individual compute nodes to percentage of non-utilization, usage via wasimoff and usage via slurm"
    )
    parser.add_argument("-t", required=True, help="set file which contains timestamps of observation", metavar="timestamp file", dest="timestamp_file")
    parser.add_argument("-l", required=True, help="set directory of logfiles of observed compute nodes", metavar="com node wasimoff log directory", dest="wasimoff_logs")
    parser.add_argument("-s", required=True, help="set directory with slurm output files of observed compute nodes", metavar="com node slurm log directory", dest="slurm_logs")
    args = parser.parse_args()

    try:
        tmp = os.scandir(args.wasimoff_logs)
        num_nodes = len(list(tmp))
        tmp.close()
    except NotADirectoryError:
        raise SystemExit('-l argument is required to be a directory')

    try:
        tmp = os.scandir(args.slurm_logs)
        num_slurm_jobs = len(list(tmp))
        tmp.close()
    except NotADirectoryError:
        raise SystemExit('-s argument is required to be a directory')

    # initialize timestamp objects
    observation_start = 0
    observation_end = 0
    observation_duration = 0
    
    # succesful_tasks, periods, active_periods, wasimoff_usage, wasimoff_total_active
    # initialize objects for cluster
    succesful_tasks_total = 0
    node_time_lines = []
    node_wasimoff_usage = []
    node_slurm_usage = []
    node_prolog_usage = []
    node_epilog_usage = []
    node_idle_usage = []
    
    # Create datetime objects from timestamps
    with open(args.timestamp_file, 'r', encoding='utf-8') as timestamps:
        tmp = timestamps.readline().strip()
        observation_start = datetime.strptime(tmp, TIMESTAMP_READ_FORMAT)
        tmp = timestamps.readline().strip()
        observation_end = datetime.strptime(tmp, TIMESTAMP_READ_FORMAT)
        observation_duration = (observation_end - observation_start).total_seconds()

    # read slurm job data
    slurm_data = read_slurm_data(args.slurm_logs, num_nodes)

    # read and analyse 
    with os.scandir(args.wasimoff_logs) as entries:
        for entry in entries:
            if entry.name.endswith('.log'):
                node_name = entry.name.split('_')[-1].split('.')[0]
                succesful_tasks, time_line, wasimoff_usage, slurm_usage, prolog_usage, epilog_usage, idle_usage = analyse_node(observation_start, observation_end, observation_duration, entry.path, slurm_data[node_name])
                succesful_tasks_total += succesful_tasks
                node_time_lines.append(time_line)
                node_wasimoff_usage.append(wasimoff_usage)
                node_slurm_usage.append(slurm_usage)
                node_prolog_usage.append(prolog_usage)
                node_epilog_usage.append(epilog_usage)
                node_idle_usage.append(idle_usage)

    analyse_cluster(args.timestamp_file.split('.')[0], observation_start, observation_end, succesful_tasks_total, node_wasimoff_usage, node_slurm_usage, node_prolog_usage, node_epilog_usage, node_idle_usage, num_slurm_jobs)
    print_activity_chart(args.timestamp_file.split('.')[0], observation_start, observation_end, node_time_lines)


if __name__ == '__main__':
    main()