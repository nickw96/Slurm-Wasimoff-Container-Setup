import matplotlib.patches
import os, sys, argparse, csv, matplotlib, pandas, numpy, functools, locale
import matplotlib.pyplot as pyplot
from datetime import datetime, timedelta
from copy import deepcopy
import pdb

TIMESTAMP_READ_FORMAT='%Y-%m-%d %H:%M:%S'

def analyse_cluster(report_name : str, observation_start : datetime,
  observation_end : datetime, succesful_tasks_total : int,
  node_wasimoff_usage : list, node_slurm_usage : list,
  node_prolog_usage : list, node_epilog_usage : list, 
  node_idle_usage : list, num_slurm_jobs : int,
  failed_tasks_total : int):
  total_wasimoff_usage = 0.0
  total_slurm_usage = 0.0
  total_prolog = 0.0
  total_epilog = 0.0
  total_idle = 0.0
  num_nodes = len(node_slurm_usage)
  observation_duration = (observation_end - observation_start).total_seconds()
  for i in range(0,len(node_slurm_usage)):
    total_slurm_usage += node_slurm_usage[i]
    total_idle += node_idle_usage[i]
    if len(node_wasimoff_usage) > 0:
      total_wasimoff_usage += node_wasimoff_usage[i]
      total_prolog += node_prolog_usage[i]
      total_epilog += node_epilog_usage[i]

  total_prolog /= num_nodes
  total_epilog /= num_nodes
  total_idle /= num_nodes
  total_wasimoff_usage /= num_nodes
  total_slurm_usage /= num_nodes

  with open(f"{report_name}_cluster.txt", 'w', newline='', encoding='utf-8') as report:
    report_str = f"""Report for cluster
Start of observation:                             {observation_start.isoformat(timespec='microseconds')}
End of observation:                               {observation_end.isoformat(timespec='microseconds')}
Total duration of observation [h:m:s]:            {f"{int(observation_duration / 3600):d}:{int(int(observation_duration / 60) % 60):02d}:{int(observation_duration % 60):02d}"}
Total started wasimoff tasks over whole cluster:  {succesful_tasks_total + failed_tasks_total}
Succesful wasimoff tasks over whole cluster:      {succesful_tasks_total}
Failed wasimoff tasks over whole cluster:         {failed_tasks_total}
Slurm jobs over whole cluster:                    {num_slurm_jobs}
Slurm job throuput [job/h]:                       {(num_slurm_jobs*3600/observation_duration):7f}
Wasimoff task throuput [task/min]:                {(succesful_tasks_total*60/observation_duration):7f}
Slurm utilization in [%]:                         {total_slurm_usage*100:5f}
Wasimoff utilzation in [%]:                       {total_wasimoff_usage*100:5f}
Cluster in prolog in [%]:                         {total_prolog*100:5f}
Cluster in epilog in [%]:                         {total_epilog*100:5f}
Cluster idle in [%]:                              {total_idle*100:5f}
"""
    report.write(report_str)

def color_of_state(state : str) -> str:
  match state:
    case 'slurm':
      return 'g'
    case 'wasi_complete':
      return 'y'
    case 'wasi_abort':
      return 'r'
    case 'idle':
      return 'k'
    case 'prolog':
      return 'c'
    case 'epilog':
      return 'b'

def print_activity_chart(report_name : str,
  observation_start : datetime,
  observation_end : datetime,
  node_time_lines : list):
  fig, ax = pyplot.subplots()
  data_frame_dict = {}
  nodes_num = len(node_time_lines)

  data_frame_dict['node'] = functools.reduce(lambda x, y: x + [f'Node {y}'], range(0,nodes_num), [])

  max_intervalls = max(map(len,node_time_lines))
  for i in range(0,max_intervalls):
    data_frame_dict[f'start_{i}'] = functools.reduce(lambda x, y:
      x + ([node_time_lines[y][i]['start']] if i < len(node_time_lines[y]) else [None]),
      range(0,nodes_num), [])
    data_frame_dict[f'end_{i}'] = functools.reduce(lambda x, y:
      x + ([node_time_lines[y][i]['end']] if i < len(node_time_lines[y]) else [None]),
      range(0,nodes_num), [])
    data_frame_dict[f'state_{i}'] = functools.reduce(lambda x, y:
      x + ([node_time_lines[y][i]['state']] if i < len(node_time_lines[y]) else [None]),
      range(0,nodes_num), [])

  data_frame = pandas.DataFrame(data_frame_dict)
  for i in range(0,max_intervalls):
    data_frame[f'seconds_to_start_{i}'] = (data_frame[f'start_{i}'] - observation_start).dt.total_seconds()
    data_frame[f'seconds_to_end_{i}']   = (data_frame[f'end_{i}'] - observation_end).dt.total_seconds()
    data_frame[f'task_duration_{i}']   = (data_frame[f'end_{i}'] - data_frame[f'start_{i}']).dt.total_seconds()
  
  for index, row in data_frame.iterrows():
    yrange = (index + 1, 0.5)
    xrange = functools.reduce(lambda x, y:
      x + ([(row[f'seconds_to_start_{y}'], row[f'task_duration_{y}'])] if not pandas.isnull(row[f'start_{y}']) else []),
      range(0,max_intervalls), [])
    colors = functools.reduce(lambda x, y:
      x + ([color_of_state(row[f'state_{y}'])] if not pandas.isnull(row[f'state_{y}']) else []),
      range(0,max_intervalls), [])
    ax.broken_barh(xranges=xrange, yrange=yrange, color=colors)

  ax.set_yticks(list(map(lambda x: x + 1.25, range(0,nodes_num))))
  ax.set_yticklabels(data_frame['node'], fontsize=14)

  patches = []
  for state in ['slurm', 'wasi_complete', 'wasi_abort', 'idle', 'prolog', 'epilog']:
    patches.append(
      matplotlib.patches.Patch(
        color=color_of_state(state)))

  ax.legend(handles=patches,
            labels=['slurm', 'wasi_\ncomplete', 'wasi_abort', 'idle', 'prolog', 'epilog'],
            fontsize=12, bbox_to_anchor=(1.135, 0.75))

  pyplot.xticks(fontsize=14)
  pyplot.xlabel('Zeit in s', loc='right', fontsize=16)

  pyplot.gca().invert_yaxis()
  fig.set_figwidth(12)
  pyplot.savefig(report_name + '_plot.png', dpi=500)

def read_slurm_data(dir : str, num_com_nodes : int) -> tuple:
  nodes_slurm_jobs = {}
  slurm_jobs_per_node = {}
  node_names = []
  for i in range(0, num_com_nodes):
    nodes_slurm_jobs[f'com{i}'] = []
    slurm_jobs_per_node[f'com{i}'] = 0
    node_names.append(f'com{i}')

  with os.scandir(dir) as entries:
    for entry in entries:
      mapping = {}
      with open(entry.path, 'r', encoding='utf-8') as file:
        slurmstepd_lines = []
        lines = file.readlines()
        lines = list(filter(lambda x: not x.startswith('srun: ') and not x.startswith('slurmstepd-'), lines))
        num_nodes_in_job = 0
        i = 0
        preemption_found = False
        while (not preemption_found) and i < len(lines):
          split_line = lines[i].split()
          if len(split_line) > 1 and split_line[1].startswith('slurmstepd-'):
            preemption_found = True
          if len(split_line) > 1 and split_line[1] in node_names and not split_line[1] in mapping.values():
            num_nodes_in_job += 1
            mapping[split_line[0]] = split_line[1]
          i += 1
        assert num_com_nodes >= num_nodes_in_job
        i = 0
        while i < len(lines):
          if ': slurmstepd-' in lines[i]:
            slurmstepd_lines.append(i)
            i += num_nodes_in_job
          else:
            i += 1
        for i in range(0,num_nodes_in_job):
          split_line = lines[i].split()
          nodes_slurm_jobs[mapping[split_line[0]]].append(
            {'start' : datetime.fromisoformat(split_line[1][:26] + split_line[1][29:]), 'state' : 'slurm'})
        if slurmstepd_lines:
          for slurmstepd_line_index in slurmstepd_lines:
            # get cancellation time
            for i in range(0, num_nodes_in_job):
              split_line = lines[slurmstepd_line_index + i].split()
              nodes_slurm_jobs[mapping[split_line[0]]][-1]['end'] = datetime.fromisoformat(split_line[-5] + '+02:00')
              nodes_slurm_jobs[mapping[split_line[0]]][-1]['duration'] = (nodes_slurm_jobs[mapping[split_line[0]]][-1]['end'] - 
                nodes_slurm_jobs[mapping[split_line[0]]][-1]['start']).total_seconds()
            # update mapping within job
            for i in range(num_nodes_in_job * 2, num_nodes_in_job * 3):
              split_line = lines[slurmstepd_line_index + i].split()
              mapping[split_line[0]] = split_line[1]
            # add next iteration
            for i in range(num_nodes_in_job, num_nodes_in_job * 2):
              split_line = lines[slurmstepd_line_index + i].split()
              nodes_slurm_jobs[mapping[split_line[0]]].append(
                {'start' : datetime.fromisoformat(split_line[1][:26] + split_line[1][29:]), 'state' : 'slurm'})
        for i in range(-num_nodes_in_job,0):
          split_line = lines[i].split()
          nodes_slurm_jobs[mapping[split_line[0]]][-1]['end'] = datetime.fromisoformat(split_line[1][:26] + split_line[1][29:])
          nodes_slurm_jobs[mapping[split_line[0]]][-1]['duration'] = (nodes_slurm_jobs[mapping[split_line[0]]][-1]['end'] - 
            nodes_slurm_jobs[mapping[split_line[0]]][-1]['start']).total_seconds()
      for mapper in mapping.values():
        slurm_jobs_per_node[mapper] += 1


  return nodes_slurm_jobs, slurm_jobs_per_node

def read_prolog_data(dir : str, num_com_nodes : int) -> dict:
  nodes_prologs = {}
  node_names = []
  for i in range(0, num_com_nodes):
    nodes_prologs[f'com{i}'] = []
    node_names.append(f'com{i}')

  with os.scandir(dir) as entries:
    for entry in entries:
      for name in node_names:
        if name in entry.name:
          with open(entry.path, 'r', encoding='utf-8') as file:
            lines = list(file.readlines())
            prologs_in_file = int(len(lines) / 2)
            for i in range(0,prologs_in_file):
              tmp = lines[i * 2].strip()
              nodes_prologs[name].append({'start' : datetime.fromisoformat(tmp[:26] + tmp[29:]), 'state' : 'prolog'})
              tmp = lines[i * 2 + 1].strip()
              nodes_prologs[name][-1]['end'] = datetime.fromisoformat(tmp[:26] + tmp[29:])
              nodes_prologs[name][-1]['duration'] = (nodes_prologs[name][-1]['end'] -
                nodes_prologs[name][-1]['start']).total_seconds()

  return nodes_prologs

def read_epilog_data(dir : str, num_com_nodes : int) -> dict:
  nodes_epilogs = {}
  node_names = []
  for i in range(0, num_com_nodes):
    nodes_epilogs[f'com{i}'] = []
    node_names.append(f'com{i}')

  with os.scandir(dir) as entries:
    for entry in entries:
      for name in node_names:
        if name in entry.name:
          with open(entry.path, 'r', encoding='utf-8') as file:
            lines = list(file.readlines())
            epilogs_in_file = int(len(lines) / 2)
            for i in range(0,epilogs_in_file):
              tmp = lines[i * 2].strip()
              nodes_epilogs[name].append({'start' : datetime.fromisoformat(tmp[:26] + tmp[29:]), 'state' : 'epilog'})
              tmp = lines[i * 2 + 1].strip()
              nodes_epilogs[name][-1]['end'] = datetime.fromisoformat(tmp[:26] + tmp[29:])
              nodes_epilogs[name][-1]['duration'] = (nodes_epilogs[name][-1]['end'] -
                nodes_epilogs[name][-1]['start']).total_seconds()

  return nodes_epilogs

def analyse_node(observation_start : datetime, observation_end : datetime,
  observation_duration : timedelta, log : str,
  slurm_data : list, prolog_data : list, epilog_data : list,
  num_slurm_jobs : int) -> tuple:
  # initialize objects
  tasks_per_period = [{}]
  effective_tasks_per_period = []
  tasks_total = 0
  succesful_tasks = 0
  failed_tasks = 0
  wasimoff_usage = 0.0
  lost_usage = 0.0
  slurm_usage = 0.0
  prolog_usage = 0.0
  epilog_usage = 0.0
  idle_usage = 0.0
  wasimoff_total_duration = 0
  wasimoff_loss_duration = 0
  slurm_total_duration = 0
  prolog_total_duration = 0
  epilog_total_duration = 0
  idle_total_duration = 0
  time_line = [{'start' : observation_start,
                'end' : observation_start,
                'state' : 'idle',
                'duration' : 0.0}]

  if log.endswith('log'):
    with open(log, 'r', encoding='utf-8') as logfile:
      lines = list(logfile.readlines())

      for i in range(0,len(lines)):
        line = lines[i]
        line_split = line.split()
        if "Task" in line and "completed" in line:
          if line_split[-2] in tasks_per_period[-1].keys():
            succesful_tasks += 1
            tasks_per_period[-1][line_split[-2]]['end'] = datetime.fromisoformat(line_split[0])
            tasks_per_period[-1][line_split[-2]]['state'] = 'wasi_complete'
            tasks_per_period[-1][line_split[-2]]['duration'] = (tasks_per_period[-1][line_split[-2]]['end'] -
              tasks_per_period[-1][line_split[-2]]['start']).total_seconds()
        elif "Start running task" in line:
          tasks_per_period[-1][line_split[-1]] = {'start' : datetime.fromisoformat(line_split[0]), 'state' : 'wasi_abort'}
          tasks_total += 1
        elif "[Wasimoff] starting Provider in Deno" in line:
          tasks_per_period.append({})
        elif "aborted tasks" in line:
          for task_id in tasks_per_period[-1].keys():
            if tasks_per_period[-1][task_id]['state'] == 'wasi_abort':
              tasks_per_period[-1][task_id]['end'] = datetime.fromisoformat(line_split[0])
              tasks_per_period[-1][task_id]['duration'] = (tasks_per_period[-1][task_id]['end'] -
                tasks_per_period[-1][task_id]['start']).total_seconds()
        elif "Stopped wasimoff_provider.service" in line:
          for task_id in tasks_per_period[-1].keys():
            if not 'end' in tasks_per_period[-1][task_id].keys():
              tasks_per_period[-1][task_id]['end'] = datetime.fromisoformat(line_split[0])
              tasks_per_period[-1][task_id]['duration'] = (tasks_per_period[-1][task_id]['end'] -
                tasks_per_period[-1][task_id]['start']).total_seconds()
        if i == len(lines) - 1:
          for task_id in tasks_per_period[-1].keys():
            if not 'end' in tasks_per_period[-1][task_id].keys():
              tasks_per_period[-1][task_id]['end'] = observation_end
              tasks_per_period[-1][task_id]['duration'] = (tasks_per_period[-1][task_id]['end'] -
                tasks_per_period[-1][task_id]['start']).total_seconds()

    for tasks in tasks_per_period:
      if not tasks == {}:
        sorted_tasks = sorted(tasks.values(), key=lambda dic: (dic['start'], dic['end']))
        sorted_task_period_complete = list(filter(lambda x: x['state'] == 'wasi_complete', sorted_tasks))
        sorted_task_period_abort = list(filter(lambda x: x['state'] == 'wasi_abort', sorted_tasks))
        tmp = 1
        while tmp < len(sorted_task_period_complete):
          if sorted_task_period_complete[tmp]['end'] <= sorted_task_period_complete[tmp - 1]['end']:
            del sorted_task_period_complete[tmp]
          elif sorted_task_period_complete[tmp]['start'] <= sorted_task_period_complete[tmp - 1]['end']:
            sorted_task_period_complete[tmp - 1]['end'] = sorted_task_period_complete[tmp]['end']
            del sorted_task_period_complete[tmp]
            sorted_task_period_complete[tmp - 1]['duration'] = (sorted_task_period_complete[tmp - 1]['end'] -
              sorted_task_period_complete[tmp - 1]['start']).total_seconds()
          else:
            tmp += 1
        tmp = 1
        while tmp < len(sorted_task_period_abort):
          if sorted_task_period_abort[tmp]['end'] <= sorted_task_period_abort[tmp - 1]['end']:
            del sorted_task_period_abort[tmp]
          elif sorted_task_period_abort[tmp]['start'] <= sorted_task_period_abort[tmp - 1]['end']:
            sorted_task_period_abort[tmp - 1]['end'] = sorted_task_period_abort[tmp]['end']
            del sorted_task_period_abort[tmp]
            sorted_task_period_abort[tmp - 1]['duration'] = (sorted_task_period_abort[tmp - 1]['end'] -
              sorted_task_period_abort[tmp - 1]['start']).total_seconds()
          else:
            tmp += 1
        if len(sorted_task_period_complete) > 0:
          i = 0
          j = 0
          while i < len(sorted_task_period_complete) or j < len(sorted_task_period_abort):
            if i >= len(sorted_task_period_complete):
              if effective_tasks_per_period[-1]['end'] > sorted_task_period_abort[j]['start']:
                if effective_tasks_per_period[-1]['end'] > sorted_task_period_abort[j]['end']:
                  raise Exception('there cannot be completed tasks after aborted ones')
                else:
                  effective_tasks_per_period.append(
                    sorted_task_period_abort[j])
                  effective_tasks_per_period[-1]['start'] = effective_tasks_per_period[-2]['end']
                  effective_tasks_per_period[-1]['duration'] = (effective_tasks_per_period[-1]['end'] -
                    effective_tasks_per_period[-1]['start']).total_seconds()
                  j += 1
              else:
                effective_tasks_per_period.append(
                  sorted_task_period_abort[j])
                j += 1
            elif j < len(sorted_task_period_abort):
              if sorted_task_period_complete[i]['start'] < sorted_task_period_abort[j]['start']:
                effective_tasks_per_period.append(
                  sorted_task_period_complete[i])
                i += 1
              else:
                if i > 0 and effective_tasks_per_period[-1]['end'] > sorted_task_period_abort[j]['start']:
                  if effective_tasks_per_period[-1]['end'] > sorted_task_period_abort[j]['end']:
                    raise Exception('there cannot be completed tasks after aborted ones')
                  else:
                    effective_tasks_per_period.append(
                      sorted_task_period_abort[j])
                    effective_tasks_per_period[-1]['start'] = effective_tasks_per_period[-2]['end']
                    effective_tasks_per_period[-1]['duration'] = (effective_tasks_per_period[-1]['end'] -
                      effective_tasks_per_period[-1]['start']).total_seconds()
                    j += 1
                else:
                  effective_tasks_per_period.append(sorted_task_period_abort[j])
                  j += 1
            else:
              if effective_tasks_per_period[-1]['end'] > sorted_task_period_complete[i]['end']:
                effective_tasks_per_period.append(
                  sorted_task_period_complete[i])
                effective_tasks_per_period.append(
                  deepcopy(effective_tasks_per_period[-2]))
                effective_tasks_per_period[-3]['end'] = effective_tasks_per_period[-2]['start']
                effective_tasks_per_period[-3]['duration'] = (effective_tasks_per_period[-3]['end'] -
                  effective_tasks_per_period[-3]['start']).total_seconds()
                effective_tasks_per_period[-1]['start'] = effective_tasks_per_period[-2]['end']
                effective_tasks_per_period[-1]['duration'] = (effective_tasks_per_period[-1]['end'] -
                  effective_tasks_per_period[-1]['start']).total_seconds()
                i += 1
              else:
                if len(sorted_task_period_abort) > 0:
                  raise Exception('there cannot be completed tasks after aborted ones')
                else:
                  effective_tasks_per_period.append(sorted_task_period_complete[i])
                  i += 1
        else:
          effective_tasks_per_period += sorted_task_period_abort
    for i in range(0,len(effective_tasks_per_period) - 1):
      assert effective_tasks_per_period[i]['end'] <= effective_tasks_per_period[i + 1]['start']

  sorted_slurm_data = sorted(slurm_data, key=lambda dic: (dic['start'], dic['end']))
  tmp = 1
  while tmp < len(sorted_slurm_data):
    if sorted_slurm_data[tmp]['end'] <= sorted_slurm_data[tmp - 1]['end']:
      del sorted_slurm_data[tmp]
    elif sorted_slurm_data[tmp]['start'] <= sorted_slurm_data[tmp - 1]['end']:
      sorted_slurm_data[tmp - 1]['end'] = sorted_slurm_data[tmp]['end']
      del sorted_slurm_data[tmp]
      sorted_slurm_data[tmp - 1]['duration'] = (sorted_slurm_data[tmp - 1]['end'] -
        sorted_slurm_data[tmp - 1]['start']).total_seconds()
    else:
      tmp += 1
  tmp_list = sorted(sorted_slurm_data +
    prolog_data +
    effective_tasks_per_period +
    epilog_data,
    key=lambda dic: (dic['start'], dic['end']))
  tmp = 0
  tmp2 = 1
  while tmp < len(tmp_list) and tmp_list[tmp]['start'] <= observation_end:
    tmp2 = 1
    if len(time_line) > 0 and (tmp_list[tmp]['start'] -
                              time_line[-1]['end']).total_seconds() > 0:
      time_line.append({'start' : time_line[-1]['end'],
                'end' : tmp_list[tmp]['start'],
                'duration' : (tmp_list[tmp]['start'] - time_line[-1]['end']).total_seconds(),
                'state' : 'idle'})
    if tmp_list[tmp]['state'] == 'slurm':
      if (time_line[-1]['state'] == 'prolog' 
          and time_line[-1]['end'] > tmp_list[tmp]['start']):
        time_line[-1]['end'] = tmp_list[tmp]['start']
      time_line.append(deepcopy(tmp_list[tmp]))
      while tmp + tmp2 < len(tmp_list):
        if tmp_list[tmp]['end'] <= tmp_list[tmp + tmp2]['start']:
          break
        if tmp_list[tmp + tmp2]['state'] == 'prolog':
          time_line.append(tmp_list[tmp + tmp2])
          time_line.append({'start' : time_line[-1]['end'], 'end' : tmp_list[tmp]['end'], 'state' : 'slurm'})
          time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()
          time_line[-3]['end'] = tmp_list[tmp + tmp2]['start']
          time_line[-3]['duration'] = (time_line[-3]['end'] - time_line[-3]['start']).total_seconds()
        elif tmp_list[tmp + tmp2]['state'] == 'epilog':
          time_line.append(tmp_list[tmp + tmp2])
          time_line.append({'start' : time_line[-1]['end'], 'end' : tmp_list[tmp]['end'], 'state' : 'slurm'})
          time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()
          time_line[-3]['end'] = tmp_list[tmp + tmp2]['start']
          time_line[-3]['duration'] = (time_line[-3]['end'] - time_line[-3]['start']).total_seconds()
        tmp2 += 1
    elif tmp_list[tmp]['state'] == 'prolog':
      if (not 'epilog' in time_line[-1]['state'] 
          and time_line[-1]['end'] > tmp_list[tmp]['start']):
        time_line.append(deepcopy(tmp_list[tmp]))
        time_line[-1]['start'] = time_line[-2]['end']
        time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()
      else:
        if (tmp_list[tmp]['end'] - tmp_list[tmp]['start']).total_seconds() != 0.0:
          time_line.append(tmp_list[tmp])
      while tmp_list[tmp]['end'] > tmp_list[tmp + tmp2]['end']:
        time_line[-1]['end'] = tmp_list[tmp + tmp2]['start']
        time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()
        time_line.append(tmp_list[tmp + tmp2])
        time_line.append({
          'start' : time_line[-1]['end'],
          'end' : tmp_list[tmp]['end'],
          'state' : 'prolog',
          'duration' : (tmp_list[tmp]['end'] - time_line[-1]['end']).total_seconds()
        })
        tmp2 += 1
    else:
      if (tmp_list[tmp]['end'] - tmp_list[tmp]['start']).total_seconds() != 0.0:
        time_line.append(tmp_list[tmp])
    tmp += tmp2

  if time_line[-1]['end'] < observation_end:
    time_line.append({
      'start' : time_line[-1]['end'],
      'end' : observation_end,
      'state' : 'idle',
      'duration' : (observation_end - time_line[-1]['end']).total_seconds(),
    })
  elif time_line[-1]['end'] > observation_end:
    time_line[-1]['end'] = observation_end
    time_line[-1]['duration'] = (time_line[-1]['end'] - time_line[-1]['start']).total_seconds()

  i = 0
  for i in range(0,len(time_line) - 1):
    assert time_line[i]['end'] <= time_line[i + 1]['start']

  with open(f"{log}.csv", 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['intervall','state','start',
                  'end','duration','duration_perc']
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
        case 'wasi_complete' :
          wasimoff_total_duration += time_slot['duration']
        case 'wasi_abort' :
          wasimoff_loss_duration += time_slot['duration']
        case 'slurm' :
          slurm_total_duration += time_slot['duration']
        case 'epilog' :
          epilog_total_duration += time_slot['duration']
        case 'prolog' :
          prolog_total_duration += time_slot['duration']
        case 'idle' :
          idle_total_duration += time_slot['duration']
      time_line_index += 1

    wasimoff_usage = wasimoff_total_duration / observation_duration
    lost_usage = wasimoff_loss_duration / observation_duration
    slurm_usage = slurm_total_duration / observation_duration
    prolog_usage = prolog_total_duration / observation_duration
    epilog_usage = epilog_total_duration / observation_duration
    idle_usage = idle_total_duration / observation_duration

    failed_tasks = tasks_total - succesful_tasks

    writer = csv.writer(csvfile)
    writer.writerow(["total duration of observation run in [h:m:s]", f"{int(observation_duration / 3600):d}:{int(int(observation_duration / 60) % 60):02d}:{int(observation_duration % 60):02d}"])
    writer.writerow(["wasimoff node usage in [%]", f"{wasimoff_usage * 100:5f}"])
    writer.writerow(["wasimoff node usage lost to abortion in [%]", f"{lost_usage * 100:5f}"])
    writer.writerow(["slurm node usage in %", f"{slurm_usage * 100:5f}"])
    writer.writerow(["time in prolog on node relative to observation [%]", f"{prolog_usage * 100:5f}"])
    writer.writerow(["time in epilog on node relative to observation [%]", f"{epilog_usage * 100:5f}"])
    writer.writerow(["time in idle on node relative to observation [%]", f"{idle_usage * 100:5f}"])
    writer.writerow(["number of succesful wasimoff tasks", succesful_tasks])
    writer.writerow(["number of failed wasimoff tasks", failed_tasks])
    writer.writerow(["number of slurm jobs", num_slurm_jobs])
    writer.writerow(["wasimoff throughput on node in [task/min]", f"{(succesful_tasks*60/observation_duration):7f}"])
    writer.writerow(["slurm throughput on node in [job/h]", f"{(num_slurm_jobs*3600/observation_duration):7f}"])

  return succesful_tasks, time_line, wasimoff_usage, slurm_usage, prolog_usage, epilog_usage, idle_usage, failed_tasks

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
  parser.add_argument("-p", required=True, help="set directory with prolog timestamp files of observed compute nodes", metavar="com node prolog stamps directory", dest="prolog_stamps")
  parser.add_argument("-e", required=True, help="set directory with epilog timestamp files of observed compute nodes", metavar="com node epilog stamps directory", dest="epilog_stamps")
  args = parser.parse_args()

  try:
    tmp = os.scandir(args.wasimoff_logs)
    num_nodes = len(list(filter(lambda x: x.name.endswith('.log'), tmp)))
    tmp.close()
  except NotADirectoryError:
    raise SystemExit('-l argument is required to be a directory')

  try:
    tmp = os.scandir(args.slurm_logs)
    num_slurm_jobs = len(list(tmp))
    tmp.close()
  except NotADirectoryError:
    raise SystemExit('-s argument is required to be a directory')

  if num_nodes == 0:
    num_nodes = 3

  # initialize timestamp objects
  observation_start = 0
  observation_end = 0
  observation_duration = 0
  
  # succesful_tasks, periods, active_periods, wasimoff_usage, wasimoff_total_active
  # initialize objects for cluster
  failed_tasks_total = 0
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
    observation_start = datetime.fromisoformat(tmp[:26] + tmp[29:])
    observation_start -= timedelta(microseconds=observation_start.microsecond)
    tmp = timestamps.readline().strip()
    observation_end = datetime.fromisoformat(tmp[:26] + tmp[29:])
    observation_end += timedelta(seconds=1,microseconds=-observation_end.microsecond)
    observation_duration = (observation_end - observation_start).total_seconds()

  # read slurm job data
  slurm_data, slurm_jobs_per_node = read_slurm_data(args.slurm_logs, num_nodes)

  # read prolog stamps
  prolog_data = read_prolog_data(args.prolog_stamps, num_nodes)
  
  # read epilog stamps
  epilog_data = read_epilog_data(args.epilog_stamps, num_nodes)

  # read and analyse 
  entries = list(os.scandir(args.wasimoff_logs))
  if entries == []:
    for node_name in slurm_data.keys():
      succesful_tasks, time_line, wasimoff_usage, slurm_usage, prolog_usage, epilog_usage, idle_usage, failed_tasks = analyse_node(
        observation_start, observation_end, observation_duration,
        f"{args.timestamp_file}_{node_name}", slurm_data[node_name],
        prolog_data[node_name], epilog_data[node_name], slurm_jobs_per_node[node_name])
      node_time_lines.append(time_line)
      node_slurm_usage.append(slurm_usage)
      node_idle_usage.append(idle_usage)
  else:
    for entry in entries:
      if entry.name.endswith('.log'):
        node_name = entry.name.split('_')[-1].split('.')[0]
        succesful_tasks, time_line, wasimoff_usage, slurm_usage, prolog_usage, epilog_usage, idle_usage, failed_tasks = analyse_node(
          observation_start, observation_end, observation_duration,
          entry.path, slurm_data[node_name],
          prolog_data[node_name], epilog_data[node_name], slurm_jobs_per_node[node_name])
        failed_tasks_total += failed_tasks
        succesful_tasks_total += succesful_tasks
        node_time_lines.append(time_line)
        node_wasimoff_usage.append(wasimoff_usage)
        node_slurm_usage.append(slurm_usage)
        node_prolog_usage.append(prolog_usage)
        node_epilog_usage.append(epilog_usage)
        node_idle_usage.append(idle_usage)

  analyse_cluster(args.timestamp_file.split('.')[0], observation_start, observation_end, succesful_tasks_total, 
          node_wasimoff_usage, node_slurm_usage, node_prolog_usage, node_epilog_usage, node_idle_usage, num_slurm_jobs, failed_tasks_total)
  print_activity_chart(args.timestamp_file.split('.')[0], observation_start, observation_end, node_time_lines)


if __name__ == '__main__':
  main()