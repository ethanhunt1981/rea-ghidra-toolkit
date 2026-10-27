# Toolkit als GitMCP-Wissensquelle

Dieses Repository ist so aufgebaut, dass ein Agent es ohne Klonen über das Model Context Protocol abrufen kann. Der zugehörige repo-spezifische Endpunkt ist:

```text
https://gitmcp.io/ethanhunt1981/rea-ghidra-toolkit
```

Der repo-spezifische Endpunkt ist sinnvoller als der generische `https://gitmcp.io/docs`, weil klar bleibt, dass nur dieses Toolkit gelesen wird.

## OpenCode

OpenCode verwaltet MCP-Server unter `mcp.servers`. Für dieses Toolkit in allen Projekten gilt:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "rea-ghidra-toolkit": {
        "type": "remote",
        "url": "https://gitmcp.io/ethanhunt1981/rea-ghidra-toolkit"
      }
    }
  }
}
```

Alternativ lässt es sich mit der OpenCode-CLI hinzufügen:

```sh
opencode mcp add rea-ghidra-toolkit --global --url https://gitmcp.io/ethanhunt1981/rea-ghidra-toolkit
opencode mcp list
```

OpenCode beobachtet Konfigurationsdateien und lädt Änderungen automatisch. Ein Neustart ist dafür nicht nötig. Der aktuelle Status kann über `opencode mcp list` oder die Oberfläche `/mcps` geprüft werden.

## GitMCP liest vorzugsweise `llms.txt`

GitMCP unterstützt prioritär `llms.txt`. Diese Datei ist deshalb der kuratierte Einstieg für Agenten. Halte sie knapp und konkret, nicht als vollständige Kopie der Werkzeugbeschreibungen.

## Datenschutzhinweise

Der Server ist öffentlich. Deshalb gilt:

- Suche immer mit allgemeingültigen Begriffen, nicht mit namensgebenden Zielspezifischen Strings, Pfaden oder Geheimnissen.
- Sende niemals decompilierte Zielinhalte, Zugangsdaten oder private Projektinhalte an GitMCP.
- Zielspezifische Ergebnisse bleiben im privaten Analyseprojekt; dieses Toolkit enthält nur generische Methodik.

## So nutzt ein Agent das Toolkit

Erfolgreiche Prompts sind eher breit als zu spezifisch:

```text
Nutze den MCP-Server rea-ghidra-toolkit. Suche zuerst im Workflow nach REA/Ghidra
und nach Delphi-VMT-Methoden, bevor du neue Werkzeuge entwirfst.
```

```text
Frage den GitMCP-Server rea-ghidra-toolkit nach evidenzorientierten PE32-/VMT-
Methoden und nach Ghidra-Headless-Workflows im Kontext meiner Analyse.
```

Der Agent wechselt dann zwischen öffentlichem Methodik-Wissen und privatem Arbeitsverzeichnis des konkreten Ziels.
