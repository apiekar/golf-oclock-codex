#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$script_dir/.." && pwd)"
source_dir="$repo_dir/skills/golf-oclock"
codex_root="${CODEX_HOME:-$HOME/.codex}"
target_parent="$codex_root/skills"
target_dir="$target_parent/golf-oclock"

mkdir -p "$target_parent"

if [[ -L "$target_dir" ]] && [[ "$(readlink "$target_dir")" == "$source_dir" ]]; then
  echo "Golf O'Clock skill is already installed at $target_dir"
  exit 0
fi

if [[ -e "$target_dir" || -L "$target_dir" ]]; then
  echo "Refusing to overwrite existing path: $target_dir" >&2
  echo "Move or remove it manually, then run this installer again." >&2
  exit 1
fi

ln -s "$source_dir" "$target_dir"
echo "Installed Golf O'Clock skill at $target_dir"
echo "Start a fresh Codex session to load it."
