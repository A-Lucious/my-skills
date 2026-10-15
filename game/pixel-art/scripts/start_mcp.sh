#!/usr/bin/env bash
# stdout belongs to the MCP protocol. Send diagnostics to stderr only.
set -euo pipefail
PIXEL_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
export PIXEL_PROJECT_ROOT="${PIXEL_PROJECT_ROOT:-$(python3 "$PIXEL_SCRIPT_DIR/project_paths.py")}"
PIXEL_SERVER_ROOT="$PIXEL_PROJECT_ROOT/tools/aseprite-mcp"
PIXEL_PYTHON="$PIXEL_SERVER_ROOT/.venv/bin/python"
if [[ ! -x "$PIXEL_PYTHON" ]]; then
  printf 'Aseprite MCP is not installed. Run scripts/install_mcp.py in the skill.\n' >&2
  exit 1
fi
if [[ -z "${ASEPRITE_PATH:-}" ]]; then
  # ${HOME:-} rather than $HOME: under `set -u` an unset HOME aborts the script
  # before the server ever starts, which is how this looked when the host
  # launched it with an empty environment.
  for PIXEL_CANDIDATE in \
    "${HOME:-}/.local/share/Steam/steamapps/common/Aseprite/aseprite" \
    "${HOME:-}/.steam/steam/steamapps/common/Aseprite/aseprite" \
    "/Applications/Aseprite.app/Contents/MacOS/aseprite" \
    "/usr/bin/aseprite" "/usr/local/bin/aseprite"; do
    if [[ -x "$PIXEL_CANDIDATE" ]]; then
      export ASEPRITE_PATH="$PIXEL_CANDIDATE"
      break
    fi
  done
fi
export ASEPRITE_MCP_WORKSPACE="$PIXEL_PROJECT_ROOT/Test Workspace"
export ASEPRITE_MCP_ALLOW_ABSOLUTE=0
export ASEPRITE_MCP_TRANSPORT=stdio
export ASEPRITE_MCP_TIMEOUT="${ASEPRITE_MCP_TIMEOUT:-120}"
mkdir -p "$ASEPRITE_MCP_WORKSPACE"
cd -- "$PIXEL_SERVER_ROOT"
exec "$PIXEL_PYTHON" -m aseprite_mcp
