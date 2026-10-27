# Troubleshooting: REA, Ghidra und PE-Analyse

Fehler besser eingrenzen als wiederholen. Prüfe zuerst die gemeldete Ursache und das tatsächlich verwendete Setup. Wenn ein Aufruf scheitert, korrigiere zuerst die Parameter, das Ziel oder die Version; Wiederholfehler sind fast immer ein Hinweis auf ein systemisches Problem, nicht eine Ratenfrage.

## Ghidra-Installation und Version

### Version korrekt prüfen

Vertraue nicht dem Verzeichnisnamen. Die Installation wird über die `application.properties` geprüft:

```powershell
Get-Content "$env:GHIDRA_INSTALL_DIR\Ghidra\application.properties" |
  Select-String 'application.version|application.java.min'
```

- Fehlt die Datei, zeigt `GHIDRA_INSTALL_DIR` in der Regel auf das falsche Verzeichnis.
- Erfüllt die Java-Version `application.java.min` nicht, ist zuerst die geforderte Java-Version bereitzustellen.
- Ein Ghidra-Update kann die minimale Java-Version ändern. Lies daher die Properties der tatsächlich verwendeten Installation.

### Falsches Installationsverzeichnis

`GHIDRA_INSTALL_DIR` muss auf die Ghidra-Wurzel zeigen, also das Verzeichnis, in dem `Ghidra` und `support` liegen. Danach die Provider-Session oder Verbindungsprüfung neu starten.

### Keine allgemeingültige Versionsmatrix annehmen

Welche Ghidra-Version eine REA-Installation akzeptiert, hängt von der installierten REA-Distribution ab. Prüfe daher die Policy oder Dokumentation der tatsächlich verwendeten Version, statt Versionsregeln aus einem anderen Kontext zu übernehmen. Versionsspezifische Hinweise im Repo nur mit Datum und Quelle hinterlegen.

## REA-Probleme

### Provider-Session endet unerwartet

Wenn eine Provider-Session abbricht, kann eine alte Prozessinstanz oder ein ungültiger Zustand übrig bleiben. Vorgehen:

1. Zuerst die gemeldete Ursache lesen.
2. Nur den relevanten alten Analyseprozess beenden, nicht pauschal alle Java-Prozesse.
3. Dasselbe Ziel erneut mit `open_binary` öffnen.
4. Wichtige Evidence vor größeren Änderungen exportieren, weil sessionbezogene Annotationen verloren gehen können.
5. Nach Abschluss sauber mit `close_binary` schließen.

### Unbekannter oder falscher Toolname

- Lese zuerst die tatsächlich registrierten Werkzeuge und ihre Schemas.
- Verwende genau die bereitgestellten Namen und Parameter, nicht vermutete Varianten.
- Ein Präfix wie `tools.` ist je nach Harness-Integration Teil des Namens oder nicht; die konkrete Laufzeit entscheidet.

### Timeout oder zu große Antwort

Bei langen Analysen oder umfangreichen Antworten den Call nicht einfach wiederholen:

- bereitgestellte Summary- oder Detailparameter nutzen
- eine zurückgegebene Evidence-ID für eine kleinere Ansicht verwenden
- die Frage auf eine Funktion, ein Modul oder einen Bereich begrenzen
- bei Bedarf eine vollständige Analyse einmalig exportieren

Kläre zuerst, ob ein Abbruch lokal im Client oder im Server passiert ist. Wiederhole nur dann, wenn bekannt ist, dass die Analyse wirklich nicht abgeschlossen wurde.

## Ghidra Headless

### Programm nicht gefunden

`-process` bezieht sich auf ein Programm innerhalb des angegebenen Ghidra-Projekts. Für ein neues Ziel nutze `-import`; danach kann die Analyse in späteren Headless-Läufen mit `-process` wiederverwendet werden. Kombiniere nicht schematisch beide Wege.

### Skript nicht gefunden

`-scriptPath` muss das Verzeichnis mit `ExportDecompilation.java` enthalten. Im `-postScript` wird der Skriptname angegeben, gefolgt von den Argumenten. Nach dem Skriptname folgt der Ausgabepfad und optional das Timeout.

### Java-Fehler

Prüfe zuerst `application.java.min` und die tatsächlich verwendete `java -version`. Nach einer Java-Installation zuerst die Umgebungsvariablen und anschließend den Headless-Aufruf neu prüfen.

## PE-Analyseprobleme

### Eingabe wird nicht als PE32 akzeptiert

- Prüfe zuerst Dateigröße und Hash. Downloads können früh unterbrochen worden sein.
- Stelle sicher, dass es sich um einen 32-bit-PE-Optional-Header mit Magic `0x10b` handelt. 64-bit-PE-Dateien werden vom vorhandenen Parser bewusst abgelehnt.
- Ein `MZ`-Beginn allein macht noch keine PE-Struktur gültig.

### Imports fehlen oder werden übersehen

- Verzweigungen wie Bound-Imports, Ordinal-Imports oder gepackte Abschnitte können die übliche Importtabelle anders darstellen.
- Dieses Werkzeug liest nur die Directory-Tabelle und Standard-Thunks. Spezialformen ersetzt der vorhandene Parser nicht.
- Bei einem Installationspaket zuerst die Bestandteile und nicht nur das große Paket prüfen.

### VMT-Scan liefert nichts

Mögliche Ursachen:

- Der Compiler nutzt ein anderes VMT-/RTTI-Layout.
- Packer oder verschlüsselte Abschnitte verhindern einfache Datei-Prüfungen.
- Es gibt schlicht keine solchen Kandidaten im betrachteten Bereich.

Daher ist „kein Scanresultat“ kein Beweis gegen das Vorhandensein von Klasseninformationen. Es bleibt eine begrenzte Beobachtung innerhalb des untersuchten Scopes.
