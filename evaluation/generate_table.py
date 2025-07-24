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
    csvwriter.writeheader()
    # csvwriter.writerow({
    # 'series' : 'Versuchsreihe',
    #   'duration' : 'Gesamtlaufzeit [h:m:s]',
    #   'tasks_total' : 'Gesamtmenge Wasimoff Tasks',
    #   'tasks_succeded' : 'Abgeschlossene Tasks',
    #   'tasks_failed' : 'Abgebrochene Tasks',
    #   'slurm_throuput' : 'Durchsatz Slurm [Job/h]',
    #   'wasimoff_throuput' : 'Durchsatz Wasimoff [Task/min]',
    #   'slurm_utilization' : 'Clusternutzung Slurm [%]',
    #   'wasimoff_utilization' : 'Clusternutzung Wasimoff [%]',
    #   'percentage_in_prolog' : 'Anteil Zeit in Prologen verbracht [%]',
    #   'percentage_in_epilog' : 'Anteil Zeit in Epilogen verbracht [%]',
    #   'percentage_in_idle' : 'Anteil Zeit inaktiv [%]'
    # })
    for report in reports:
      with open(report[1], 'r', encoding='utf-8', newline='') as report_file:
        lines = report_file.readlines()
        rows.append({
          'series' : (report[0].split('_')[-2] + "_" + report[0].split('_')[-1] if report[0].split('_')[-1] == 'pure' else report[0].split('_')[-1]).replace('_','\\_'),
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
    # csvwriter.writerow({
    #   'series' : 'Anzahl Rechenknoten in Cluster',
    #   'duration' : args.nodes_num
    # })
    # csvwriter.writerow({
    #   'series' : 'Anzahl Slurm Jobs in Versuch',
    #   'duration' : args.slurm_jobs
    # })
  
  width = 3.0

  # duration
  # for i in range(0,len(rows)):
  #   ax.bar(6.0 * i, functools.reduce(lambda acc, x: acc + int(rows[i]['duration'].split(':')[x]) * 60 ** (2 - x),
  #                                range(0, len(rows[i]['duration'].split(':'))), 0.0),
  #                                width=width,
  #                                label=rows[i]['series'])

  # duration
  fig, ax = pyplot.subplots()
  translation_table = dict.fromkeys(map(ord, '_-'), '\n')
  ax.bar([(6.0) * i for i in range(0,len(rows))],
              [functools.reduce(lambda acc, x: acc + int(row['duration'].split(':')[x]) * 60 ** (2 - x),
                                 range(0, len(row['duration'].split(':'))), 0.0) for row in rows],
                                 width=width)
  ax.set_ylabel('Zeit in s')
  ax.set_title('Versuchsdauer nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows))], [row['series'].translate(translation_table) for row in rows], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_duration.png', dpi=500)

  # Throughput Slurm
  fig, ax = pyplot.subplots()
  ax.bar([(6.0) * i for i in range(0,len(rows))], [float(row['slurm_throuput']) for row in rows], width=width)
  ax.set_ylabel('Durchsatz in Job/h')
  ax.set_title('Slurm-Durchsatz nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows))], [row['series'].translate(translation_table) for row in rows], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_slurm_throughput.png', dpi=500)

  # Cluster utilization slurm
  fig, ax = pyplot.subplots()
  ax.bar([(6.0) * i for i in range(0,len(rows))], [float(row['slurm_utilization']) for row in rows], width=width)
  ax.set_ylabel('Clusternutzung in %')
  ax.set_title('Slurm-Clusternutzung nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows))], [row['series'].translate(translation_table) for row in rows], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_slurm_utilization.png', dpi=500)

  rows_non_pure = [row for row in rows if not 'pure' in row['series']]

  # Throughput Wasimoff
  fig, ax = pyplot.subplots()
  ax.bar([(6.0) * i for i in range(0,len(rows_non_pure))], [float(row['wasimoff_throuput']) for row in rows_non_pure], width=width)
  ax.set_ylabel('Durchsatz in Task/min')
  ax.set_title('Wasimoff-Durchsatz nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows_non_pure))], [row['series'].translate(translation_table) for row in rows_non_pure], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_wasimoff_throughput.png', dpi=500)

  # Cluster utilization Wasimoff
  fig, ax = pyplot.subplots()
  ax.bar([(6.0) * i for i in range(0,len(rows_non_pure))], [float(row['wasimoff_utilization']) for row in rows_non_pure], width=width)
  ax.set_ylabel('Clusternutzung in %')
  ax.set_title('Wasimoff-Clusternutzung nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows_non_pure))], [row['series'].translate(translation_table) for row in rows_non_pure], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_wasimoff_utilization.png', dpi=500)

  # Cluster idle
  fig, ax = pyplot.subplots()
  ax.bar([(6.0) * i for i in range(0,len(rows))], [float(row['percentage_in_idle']) for row in rows], width=width)
  ax.set_ylabel('Clusternutzung in %')
  ax.set_title('Clusterinaktivität nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows))], [row['series'] for row in rows], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_idle.png', dpi=500)

if __name__ == '__main__':
  main()