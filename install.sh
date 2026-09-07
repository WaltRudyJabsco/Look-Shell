#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1
have(){ command -v "$1" >/dev/null 2>&1; }
run(){ if ((DRY)); then printf '  →'; printf ' %q' "$@"; printf '\n'; else "$@"; fi; }
echo "LOOK — system installer"
echo "$(uname -s) · $(uname -m)"
if ! have brew; then
  if ((DRY)); then echo "✗ Homebrew (would install)"
  else
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    [[ -x /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv)"
    [[ -x /home/linuxbrew/.linuxbrew/bin/brew ]] && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
  fi
fi
declare -A P=([zsh]=zsh [python3]=python [git]=git [zoxide]=zoxide [fzf]=fzf [nvim]=neovim [bat]=bat [fortune]=fortune [cowsay]=cowsay)
missing=()
echo; echo "Dependencies"
for c in zsh python3 git zoxide fzf nvim bat fortune cowsay; do
  if have "$c"; then echo "✓ $c"; else echo "✗ $c"; missing+=("${P[$c]}"); fi
done
if have neofetch || have fastfetch; then echo "✓ system fetch"; else echo "✗ system fetch"; missing+=(fastfetch); fi
((${#missing[@]}==0)) || run brew install "${missing[@]}"

ZDIR="${ZSH:-$HOME/.oh-my-zsh}"
[[ -d "$ZDIR" ]] || run git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git "$ZDIR"
CUSTOM="${ZSH_CUSTOM:-$ZDIR/custom}"
clone(){ [[ -d "$2" ]] || run git clone --depth=1 "$1" "$2"; }
clone https://github.com/romkatv/powerlevel10k.git "$CUSTOM/themes/powerlevel10k"
clone https://github.com/zsh-users/zsh-autosuggestions.git "$CUSTOM/plugins/zsh-autosuggestions"
clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$CUSTOM/plugins/zsh-syntax-highlighting"

# `lk` is intentionally uncommon, but never silently replace another command.
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
run cp "$ROOT/lk" "$HOME/.local/share/look/lk"
run cp "$ROOT/look_renderer.py" "$HOME/.local/share/look/look_renderer.py"
run chmod +x "$HOME/.local/share/look/lk"
if ((!DRY)); then ln -sfn "$HOME/.local/share/look/lk" "$HOME/.local/bin/lk"; fi

if [[ -f "$HOME/.zshrc" ]]; then
  B="$HOME/.zshrc.backup.$(date +%Y%m%d-%H%M%S)"; run cp "$HOME/.zshrc" "$B"; echo "Backed up ~/.zshrc → $B"
fi
run cp "$ROOT/zshrc" "$HOME/.zshrc"
[[ -f "$HOME/.zsh_secrets" ]] || run cp "$ROOT/zsh_secrets.example" "$HOME/.zsh_secrets"
run chmod 600 "$HOME/.zsh_secrets"
if ((!DRY)); then zsh -n "$HOME/.zshrc"; echo; echo "LOOK installed."; echo "Run: exec zsh"; echo "Then: lk doctor"; fi
