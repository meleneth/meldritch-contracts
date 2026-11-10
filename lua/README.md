# Lua host API

`api.yaml` is the authoritative supported author API. It is JSON-compatible
YAML so validation and generation need only Python's standard library.

The engine implements the API and reports `meldritch.host_api_version()` plus
`meldritch.host_capabilities()`. Applications declare a compatible range and
required capability IDs in an `application.json` validated by
`schemas/application.schema.json`.

Private bootstrap names beginning with `_` are intentionally absent. The
engine-owned prelude may use them, but applications must not.

Run `make generate` at the repository root to reproduce LuaLS annotations in
`types/meldritch.lua`. The generated file is consumer developer support; this
manifest remains authoritative.
