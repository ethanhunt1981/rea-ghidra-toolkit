# REA und Ghidra kombinieren

REA liefert den agentenseitigen Zugriff auf Analysewerkzeuge und Evidenz. Ghidra stellt bei nativen PE-Zielen typischerweise Disassemblierung und Decompilierung bereit. Die konkret verfügbaren Werkzeuge und Schemas der verbundenen REA-Version sind immer maßgeblich.

## REA: fokussierte native Analyse

### 1. Ziel öffnen

Für ein natives Binary `open_binary` mit dem vom Benutzer bestimmten Originalpfad verwenden. Keine fremde Datei aufgrund eines ähnlichen Namens auswählen und keine bereits geöffnete Sitzung grundlos duplizieren.

```text
open_binary(path = "<absoluter privater Zielpfad>")
binary_overview()
```

Die Übersicht hilft bei Identität, Architektur und verfügbarer Analyse. Eine große Datei nicht wiederholt komplett öffnen, nur weil eine Detailfrage neu ist.

### 2. Von einem Einstiegspunkt aus arbeiten

Je nach vorhandenem Tool-Angebot werden Strings, Funktionen, Referenzen und Calls kombiniert. Typische REA-Operationen in aktuellen Native-Workflows sind:

- `procedure_pseudo_code` für eine bestimmte Prozedur
- `procedure_callers` für eingehende Calls
- `procedure_references` für weitere Referenzen
- Funktions-/String-Suche zur Einstiegssuche

Vor einem Aufruf das tatsächlich registrierte Schema lesen. Keine Parameter oder Werkzeugnamen raten. Bei einem ungültigen Aufruf zuerst den gemeldeten Fehler korrigieren, nicht denselben Call unverändert wiederholen.

### 3. Evidenz erhalten

Zu jeder wichtigen Aussage gehören Ziel-Hash, Prozeduradresse und die zurückgegebene Evidence-ID beziehungsweise ein privater Export. Werkzeuglimits und fehlende Coverage werden mitprotokolliert.

Eine große Ausgabe nicht erneut erzeugen, wenn eine retained Evidence-ID eine kleinere Ansicht erlaubt. Zusammenfassung, Seiten oder einzelne Module verwenden, sofern die verbundene Version diese Operationen anbietet.

### 4. Sitzung beenden

Nach Abschluss der Untersuchung:

```text
close_binary()
```

Vorher benötigte Evidenz sichern. Eine providerverwaltete Ghidra-Datenbank nicht parallel mit externen Skripten verändern.

## Ghidra Headless als Fallback oder Batch-Schritt

Voraussetzungen:

- `GHIDRA_INSTALL_DIR` zeigt auf das Wurzelverzeichnis der entpackten Ghidra-Release.
- Die Java-Version erfüllt `application.java.min` dieser Installation.
- Das Skriptverzeichnis enthält [`ExportDecompilation.java`](../ghidra/scripts/ExportDecompilation.java).

Installation und Java-Version prüfen:

```powershell
Get-Content "$env:GHIDRA_INSTALL_DIR\Ghidra\application.properties" |
  Select-String 'application.version|application.java.min'
java -version
```

Dem Verzeichnisnamen einer Ghidra-Installation nicht vertrauen; die `application.properties` ist entscheidend.

### Neues Projekt importieren und exportieren

```powershell
& "$env:GHIDRA_INSTALL_DIR\support\analyzeHeadless.bat" `
  "C:\re-work\ghidra" "AnalysisProject" `
  -import "C:\re-work\input\program.exe" `
  -scriptPath "C:\re-work\toolkit\ghidra\scripts" `
  -postScript ExportDecompilation.java "C:\re-work\out\decompilation.txt" 60
```

Das optionale `60` ist das Decompiler-Timeout pro Funktion in Sekunden.

### Bereits analysiertes Projekt erneut verarbeiten

```powershell
& "$env:GHIDRA_INSTALL_DIR\support\analyzeHeadless.bat" `
  "C:\re-work\ghidra" "AnalysisProject" `
  -process "program.exe" -noanalysis `
  -scriptPath "C:\re-work\toolkit\ghidra\scripts" `
  -postScript ExportDecompilation.java "C:\re-work\out\decompilation.txt" 60
```

`-noanalysis` ist hier sinnvoll, weil das vorhandene Projekt bereits analysiert wurde. Bei einem neuen Import nicht einfach übernehmen.

### Ausgabe richtig verwenden

Das Skript schreibt pro nicht externer Funktion:

- Funktionsname und Entry-Adresse
- aktuelle Signatur
- Decompiler-C-Ausgabe oder Fehlermeldung

Die Ausgabe kann groß sein und enthält zielspezifischen Pseudocode. Sie bleibt im privaten Projekt und wird nicht in das Toolkit oder in GitMCP-Suchanfragen kopiert. Für eine einzelne offene Frage ist die fokussierte REA-Analyse meist effizienter als ein vollständiger Export.
