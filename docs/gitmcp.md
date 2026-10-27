# Toolkit as a GitMCP knowledge source

This repository is arranged so that an agent can consume it through the Model Context Protocol without cloning it. The repository-specific endpoint is:

```text
https://gitmcp.io/ethanhunt1981/rea-ghidra-toolkit
```

The repository-specific endpoint is preferable to the generic `https://gitmcp.io/docs`, because it keeps the lesson target clear.

## OpenCode

OpenCode manages MCP servers under `mcp.servers`. For this toolkit in every project:

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

Alternatively, use the OpenCode CLI:

```sh
opencode mcp add rea-ghidra-toolkit --global --url https://gitmcp.io/ethanhunt1981/rea-ghidra-toolkit
opencode mcp list
```

OpenCode watches configuration changes and reloads automatically. You do not need to restart it for a config change.

## GitMCP prioritizes `llms.txt`

GitMCP reads `llms.txt` first. Keep that file short and curated. Point it to the most useful docs and tools instead of duplicating their text.

## Privacy notes

The server is public. Treat it accordingly:

- use broad, generic queries, not target-specific strings, paths, or secrets;
- never send decompiled target content, credentials, or private project details to GitMCP;
- target-specific results stay in the private analysis project; this toolkit contains only generic methodology.

## How an agent should use the toolkit

Broad prompts work better than narrow ones:

```text
Use the MCP server rea-ghidra-toolkit. First look at the workflow for
REA/Ghidra and Delphi VMT guidance before you invent new tools.
```

```text
Ask the GitMCP server rea-ghidra-toolkit for evidence-oriented PE32 / VMT
methods and Ghidra headless workflows in the context of my analysis.
```

An agent should then split its work: public methodology from this toolkit, concrete target data from the private working directory.
