# Delphi-PE32: VMTs und RTTI sicher untersuchen

Diese Hinweise betreffen klassische 32-bit-Delphi-Muster. Compilerversion, Linker, Packung und Sprachvarianten können Abweichungen erzeugen. Jede Layout-Annahme muss am konkreten Ziel bestätigt werden.

## RVA und VA unterscheiden

Bei statischen PE-Werkzeugen werden drei Adressarten benötigt:

- **File Offset:** Position in der Datei.
- **RVA:** relativ zum Image Base im geladenen Image.
- **VA:** virtuelle Adresse, bei PE32 typischerweise `Image Base + RVA`.

Eine Sektion beschreibt, welche Dateibytes auf welche RVAs abgebildet werden. Nicht jeder virtuelle Bereich besitzt Dateibytes; zero-filled Bereiche lassen sich nicht aus der Datei lesen.

Der mitgelieferte Parser kapselt diese Übersetzung:

```python
from tools.pe32 import PE32

pe = PE32.from_path("program.exe")
rva = 0x1234
offset = pe.rva_to_offset(rva)
value = pe.u32_va(pe.image_base + rva)
```

## Häufiges klassisches VMT-Layout

Bei vielen 32-bit-Delphi-Versionen liegt vor dem positiven Methodentabellenbereich Metadaten. Häufig anzutreffen sind:

| Relativ zum VMT-Start | Typische Bedeutung |
|---|---|
| `-44` | Zeiger auf den Klassennamen als ShortString |
| `-40` | Instanzgröße als 32-bit-Wert |
| `0` | Beginn des positiven Methoden-/Virtual-Method-Bereichs |

Ein ShortString beginnt typischerweise mit einem Längenbyte, gefolgt von den Zeichen ohne zwingendes Nullbyte am Ende.

Diese Offsets sind **keine universelle Spezifikation**. Sie sind eine überprüfbare Hypothese, die durch Code-Referenzen, Methodenzeiger und Objektverwendung gestützt werden muss.

## Einen bekannten Kandidaten prüfen

```powershell
python -m tools.delphi_vmt "C:\analyse\programm.exe" --vmt 0x00412340
```

Das Werkzeug prüft unter anderem:

- Ist der Namenszeiger auf file-backed Bytes abbildbar?
- Ist die ShortString-Länge plausibel?
- Besteht der Name aus printable ASCII?
- Ist die Instanzgröße innerhalb einer defensiven Obergrenze?
- Liegt der erste Methodenzeiger in einer ausführbaren Sektion?

Auch eine erfolgreiche Ausgabe enthält `"verified": false`. Das ist absichtlich so: Strukturelle Plausibilität ersetzt keine Disassemblerprüfung.

## Heuristisch suchen

```powershell
python -m tools.delphi_vmt "C:\analyse\programm.exe" --scan
```

Standardmäßig werden nur Kandidaten ausgegeben, deren erster Methodenzeiger in eine executable Section zeigt. Weitere, schwächere Kandidaten:

```powershell
python -m tools.delphi_vmt "C:\analyse\programm.exe" --scan --include-unverified
```

Die Suche ist auf Geschwindigkeit und einfache Prüfbarkeit ausgelegt, nicht auf Vollständigkeit. Sie kann falsche Treffer liefern und ungewöhnliche Layouts übersehen.

## Kandidat im Disassembler bestätigen

1. Negative Metadaten und positiven Methodenbereich gemeinsam betrachten.
2. Mehrere Methodenzeiger auf tatsächliche Funktionsanfänge prüfen.
3. Referenzen auf die Tabelle suchen.
4. Objektallokation und Instanzgröße mit beobachteten Zugriffen vergleichen.
5. Klassenname, Hierarchie und Methodenverhalten erst danach benennen.

Bei vielen Delphi-Objekten steht im ersten Feld ein VMT-Zeiger. Daraus folgt nicht, dass jeder erste 32-bit-Wert einer beliebigen Struktur eine VMT ist.

## Häufige Fehlinterpretationen

- **Printable String allein genügt nicht.** Zufällige Bytes können die Heuristik bestehen.
- **Codeähnliche Bytes sind keine Funktion.** Entry-Adresse und Referenzen prüfen.
- **Ein Feldoffset ist noch kein Typ.** Zugriffsbreite und Verwendung auswerten.
- **Imports und Strings liefern Einstiege, kein vollständiges Verhalten.**
- **Packer verändern die Ausgangslage.** File-backed statische Strukturen können fehlen; keine VMT-Behauptung aus einer leeren Suche ableiten.
- **ASLR ändert Laufzeitadressen.** Für Dokumentation RVA plus Ziel-Hash zusätzlich zur statischen VA speichern.

## Sinnvolle nächste Belege

- unabhängige Xrefs auf dieselbe VMT
- konsistente Methodenaufrufe über dieselben Tabellenoffsets
- Allokationsgröße und Feldzugriffe passend zur Instanzgröße
- mehrere Klassen mit konsistentem Layout
- RTTI-Referenzen, deren eigene Struktur ebenfalls validiert wurde

Erst diese Kombination macht aus einem Kandidaten eine belastbare Klassen- oder Methodenrekonstruktion.
