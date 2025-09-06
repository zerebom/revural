#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME=${CODEX_HOME:-"$HOME/.codex"}
CFG_SRC=".codex/config.example.toml"
CFG_DST="$CODEX_HOME/config.toml"

echo "[codex] Using CODEX_HOME=$CODEX_HOME"
mkdir -p "$CODEX_HOME"

if [ ! -f "$CFG_DST" ]; then
  echo "[codex] Installing example config -> $CFG_DST"
  cp "$CFG_SRC" "$CFG_DST"
else
  echo "[codex] Backing up existing config -> $CFG_DST.bak"
  cp "$CFG_DST" "$CFG_DST.bak"
  echo "[codex] Merging base (append if keys absent)"
  # Simplest approach: keep user config, do not overwrite. User can diff with .bak
fi

# Inject trust entry for this repository path
REPO_ROOT=$(git rev-parse --show-toplevel)
ESCAPED_PATH=${REPO_ROOT//\//\/}

if ! grep -q "\[projects.\"$REPO_ROOT\"\]" "$CFG_DST"; then
  {
    echo ""
    echo "[projects.\"$REPO_ROOT\"]"
    echo "trust_level = \"trusted\""
  } >> "$CFG_DST"
  echo "[codex] Marked project as trusted: $REPO_ROOT"
else
  echo "[codex] Project already trusted in config"
fi

echo "[codex] Done. You can run with a profile, e.g.:"
echo "  codex --profile dev"
