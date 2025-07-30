# Slurm-Wasimoff-Container-Setup
Das vorliegende Repository ist eine Ansammlung von Ressourcen, Werkzeugen, archivierten Daten und Notizen.
Hier sind die Versuchsdaten und die Werkzeugen für deren Auswertung aus der Arbeit ***Entwicklung und Untersuchung der Clusterauslastung eines Hybridsystem aus Slurm und Wasimoff*** abgelegt.
Die Unterteilung des Repositorys ist in der unten stehenden Tabelle abgebildet.

| Ordner               | Typ            | Kurzbeschreibung   |
| :------------------- | :------------- | :------------------|
| .vscode | Ressourcen | Run-Konfigurationen für VS Code |
| CloverLeaf_Serial, Proxels | Testressourcen | Enthalten nötige Anwendungen, die für die Generierung der Aufgabenlast genutzt wurden |
| (computer\|controller)-node | Relikt | Ansätze für Containerabbilder der Knoten |
| data-ex\* | Versuchsdaten | Archivierte Analysedaten aus den Versuchen. Unterteilt in die Versuche und Reihen. |
| evaluation | Werkzeuge | Analysewerkzeuge, um Analysedaten zu vearbeiten und zusammenzuführen |
| jobs | Testressourcen | Job-Skripte für die Versuche |
| prototype | Ressourcen | Modifizierte Wasimoff-implementierung für die Woche. Beinhaltet auch eine TSP-Implementierung in Rust |
| slurm-resources | Ressourcen | Enthält die nötigen Ressourcen, um ein Hybridsystem aus Slurm und Wasimoff zu implementieren |
| testing | Werkzeuge | Automatisierungsskripte, die für die Erhebung von Anlaysedaten genutzt wurden |
| wasi-sdk | Ressource | Skript zu Herunterladen des verwendeten Version des wasi-sdk |
| auto_eval.bat, auto_generate_tables.bat | Skripte | Automatisierungsskripte um die Analysen automatisch für alle Reihen/Versuche durchzuführen |
| compose, Dockerfile | Implementierung | Ansatz für eine Implementierung mittels Container (benötigt Podman) |
| notes.md                  | Forschungsnotizen | Unorganisierte Notizen zu Erkenntnissen in der Entwicklung des Hybridsystems sowie Versuche |


## Aufsetzen des VM Aufbaus
Voraussetzung: 
- IP-Adressen der VMs sind bekannt,
- Die VMs sind über eine Netzwerkbrücke miteinander verbunden,
- Munge ist auf allen VMs eingerichtet 
 - am einfachsten auf einer VM einrichten und die VM anschließend kopieren

Aufsetzen:
- Durch Ausführen des Skripts `setup-slurm.sh` in `slurm-resources` mit Administratorrechten und entsprechend Argumenten wird alles nötige eingerichtet
 - Aufruf: `sudo setup-slurm.sh <controller|compute> <first|> <builtin|backfill|gang|preempt> <controller-ip> <com0-ip> <com1-ip> <com2-ip>`
  - `<controller|compute>`: Kontroll oder Rechenknoten
  - `<first|>`: Angaben bei erstem Durchlauf für das Ergänzen der IP-Adressen mit Hostnames, sonst ""
  - `<builtin|backfill|gang|preempt>`: gewünschtes Scheduling
   -   Ergänzen des Suffix `_pure` nötig, wenn Wasimoff unerwünscht
 - `<controller-ip> <com0-ip> <com1-ip> <com2-ip>`: IP-Adressen der jeweiligen VMs bzw. Knoten
 - Skript muss im Wurzelordner des Repositorys ausgeführt werden

Am Ende müssen nur noch Wasimoff Broker und Client kompiliert werden.
Hierfür wird Go benötigt.
 
## Hybridsystem benutzen
Im Hybridsystem können per `srun` oder `sbatch` Slurm-Jobs in Auftrag gegeben werden.
Als Jobs können die Jobs in `jobs` verwendet werden, jedoch muss dann auch gewährleistet sein, dass sich die Anwendungen auf den VMs in dem im Skript beschriebenen Verzeichnis befinden.
WebAssembly Binaries werden über `client -upload` hochgeladen und können dann für Tasks verwendet werden.
Hierfür muss `client -exec <app> <args>` genutzt werden.
Beispiele für Aufrufe von `client` befinden sich in den Skripten in `testing`.
Sollte die Slurm-Konfiguration geändert werden, ist ein Neustart der Systemd-Services nötig.

## Versuche durchführen
Die Versuche werden über die auto_\*.sh Skripte ausgeführt.
Der Aufruf ist dann: `auto_\*.sh <"preempt"|"">`.
`preempt` muss immer angegeben werden, wenn bei einer Versuchsreihe ein Preemption-Mechanismus genutzt werden soll.
Das Skript darf nicht mitten im Versuch abgebrochen werden, da sonst ein Teil des automatisierten Versuchs im Hintergrund weiterläuft.
Es ist ratsamer per `scancel -u <user>` die Jobs abzubrechen.

## Analysedaten auswerten
Die `.tar.gz`-Archive müssen entpackt werden.
Anschließend muss zuerst `auto_eval.bat` (leider Batch-Skript, die Übersetzung in ein Shell-Skript sollte trivial sein) ausgeführt werden.
`auto_eval.bat` erzeugt pro Versuchsreihe für jeden Knoten eine csv mit der Zeitlinie des Knotens, einen Report des Clusters und einen Aktivitätsgraphen.
Danach können mittels `auto_generate_tables.bat` (es tut mir leid) die Tabellen sowie Grafiken zum Vergleich der in der Masterarbeit beschriebenen Metriken generiert werden.
Die `auto_*`-Skripte sind im Wurzelverzeichnis des Repos auszuführen.