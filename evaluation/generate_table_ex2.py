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
  # parser.add_argument("-s", required=True, help="set amount of slurm jobs", metavar="amount of slurm jobs", dest="slurm_jobs")
  # parser.add_argument("-n", required=True, help="set amount of nodes in cluster", metavar="amount of nodes", dest="nodes_num")
  args = parser.parse_args()

  with os.scandir(args.dir) as dir:
    for entry in dir:
      if entry.is_dir():
        with os.scandir(entry.path+'\\wasimoff') as data_dir:
          for data_entry in data_dir:
            if not data_entry.is_dir() and data_entry.name.endswith('com2.log.csv'):
              reports.append((entry.name, data_entry))
              break

  rows = []
  with open(f"{args.dir}\\{args.dir.split('\\')[-1]}_wasimoff_performance.csv", 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['series','duration','wasimoff_utilization','wasimoff_util_abort','tasks_total','tasks_succeded','tasks_failed','wasimoff_throuput','percentage_in_prolog','percentage_in_epilog','percentage_in_idle']
    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csvwriter.writeheader()
    # csvwriter.writerow({
    # 'series' : 'Versuchsreihe',
    #   'duration' : 'Gesamtlaufzeit [h:m:s]',
    #   'wasimoff_utilization' : 'Clusternutzung Wasimoff [%]',
    #   'wasimoff_util_abort' : 'Verlorene Clusternutzung Wasimoff durch Abbruch[%]',
    #   'tasks_succeded' : 'Abgeschlossene Tasks',
    #   'tasks_failed' : 'Abgebrochene Tasks',
    #   'wasimoff_throuput' : 'Durchsatz Wasimoff [Task/min]',
    #   'percentage_in_prolog' : 'Anteil Zeit in Prologen verbracht',
    #   'percentage_in_epilog' : 'Anteil Zeit in Epilogen verbracht',
    #   'percentage_in_idle' : 'Anteil Zeit inaktiv'
    # })
    for report in reports:
      with open(report[1], 'r', encoding='utf-8', newline='') as report_file:
        lines = report_file.readlines()
        rows.append({
          'series' : (report[0].split('_')[-1]).replace('_','\\_'),
          'duration' : lines[-12].split(',')[-1].strip(),
          'wasimoff_utilization' : lines[-11].split(',')[-1].strip(),
          'wasimoff_util_abort' : lines[-10].split(',')[-1].strip(),
          'tasks_total' : str(int(lines[-5].split(',')[-1]) + int(lines[-4].split(',')[-1])),
          'tasks_succeded' : lines[-5].split(',')[-1].strip(),
          'tasks_failed' : lines[-4].split(',')[-1].strip(),
          'wasimoff_throuput' : lines[-2].split(',')[-1].strip(),
          'percentage_in_prolog' : lines[-8].split(',')[-1].strip(),
          'percentage_in_epilog' : lines[-7].split(',')[-1].strip(),
          'percentage_in_idle' : lines[-6].split(',')[-1].strip()
        })
    csvwriter.writerows(sorted(rows, key=lambda dic: dic['series']))
    # csvwriter.writerow({
    #   'series' : 'Anzahl Rechenknoten\nin Cluster',
    #   'duration' : args.nodes_num
    # })
    # csvwriter.writerow({
    #   'series' : 'Anzahl Slurm Jobs\nin Versuch',
    #   'duration' : args.slurm_jobs
    # })

  width = 3.0
  # Throughput Wasimoff
  fig, ax = pyplot.subplots()
  ax.bar([(6.0) * i for i in range(0,len(rows))], [float(row['wasimoff_throuput']) for row in rows], width=width)
  ax.set_ylabel('Durchsatz in Task/min')
  ax.set_title('Wasimoff-Durchsatz nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows))], [row['series'] for row in rows], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_node_wasimoff_throughput.png', dpi=500)

  # Cluster utilization Wasimoff
  fig, ax = pyplot.subplots()
  ax.bar([(6.0) * i for i in range(0,len(rows))], [float(row['wasimoff_utilization']) for row in rows], width=width)
  ax.set_ylabel('Knotennutzung in %')
  ax.set_title('Wasimoff-Knotennutzung nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows))], [row['series'] for row in rows], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_node_wasimoff_utilization.png', dpi=500)

  # Cluster Wasimoff loss
  fig, ax = pyplot.subplots()
  ax.bar([(6.0) * i for i in range(0,len(rows))], [float(row['wasimoff_util_abort']) for row in rows], width=width)
  ax.set_ylabel('Knotennutzung in %')
  ax.set_title('Verlorene Wasimoff-Nutzung nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows))], [row['series'] for row in rows], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_node_wasimoff_util_abort.png', dpi=500)

  # Cluster idle
  fig, ax = pyplot.subplots()
  ax.bar([(6.0) * i for i in range(0,len(rows))], [float(row['percentage_in_idle']) for row in rows], width=width)
  ax.set_ylabel('Knotennutzung in %')
  ax.set_title('Knoteninaktivität nach Reihe')
  ax.set_xticks([(6.0) * i for i in range(0,len(rows))], [row['series'] for row in rows], fontsize=7)
  pyplot.savefig(f'{args.dir}\\{args.dir.split('\\')[-1]}_node_wasimoff_idle.png', dpi=500)
  

if __name__ == '__main__':
  main()