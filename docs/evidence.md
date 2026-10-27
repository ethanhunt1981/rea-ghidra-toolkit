# Evidenz, Protokoll und Übergabe

Eine Reverse-Engineering-Analyse ist erst dann wiederverwendbar, wenn erkennbar bleibt, was direkt beobachtet und was abgeleitet wurde.

## Aussagearten klar trennen

| Art | Bedeutung | Beispiel |
|---|---|---|
| Beobachtung | Direkt aus Dateibytes, Werkzeugausgabe oder dokumentiertem Runtime-Schritt belegt | „Der Pseudocode der Funktion X zeigt einen Call zum importierten Symbol Y.“ |
| Inferenz | Mit Beobachtungen begründet, aber nicht eindeutig bewiesen | „Zugriffsbreite und arithmetische Verwendungen passen zu einem 32-bit-Zähler.“ |
| Unbekannt | Im untersuchten Scope nicht entschieden | „Die Suche umfasste die Sectionen A und B; über C liegt kein Befund vor.“ |

Vermeide Ausdrücke wie „die App macht X“, wenn die Aussage nur aus statischer Analyse kommt. Präzise ist zum Beispiel „der decompilierte Pfad verarbeitet Y“.

## Einträge im privaten Analyseprotokoll

Halte jeden Befund in derselben Struktur fest:

| Feld | Inhalt |
|---|---|
| `ID` | Stabile Referenz, zum Beispiel `F001` |
| `Ziel` | Dateiname, SHA-256 und Version |
| `Adresse` | Entry-Adresse sowie RVA/Image Base bei VA |
| `Frage` | Zu prüfende Frage |
| `Beobachtung` | Direkt nachprüfbare Werkzeug- oder Bytebeobachtung |
| `Schlussfolgerung` | Aus Beobachtungen abgelegte, nicht bewiesene Ausage |
| `Name/Hypothese` | Möglicher Funktionsname, Typ, Offset oder VMT-Bedeutung |
| `Status` | `confirmed`, `plausible` oder `unresolved` |
| `Evidence` | REA-Evidence-ID oder privater Exportpfad |
| `Nachprüfung` | Welche unabhängige Prüfung steht aus oder wurde erledigt |
| `Suchgrenze` | Welche Bereiche ausdrücklich nicht untersucht wurden |

## Negative Ergebnisse verwenden

Ein „kein Treffer“ ist wertvoll, wenn der Suchraum sichtbar ist:

- untersuchte Sektionen, Dateien oder Funktionen
- verwendete Suchmuster und Groß-/Kleinschreibung
- geprüfte Referenzen oder Entry-Points
- Grenzen durch Packung, Dateityp oder verschlüsselte Abschnitte

Ohne diese Grenze darfst du nicht schreiben, etwas existiere grundsätzlich nicht; nur, dass es im beobachtbaren Scope nicht fundiert wurde.

## Namen fortlaufend verwenden

Ein verifizierter Funktionsname ist wertvoll, weil spätere Referenzen sofort lesbar werden. Wenn eine Hypothese sich widerlegt, benenne die Änderung mit Datum und Grund im Eintrag, damit keine alte Annahme still weiterlebt.

## Übergabe an die nächste Sitzung

Am Ende einer Sitzung gehört in die private `handover.md` zum Beispiel:

```text
## Status
- F002 confirmed: VMT-Hypothese, Xrefs bestätigt.
- F003 unresolved: Feld bei Offset 0x10 unbekannt.

## Nächste Schritte
- Objektverwendung der Klasse X verfolgen.
- Schreibzugriffe auf das Feld bei Offset 0x10 prüfen.
```

Vorlagen stehen in [`templates/analysis-log.md`](../templates/analysis-log.md) und [`templates/handover.md`](../templates/handover.md).
