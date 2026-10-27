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

## Official MCP Registry listing

The toolkit is registered in the official [MCP Registry](https://registry.modelcontextprotocol.io) as
`io.github.ethanhunt1981/rea-ghidra-toolkit` version `1.0.0`, status `active`.

- Metadata lives in [`server.json`](../server.json) at the repository root.
- Remote transport: `streamable-http` at `https://gitmcp.io/ethanhunt1981/rea-ghidra-toolkit/mcp`.
  (A live probe confirmed that `/mcp` serves the MCP handshake, while the legacy `/sse` path returns HTTP 405 — hence only streamable HTTP is registered.)
- To publish an updated version: bump `version` in `server.json`, then run `mcp-publisher login github` and `mcp-publisher publish` from the repository root.
- Several MCP server directories (for example Glama and mcp.directory) import registry entries; PulseMCP has paused direct submissions and points publishers to the registry.

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
