#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY=0
ASSUME_YES=0
NO_OPTIONAL=0
BREW_BOOTSTRAPPED=0
installed_packages=()
created_dirs=()
ZSH_BACKUP=""

usage() {
  cat <<'EOF'
LOOK — system installer

Usage:
  ./install.sh [--dry-run] [--yes] [--no-optional]

  --dry-run      show what LOOK would do
  --yes          install offered Remote + AI components without prompting
  --no-optional  install the LOOK workstation only
EOF
}

while (($#)); do
  case "$1" in
    --dry-run) DRY=1 ;;
    --yes|-y) ASSUME_YES=1 ;;
    --no-optional) NO_OPTIONAL=1 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
  shift
done

have(){ command -v "$1" >/dev/null 2>&1; }
run(){ if ((DRY)); then printf '  →'; printf ' %q' "$@"; printf '\n'; else "$@"; fi; }
ask() {
  local prompt="$1" default="$2" answer
  if ((NO_OPTIONAL)); then return 1; fi
  if ((ASSUME_YES)); then return 0; fi
  if ((DRY)) || [[ ! -t 0 ]]; then
    [[ "$default" == "Y" ]]
    return
  fi
  if [[ "$default" == "Y" ]]; then
    read -r -p "$prompt [Y/n] " answer
    [[ ! "$answer" =~ ^[Nn] ]]
  else
    read -r -p "$prompt [y/N] " answer
    [[ "$answer" =~ ^[Yy] ]]
  fi
}

echo "LOOK — opinionated Unix workstation installer"
echo "$(uname -s) · $(uname -m)"
echo
echo "LOOK installs the small tools its own interface is built around."
echo "Remote access and local AI are offered separately."

if ! have brew; then
  if ((DRY)); then
    echo "✗ Homebrew/Linuxbrew (would bootstrap)"
  else
    echo
    echo "BOOTSTRAP"
    echo "  LOOK uses Homebrew/Linuxbrew as its package layer."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    BREW_BOOTSTRAPPED=1
    [[ -x /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv)"
    [[ -x /home/linuxbrew/.linuxbrew/bin/brew ]] && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
  fi
fi

package_for() {
  case "$1" in
    python3) printf '%s\n' python ;;
    nvim) printf '%s\n' neovim ;;
    pdftotext) printf '%s\n' poppler ;;
    *) printf '%s\n' "$1" ;;
  esac
}

echo
echo "LOOK WORKSTATION"
core=(zsh python3 git zoxide fzf fd nvim bat fortune cowsay fastfetch chafa pdftotext ttyd lsof)
missing=()
for c in "${core[@]}"; do
  if have "$c"; then
    printf '  ✓ %s\n' "$c"
  else
    printf '  ✗ %s\n' "$c"
    missing+=("$(package_for "$c")")
  fi
done
if ((${#missing[@]})); then
  run brew install "${missing[@]}"
  if ((!DRY)); then installed_packages+=("${missing[@]}"); fi
fi

# Remote is deliberately offered rather than silently assumed: installation is
# useful only after the user authenticates this machine into a tailnet.
echo
echo "LOOK REMOTE"
if have tailscale; then
  echo "  ✓ tailscale"
else
  echo "  webterm() can expose this shell securely to your own devices."
  if ask "  Install Tailscale?" Y; then
    run brew install tailscale
    if ((!DRY)); then installed_packages+=("tailscale"); fi
  else
    echo "  · skipped tailscale"
  fi
fi

# Ollama is a larger choice. LOOK supports it deeply but does not require it.
echo
echo "LOOK AI"
if have ollama; then
  echo "  ✓ ollama"
else
  echo "  lo adds local chat, workspace tools, memory, search, and PDF reading."
  if ask "  Install Ollama?" N; then
    run brew install ollama
    if ((!DRY)); then installed_packages+=("ollama"); fi
  else
    echo "  · skipped ollama"
  fi
fi

ZDIR="${ZSH:-$HOME/.oh-my-zsh}"
if [[ ! -d "$ZDIR" ]]; then
  run git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git "$ZDIR"
  if ((!DRY)); then created_dirs+=("$ZDIR"); fi
fi
CUSTOM="${ZSH_CUSTOM:-$ZDIR/custom}"
clone() {
  if [[ ! -d "$2" ]]; then
    run git clone --depth=1 "$1" "$2"
    if ((!DRY)); then created_dirs+=("$2"); fi
  fi
}
clone https://github.com/romkatv/powerlevel10k.git "$CUSTOM/themes/powerlevel10k"
clone https://github.com/zsh-users/zsh-autosuggestions.git "$CUSTOM/plugins/zsh-autosuggestions"
clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$CUSTOM/plugins/zsh-syntax-highlighting"

if have lk; then
  existing_lk="$(command -v lk)"
  case "$existing_lk" in
    "$HOME/.local/bin/lk"|"$HOME/.local/share/look/lk") ;;
    *)
      echo "WARNING: 'lk' already exists at: $existing_lk"
      echo "LOOK will install ~/.local/bin/lk; review this collision if that command matters to you."
      ;;
  esac
fi

run mkdir -p "$HOME/.local/share/look" "$HOME/.local/bin"
if ((!DRY)); then
  MEMORY="$HOME/.local/share/look/ollama_memory.json"
  if [[ ! -f "$MEMORY" ]]; then
    printf '{"long":"","recent":[]}\n' > "$MEMORY"
    chmod 600 "$MEMORY"
  fi
fi

run cp "$ROOT/lk" "$HOME/.local/share/look/lk"
run cp "$ROOT/look_renderer.py" "$HOME/.local/share/look/look_renderer.py"
run chmod +x "$HOME/.local/share/look/lk"
if ((!DRY)); then ln -sfn "$HOME/.local/share/look/lk" "$HOME/.local/bin/lk"; fi

if [[ -f "$HOME/.zshrc" ]]; then
  B="$HOME/.zshrc.backup.$(date +%Y%m%d-%H%M%S)"
  run cp "$HOME/.zshrc" "$B"
  ZSH_BACKUP="$B"
  echo "Backed up ~/.zshrc → $B"
fi
run cp "$ROOT/zshrc" "$HOME/.zshrc"
[[ -f "$HOME/.zsh_secrets" ]] || run cp "$ROOT/zsh_secrets.example" "$HOME/.zsh_secrets"
run chmod 600 "$HOME/.zsh_secrets"

if ((!DRY)); then
  zsh -n "$HOME/.zshrc"

  # Record only what this installer can prove it added. `lk uninstall` uses
  # this manifest so it never guesses that a pre-existing package belongs to LOOK.
  export LOOK_MANIFEST_PACKAGES="$(printf '%s\n' "${installed_packages[@]-}")"
  export LOOK_MANIFEST_DIRS="$(printf '%s\n' "${created_dirs[@]-}")"
  export LOOK_MANIFEST_ZSH_BACKUP="$ZSH_BACKUP"
  export LOOK_MANIFEST_BREW_BOOTSTRAPPED="$BREW_BOOTSTRAPPED"
  python3 - <<'PY'
import json, os
from pathlib import Path

state = Path.home()/".local/share/look"
state.mkdir(parents=True, exist_ok=True)
manifest = {
    "version": "3.0.3",
    "packages": [x for x in os.environ.get("LOOK_MANIFEST_PACKAGES","").splitlines() if x],
    "created_dirs": [x for x in os.environ.get("LOOK_MANIFEST_DIRS","").splitlines() if x],
    "zsh_backup": os.environ.get("LOOK_MANIFEST_ZSH_BACKUP",""),
    "brew_bootstrapped": os.environ.get("LOOK_MANIFEST_BREW_BOOTSTRAPPED","0") == "1",
}
tmp = state/"install_manifest.json.tmp"
tmp.write_text(json.dumps(manifest, indent=2) + "\n")
tmp.chmod(0o600)
tmp.replace(state/"install_manifest.json")
PY

  echo
  echo "LOOK installed."
  echo "  1. exec zsh"
  echo "  2. lk doctor"
  echo "  3. l          # look around"
  echo "  4. f          # find anything under home"
  echo
  echo "Reference: lk help"
fi
