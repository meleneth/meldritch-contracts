#!/usr/bin/env bash
set -euo pipefail

readonly contracts_repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
readonly workspace_dir="$(dirname -- "$contracts_repo")"

readonly engine_repo="${MELDRITCH_ENGINE_REPO:-$workspace_dir/meldritch}"
readonly lua_repo="${MELDRITCH_LUA_REPO:-$workspace_dir/meldritch-lua}"
readonly ui_repo="${MELDRITCH_UI_REPO:-$workspace_dir/meldritch-ui}"

require_checkout() {
  local name="$1"
  local directory="$2"
  if [[ ! -d "$directory/.git" ]]; then
    printf 'error: %s is not a Git checkout: %s\n' "$name" "$directory" >&2
    exit 2
  fi
}

require_checkout meldritch "$engine_repo"
require_checkout meldritch-lua "$lua_repo"
require_checkout meldritch-ui "$ui_repo"

integration() {
  python3 "$contracts_repo/tools/integrate.py" "$@" \
    --engine "$engine_repo" \
    --lua "$lua_repo" \
    --ui "$ui_repo"
}
