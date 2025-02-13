Aufbau Slurm-Wasimoff auf Containerbasis:
- Bridge Netzwerk ermöglicht nahtlose Netzwerkverbindung zwischen Containern (Wasimoff+)
- Für Slurm ist zusätzlich systemd notwendig (erfordert systemd als `init`)
- Wasimoff: Einrichtung vergleichsweise einfach (Deno-Bin + Kopieren notwendiger Ordner)
 - Provider benötigt zwei Ordner aus dem Repo (etwas ungünstig gelöst, aber nicht problematisch)
 - Broker-Adresse muss gesetzt werden auf die Adresse des Controller-Knoten (geht über `container name`)
- Slurm
 - Aufbau auf Basis der Sourcen von SchedMD umständlich (benötigt sehr viel Extra Kram)
  - Muss im Container gebaut werden
  - Zusätzliche Einrichtung der Infrastruktur nötig (slurm-user, Ordner aus der slurm.conf + Zugriffsrechte/Besitz an slurm-user, systemd/dbus, evtl. cgroups nach cgroups.conf)
