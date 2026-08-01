#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This setup script requires macOS Keychain." >&2
  exit 1
fi

echo "Enter the Golf O'Clock API key when Keychain prompts."
echo "The value will not be stored in shell history."
/usr/bin/security add-generic-password \
  -U \
  -a "codex" \
  -s "the-tips-golf-oclock-api" \
  -l "The Tips Golf O'Clock API for Codex" \
  -j "Read-only Golf O'Clock API credential for local Codex use" \
  -w

echo "Saved the Golf O'Clock API key in macOS Keychain."
