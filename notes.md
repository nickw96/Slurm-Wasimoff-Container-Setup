Aufbau Slurm-Wasimoff auf Containerbasis:
- Bridge Netzwerk ermöglicht nahtlose Netzwerkverbindung zwischen Containern (Wasimoff+)
- Für Slurm ist zusätzlich systemd notwendig (erfordert systemd als `init`)
- Wasimoff: Einrichtung vergleichsweise einfach (Deno-Bin + Kopieren notwendiger Ordner)
 - Provider benötigt zwei Ordner aus dem Repo (etwas ungünstig gelöst, aber nicht problematisch)
 - Broker-Adresse muss gesetzt werden auf die Adresse des Controller-Knoten (geht über `container name` bzw. `compose.yaml`)
- Slurm
 - Aufbau auf Basis der Sourcen von SchedMD umständlich (benötigt sehr viel Extra Kram)
  - Muss im Container gebaut werden
  - Zusätzliche Einrichtung der Infrastruktur nötig (slurm-user, Ordner aus der slurm.conf + Zugriffsrechte/Besitz an slurm-user, systemd/dbus, evtl. cgroups nach cgroups.conf, Wahl eines spezifischen Image mit systemd und `sbin/init` als Applikation)
  - Unabhängig von der Wahl des Werts von `ProctrackType` konnte mittels podman kein slurmd ausgeführt werden
- Künftig prüfen, ob VM-Aufbau auf Container umgemüntzt werden kann

Aufbau Slurm-Wasimoff in VMs:
- Bridge Netzwerk potentiell am geeignetesten
- Wasimoff potentiell direkt einsatzfähilg -> Inzwischen einsatzfähig
- Bauen von Slurm aus Sourcen scheinbar wieder umständlich -> Umschwung auf apt -> Deutlich erfolgreicher
- Wasimoff Broker als Service theoretisch möglich, jedoch in der Umsetzung bisher Schwierigkeiten bzw. Service nicht erfolgreich gestartet und somit auch nicht der Broker -> Gelöst über Restart
 - Nachträgliches Starten vom Broker denkbar, nur wie?
 - Als Service, jedoch Bauen des Broker über `go build` notwendig
 - Statisches Setzen der IP bisher notwendig -> IP offenlassen bei Broker
- Wasimoff Provider kann nicht einfach von Epilog aufgerufen werden, da sonst Epilog nicht abgeschlossen werden kann -> Gelöst über systemd Service

Erste Versuche:
- Auf einzelnen Knoten Slurm und Wasimoff Auslastung messbar
- Wasimoffdurchsatz nur auf Annahme aus Rechenknotenlogs bestimmbar (insofern nur eine Mutmaßung)
- Clover kann zu einem Out of Memory Fehler führen falls zu groß dimensioniert


Test der Slurmkonfigurationen offen
- Speichereinstellungen kritisch, evtl. zu wenig Speicher für Jobs verfügbar bei Oversubscribe