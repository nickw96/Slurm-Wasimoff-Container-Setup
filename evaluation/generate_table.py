import matplotlib.patches
import os, sys, argparse, csv, matplotlib, pandas, numpy, functools, locale
import matplotlib.pyplot as pyplot
from datetime import datetime, timedelta
from copy import deepcopy


def main():
  reports = []

  locale.setlocale(locale.LC_ALL,'')
  parser = argparse.ArgumentParser(
  prog="",
  description="Analyse usage of compute node and cluster",
  epilog="Break down usage of individual compute nodes to percentage of non-utilization, usage via wasimoff and usage via slurm"
  )
  parser.add_argument("-d", required=True, help="set directory of experiment data", metavar="directory with data", dest="dir")
  parser.add_argument("-s", required=True, help="set amount of slurm jobs", metavar="amount of slurm jobs", dest="slurm_jobs")
  parser.add_argument("-n", required=True, help="set amount of nodes in cluster", metavar="amount of nodes", dest="nodes_num")
  args = parser.parse_args()

  with os.scandir(args.dir) as dir:
    for entry in dir:
      if entry.is_dir():
        with os.scandir(entry) as data_dir:
          for data_entry in data_dir:
            if not data_entry.is_dir() and data_entry.name.endswith('cluster.txt'):
              reports.append((entry.name, data_entry))
              break

  with open(f"{args.dir}\\{args.dir.split('\\')[-1]}_report_table.csv", 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['series','duration','tasks_total','tasks_succeded','tasks_failed','slurm_throuput','wasimoff_throuput','slurm_utilization','wasimoff_utilization','percentage_in_prolog','percentage_in_epilog','percentage_in_idle']
    rows = []
    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    # csvwriter.writeheader()
    csvwriter.writerow({
    'series' : 'Versuchsreihe',
      'duration' : 'Gesamtlaufzeit [s]',
      'tasks_total' : 'Gesamtmenge\nWasimoff\nTasks',
      'tasks_succeded' : 'Abgeschlossene\nTasks',
      'tasks_failed' : 'Abgebrochene\nTasks',
      'slurm_throuput' : 'Durchsatz\nSlurm [Job/s]',
      'wasimoff_throuput' : 'Durchsatz\nWasimoff\n[Task/s]',
      'slurm_utilization' : 'Clusternutzung\nSlurm [%]',
      'wasimoff_utilization' : 'Clusternutzung\nWasimoff [%]',
      'percentage_in_prolog' : 'Anteil Zeit\nin Prologen\nverbracht',
      'percentage_in_epilog' : 'Anteil Zeit\nin Epilogen\nverbracht',
      'percentage_in_idle' : 'Anteil Zeit\ninaktiv'
    })
    for report in reports:
      with open(report[1], 'r', encoding='utf-8', newline='') as report_file:
        lines = report_file.readlines()
        rows.append({
          'series' : report[0].split('_')[-2] + "_" + report[0].split('_')[-1] if report[0].split('_')[-1] == 'pure' else report[0].split('_')[-1],
          'duration' : lines[3].split()[-1],
          'tasks_total' : lines[4].split()[-1],
          'tasks_succeded' : lines[5].split()[-1],
          'tasks_failed' : lines[6].split()[-1],
          'slurm_throuput' : lines[8].split()[-1],
          'wasimoff_throuput' : lines[9].split()[-1],
          'slurm_utilization' : lines[10].split()[-1],
          'wasimoff_utilization' : lines[11].split()[-1],
          'percentage_in_prolog' : lines[12].split()[-1],
          'percentage_in_epilog' : lines[13].split()[-1],
          'percentage_in_idle' : lines[14].split()[-1]
        })
    csvwriter.writerows(sorted(rows, key=lambda dic: dic['series']))
    csvwriter.writerow({
      'series' : 'Anzahl Rechenknoten\nin Cluster',
      'duration' : args.nodes_num
    })
    csvwriter.writerow({
      'series' : 'Anzahl Slurm Jobs\nin Versuch',
      'duration' : args.slurm_jobs
    })

if __name__ == '__main__':
  main()