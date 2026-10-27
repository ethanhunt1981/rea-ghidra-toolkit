# Repository-Regeln

## Scope

Dieses Repository enthält ausschließlich generische, wiederverwendbare REA-/Ghidra-Methoden, Werkzeuge und synthetische Tests. Es ist keine Ablage für ein konkretes Reverse-Engineering-Ziel.

Niemals committen:

- Originalbinaries, Installer, Bibliotheken oder Assets eines analysierten Ziels
- Decompilate, Strings oder größere Datenextrakte aus einem konkreten Ziel
- proprietäre, zielspezifische Dateiformat-Spezifikationen oder Nachimplementierungen
- Zugangsdaten, private URLs, Benutzernamen in lokalen Pfaden oder vertrauliche Projektnamen
- Code oder Texte ohne geprüfte Rechte- und Lizenzgrundlage

Verwende für Tests ausschließlich selbst erzeugte Daten. Halte Beispiele neutral und vermeide Rückschlüsse auf ein reales Analyseziel.

## Änderungen

- Bevorzuge kleine, read-only Python-Werkzeuge mit Standardbibliothek.
- Neue Dokumentation in `README.md` und `llms.txt` verlinken; `llms.txt` ist der primäre GitMCP-Einstieg.
- Keine REA-/Ghidra-/JDK-Versionskombination als allgemeingültig behaupten. Versionsspezifische Hinweise mit Datum und Prüfquelle versehen oder besser eine dynamische Prüfung beschreiben.
- Beobachtungen, Heuristiken und verifizierte Aussagen sprachlich klar trennen.
- Keine generierten Ghidra-Projekte oder Decompilierungsausgaben committen.

## Prüfung

Nach Python-Änderungen im Repository-Wurzelverzeichnis ausführen:

```sh
python -m unittest discover -v
python -m compileall -q tools tests
```

Ghidra-Skripte nach Möglichkeit mit der tatsächlich installierten Ghidra-Version kompilieren beziehungsweise als Headless-Skript ausführen. Wenn das in der aktuellen Umgebung nicht möglich ist, diese fehlende Prüfung ausdrücklich benennen.
