# REA + Ghidra Toolkit

Wiederverwendbare Workflows und kleine Werkzeuge für die **autorisierte statische Analyse** nativer Programme mit [REA](https://github.com/morluto/rea) und [Ghidra](https://github.com/NationalSecurityAgency/ghidra). Das Repository ist als Wissensquelle für GitMCP aufgebaut.

## Zweck und Abgrenzung

Dieses Repository beantwortet vor allem:

- Wie beginne ich eine nachvollziehbare PE-/Delphi-Analyse?
- Wie kombiniere ich REA, Ghidra und eigene Skripte, ohne Schlussfolgerungen als Fakten zu behandeln?
- Wie exportiere und dokumentiere ich Ergebnisse so, dass eine spätere Sitzung darauf aufbauen kann?
- Welche typischen Setup- und Analysefehler kann ich vermeiden?

**Nicht hierhin gehören** Originalbinaries, Installationspakete, Decompilate, proprietäre Formatspezifikationen, projektspezifische Nachimplementierungen, Zugangsdaten oder private Pfade. Solche Inhalte bleiben im jeweiligen privaten Analyseprojekt.

## Für Agenten: Einstieg über GitMCP

Repo-spezifischer MCP-Endpunkt:

```text
https://gitmcp.io/ethanhunt1981/rea-ghidra-toolkit
```

Beispielprompt in einem privaten Analyseprojekt:

```text
Nutze für diese autorisierte Analyse zuerst den GitMCP-Server
rea-ghidra-toolkit. Lies den Workflow und suche passende REA-/Ghidra- und
Delphi-Hinweise, bevor du neue Werkzeuge entwickelst. Übernimm nur generische
Methoden; speichere alle zielspezifischen Ergebnisse ausschließlich lokal im
privaten Projekt.
```

GitMCP liest bevorzugt [`llms.txt`](llms.txt). Diese Datei ist deshalb der kuratierte Einstieg für Agenten. Die Einrichtung in OpenCode steht in [`docs/gitmcp.md`](docs/gitmcp.md).

## Inhalt

| Pfad | Verwendung |
|---|---|
| [`docs/workflow.md`](docs/workflow.md) | Vollständiger, evidenzorientierter Analyseworkflow |
| [`docs/rea-ghidra.md`](docs/rea-ghidra.md) | REA-Werkzeugfolge und Ghidra-Headless-Fallback |
| [`docs/delphi-pe32.md`](docs/delphi-pe32.md) | PE32-, Delphi-VMT- und RTTI-Hinweise |
| [`docs/evidence.md`](docs/evidence.md) | Beobachtungen, Hypothesen und Unbekannte sauber trennen |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Setup-, Provider- und Analysefehler eingrenzen |
| [`docs/gitmcp.md`](docs/gitmcp.md) | Toolkit als dauerhafte MCP-Wissensquelle verwenden |
| [`ghidra/scripts/ExportDecompilation.java`](ghidra/scripts/ExportDecompilation.java) | Nicht externe Funktionen in eine UTF-8-Datei decompilieren |
| [`tools/pe_inventory.py`](tools/pe_inventory.py) | PE32-Hash, Header, Sektionen und optionale Imports ausgeben |
| [`tools/pe32.py`](tools/pe32.py) | Read-only Kernel: RVA-/VA-Umrechnung und PE32-Grunddaten |
| [`tools/delphi_vmt.py`](tools/delphi_vmt.py) | Klassische 32-bit-Delphi-VMTs prüfen oder heuristisch suchen |
| [`templates/analysis-log.md`](templates/analysis-log.md) | Vorlage für das private Analyseprotokoll |
| [`templates/handover.md`](templates/handover.md) | Vorlage für eine spätere Sitzung oder Übergabe |

## Lokale Werkzeuge

Voraussetzung: Python 3.10 oder neuer. Die Python-Werkzeuge verwenden nur die Standardbibliothek und führen die untersuchte Datei **nicht** aus.

```powershell
# Im Wurzelverzeichnis dieses Repositories
python -m tools.pe_inventory "C:\analyse\programm.exe"
python -m tools.pe_inventory "C:\analyse\programm.exe" --imports --json

# Einen bereits bekannten VMT-Kandidaten an seiner virtuellen Adresse prüfen
python -m tools.delphi_vmt "C:\analyse\programm.exe" --vmt 0x00412340

# Heuristisch nach Kandidaten suchen; Ergebnisse immer im Disassembler prüfen
python -m tools.delphi_vmt "C:\analyse\programm.exe" --scan
```

Die Werkzeuge sind bewusst klein und read-only. Sie ersetzen weder Ghidra noch eine Validierung am konkreten Compiler-/Binary-Muster.

## Tests

Alle Tests erzeugen ihre PE-Daten synthetisch und benötigen keine Drittanbieterdateien:

```powershell
python -m unittest discover -v
```

## Grundprinzip

**Erst Identität und Beobachtungen sichern, dann gezielt decompilieren, danach Hypothesen verifizieren.** Ein plausibler Funktionsname, String oder VMT-Kandidat ist noch kein Verhaltensbeweis. Die Vorlagen helfen, diesen Unterschied auch über Sitzungsgrenzen hinweg sichtbar zu halten.

## Lizenz

Das Repository steht unter der [MIT-Lizenz](LICENSE). Damit ist die Nutzung der enthaltenen Methodik und Werkzeuge erlaubt. Die Lizenz ist keine Freigabe von Originalbinaries, decompilierten Zielspezifikationen, fremd geschütztem Material oder privat gespeicherten Analyseergebnissen.

