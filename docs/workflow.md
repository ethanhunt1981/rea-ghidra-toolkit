# Evidenzorientierter Analyseworkflow

Dieser Workflow ist für autorisierte statische Analyse gedacht. Das konkrete Ziel und alle daraus abgeleiteten Daten bleiben im privaten Projekt.

## 1. Fragestellung und Grenzen festlegen

Formuliere zunächst überprüfbare Fragen, zum Beispiel:

- Welche Funktion liest einen bestimmten Dateityp?
- Welche Klasse besitzt ein beobachtetes Verhalten?
- Welche Datenstruktur wird an einer Funktion verwendet?
- Ist eine Vermutung durch statische Belege bestätigt oder nur plausibel?

Lege fest, ob ausschließlich statische Analyse erlaubt ist. Eine Datei zu öffnen, Strings zu extrahieren oder sie zu decompilieren bedeutet nicht, sie auszuführen. Runtime-Schritte sind ein separater Scope.

## 2. Privates Arbeitsverzeichnis und Artefaktidentität

Eine einfache private Struktur genügt:

```text
analysis/
  notes/
  evidence/
  exports/
tools/
handover.md
```

Sichere vor der Analyse mindestens:

- eindeutiger Dateiname und Herkunft innerhalb des privaten Projekts
- Dateigröße und SHA-256
- Dateityp und gegebenenfalls Architektur
- Datum und verwendete Werkzeugversionen

Für PE32-Dateien:

```powershell
python -m tools.pe_inventory "C:\analyse\programm.exe" --imports --json
```

Die Ausgabe gehört in das **private** Projekt, nicht in dieses Toolkit.

## 3. Kleinste nützliche Übersicht erzeugen

Nicht sofort jede Funktion vollständig decompilieren. Beginne mit:

1. PE-/Archiv-Inventar und vorhandenen Metadaten
2. Sektionen, Imports, Ressourcen und Entry Points
3. vorhandener REA-Sitzung oder Ghidra-Projekt statt Duplikat
4. Strings und Referenzen als Einstiegspunkte, nicht als Verhaltensbeweis

Bei einem Installer oder Archiv muss zunächst das tatsächlich relevante Mitglied identifiziert werden. Ein Installer ist nicht automatisch das zu decompilierende Programm.

## 4. Von der Frage zur Funktion

Für jede Frage wird ein konkreter Einstieg gesucht:

- Import oder API-Aufruf
- String und dessen Code-Referenzen
- Ressource oder Dateizugriff
- Funktionsadresse aus einer früheren Beobachtung
- VMT-/RTTI-Kandidat bei Delphi

Danach werden gezielt Pseudocode, Calls, Caller und Referenzen geprüft. Erweitere die Analyse nur, wenn eine offene Frage dazu Anlass gibt.

## 5. Funktionen und Strukturen schrittweise rekonstruieren

Pro untersuchter Funktion im privaten Protokoll festhalten:

- SHA-256 des Ziels und Entry-Adresse
- ursprünglicher und später vergebener Funktionsname
- Signatur und deren Sicherheit
- beobachtete Calls und relevante Referenzen
- verwendete Konstanten, Offsets und String-/Datenreferenzen
- Evidence-ID oder Exportpfad
- offene Fragen

Benenne eine Funktion nicht allein nach einem String oder einem plausiblen Codefragment. Ein Name wie `load_data` ist eine Hypothese, bis Aufrufkontext und Datenfluss ihn stützen.

Bei Datenstrukturen zunächst nur bestätigte Felder eintragen. Feldgröße und Typ ergeben sich aus Zugriffsbreite, Vorzeichenverwendung, Zeigerarithmetik und mehreren unabhängigen Verwendungsstellen.

## 6. VMT- und RTTI-Hinweise validieren

Bei klassischem 32-bit-Delphi kann [`delphi_vmt.py`](../tools/delphi_vmt.py) Kandidaten liefern. Jeder Treffer bleibt zunächst unbestätigt. Prüfe im Disassembler insbesondere:

- Ist die Adresse wirklich der Beginn einer Methodentabelle?
- Zeigt der Namenszeiger auf einen plausiblen ShortString?
- Passen Instanzgröße und beobachtete Speicherzugriffe zusammen?
- Verweisen Methodeneinträge auf tatsächlichen Code?
- Gibt es konsistente Referenzen auf dieselbe Tabelle?

Details stehen in [`delphi-pe32.md`](delphi-pe32.md).

## 7. Verifikation statt Plausibilität

Verwende drei getrennte Aussagearten:

- **Beobachtung:** direkt aus Artefakt oder Werkzeugausgabe belegt.
- **Inferenz:** aus Beobachtungen abgeleitet, aber nicht eindeutig bewiesen.
- **Unbekannt:** mit dem bisherigen Scope nicht entschieden.

Eine statische Analyse beweist kein tatsächlich ausgeführtes Verhalten. Umgekehrt beweist ein einzelner Lauf nicht alle Pfade. Negative Suchen immer mit Suchraum angeben: „kein Treffer in den untersuchten Funktionen“ statt „existiert nicht“.

## 8. Reproduzierbar prüfen

Geeignete Prüfungen sind:

- dieselbe Funktion nach erneuter Analyse erneut vergleichen
- eine zweite unabhängige Referenz oder einen zweiten Aufrufkontext heranziehen
- Adress- und Offsetberechnungen mit einem kleinen Skript wiederholen
- Parserhypothesen mit selbst erzeugten Daten testen
- erwartete Fehlerfälle und Grenzfälle prüfen

Ein eigener Parser darf nicht allein mit denselben Annahmen verifiziert werden, aus denen er entstanden ist. Suche mindestens einen unabhängigen Beleg am Ziel.

## 9. Sauber abschließen

- Analysefragen als beantwortet, teilweise beantwortet oder offen markieren.
- Relevante Evidenz exportieren und private Handover-Datei aktualisieren.
- Geöffnete REA-Binärsitzung mit `close_binary` schließen.
- Keine providerverwaltete Ghidra-Datenbank extern verändern.
- Nur allgemeine, bereinigte und rechtlich unbedenkliche Erkenntnisse ins öffentliche Toolkit übernehmen.

Für die Übergabe [`templates/handover.md`](../templates/handover.md) verwenden.
