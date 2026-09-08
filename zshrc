# ─────────────────────────────────────────────────────────────────────────────
# Sasha's Zsh — shell/navigation stays shell; LOOK owns filesystem presentation.
# ─────────────────────────────────────────────────────────────────────────────

# Powerlevel10k instant prompt: keep near the top.
export PATH="$HOME/.local/bin:$PATH"
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Homebrew: Apple Silicon, Intel Mac, or Linuxbrew.
if (( $+commands[brew] )); then
  eval "$(brew shellenv)"
elif [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -x /usr/local/bin/brew ]]; then
  eval "$(/usr/local/bin/brew shellenv)"
elif [[ -x /home/linuxbrew/.linuxbrew/bin/brew ]]; then
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi

# Prefer Homebrew Ruby without hard-coding a Ruby ABI such as 3.4.0.
if (( $+commands[brew] )) && brew --prefix ruby &>/dev/null; then
  path=("$(brew --prefix ruby)/bin" $path)
fi

# Optional Node 18 if installed through Homebrew.
if (( $+commands[brew] )) && brew --prefix node@18 &>/dev/null; then
  path=("$(brew --prefix node@18)/bin" $path)
fi

# Secrets never belong in this file.
[[ -r "$HOME/.zsh_secrets" ]] && source "$HOME/.zsh_secrets"

export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"
ENABLE_CORRECTION="true"
plugins=(git zsh-syntax-highlighting zsh-autosuggestions web-search)
source "$ZSH/oh-my-zsh.sh"

# ── Navigation ────────────────────────────────────────────────────────────────
if (( $+commands[zoxide] )); then
  eval "$(zoxide init zsh)"
fi

alias rb='exec zsh'
alias c='clear'
alias neo='neofetch'
# Small command glossary. Keep it short enough to actually be useful.
commands() {
  print -P '%F{cyan}%BLOOK SHELL%b%f  %F{244}filesystem + navigation%f'
  print ''
  print -P '%F{75}  l / ls%f   smart view        %F{75}ll%f       details'
  print -P '%F{75}  ld%f       directories       %F{75}lf%f       files'
  print -P '%F{75}  lt%f       tree              %F{75}lr%f       recent'
  print -P '%F{75}  lz%f       sizes             %F{75}zll WORD%f jump + look'
  print -P '%F{75}  cdl WORD%f jump + details    %F{75}fznv%f     fuzzy edit'
  print -P '%F{75}  f%f        fuzzy open        %F{75}mkd DIR%f  make + enter'
  print -P '%F{75}  rb%f       reload shell      %F{75}rs%f       reset ritual'
  print ''
  print -P '%F{244}Inside a long LOOK view: Space page · b back · ↑↓/jk row · g/G ends · q quit%f'
  print -P '%F{244}Real Unix ls is always available as: command ls%f'
}

rs() {
  c
  (( $+commands[neofetch] )) && neo
  if (( $+commands[fortune] && $+commands[cowsay] )); then
    fortune | cowsay -r
  fi
  print -P '%F{244}commands  →  quick shell glossary%f'
}


# These two are intentionally yours. They make interactive navigation wonderful.
alias cd='z'
alias ..='cd ..'
alias zz='z -'

# ── LOOK: dynamic filesystem renderer ────────────────────────────────────────
# Install helper at ~/.local/bin/look.py. It never pipes rendered output through
# less/colorls; it owns terminal layout and paging itself.
LOOK="$HOME/.local/bin/lk"

_look() {
  if [[ ! -x "$LOOK" ]]; then
    print -P "%F{red}LOOK helper missing:%f $LOOK"
    print "Install look.py into ~/.local/bin/look.py and chmod +x it."
    return 127
  fi
  "$LOOK" "$@"
}

# Oh My Zsh may own some of these names; clear them before function parsing.
# (This line must stay before the function definitions.)
unalias ls l ll ld lf lt lr lz lsd lsf lc 2>/dev/null

# Human-facing filesystem vocabulary.
l() {
  if (( $# == 0 )); then
    _look . --mode smart --interactive
    return
  fi

  # `l WORD` means navigate there, then LOOK. Explicit directories win;
  # otherwise let zoxide resolve previously visited shorthand.
  if (( $# == 1 )) && [[ -d "$1" ]]; then
    builtin cd -- "$1" || return
    _look . --mode smart --interactive
    return
  fi

  local target
  target="$(zoxide query -- "$@" 2>/dev/null)" || {
    print -P "%F{red}LOOK:%f no directory match for $*"
    return 1
  }
  builtin cd -- "$target" || return
  _look . --mode smart --interactive
}
ll()  { _look "${1:-.}" --mode detail --interactive; }
ld()  { _look "${1:-.}" --mode dirs --interactive; }
lf()  { _look "${1:-.}" --mode files --interactive; }
lt()  { _look "${1:-.}" --mode tree --depth 3 --interactive; }
lr()  { _look "${1:-.}" --mode recent --interactive; }
lz()  { _look "${1:-.}" --mode size --interactive; }

# Keep your old names too: muscle memory is an API.
lsd() { ld "$@"; }
lsf() { lf "$@"; }
lc()  { ll "$@"; }

# Your original idea survives: normal interactive `ls` means smart LOOK.
# `command ls` always reaches the real Unix command when you need it.
ls() {
  if (( $# == 0 )); then
    lk
  else
    command ls "$@"
  fi
}

# Zoxide jump + immediate orientation. These are worth keeping exactly.
zll() {
  z "$@" || return
  l
}

cdl() {
  z "$@" || return
  ll
}

mkd() {
  [[ $# -eq 1 ]] || { print "usage: mkd <directory>"; return 2; }
  mkdir -p -- "$1" || return
  builtin cd -- "$1"
}

# ── Fuzzy files ──────────────────────────────────────────────────────────────
displayFZFFiles() {
  fzf --preview 'bat --theme=gruvbox-dark --color=always --style=header,grid --line-range :400 -- {}'
}

fznv() {
  (( $+commands[nvim] )) || return 127
  local selection
  selection=$(displayFZFFiles) || return
  [[ -n "$selection" ]] && nvim -- "$selection"
}

# Open a fuzzy-picked path in the desktop environment.
f() {
  local selection
  selection=$(fzf) || return
  [[ -z "$selection" ]] && return
  if [[ "$OSTYPE" == darwin* ]]; then
    open -- "$selection"
  elif (( $+commands[xdg-open] )); then
    xdg-open "$selection" >/dev/null 2>&1 &!
  fi
}

# ── Personal tools / projects ────────────────────────────────────────────────
alias trackflight='flightProgress'
[[ "$OSTYPE" == darwin* ]] && alias love='/Applications/love.app/Contents/MacOS/love'
alias rst='python3 ~/Desktop/misc-programs/labs/reboot_screen_improbability.py'
alias rzt='python3 ~/Desktop/misc-programs/labs/future_crash_oracle_web.py --ollama --web --model qwen3:8b'
alias dub='python3 ~/Desktop/misc-programs/labs/oracle_sound_system_dub.py --ollama --web --model qwen3:8b'
alias rzt2='python3 ~/Desktop/misc-programs/labs/future_crash.py --model qwen3:8b'

flightProgress() {
  while true; do
    ./flight.sh "$1" "$2" | ./parse_flight_progress.sh
    sleep 60
  done
}

# Optional helpers should never break shell startup.
(( $+commands[thefuck] )) && eval "$(thefuck --alias)"
[[ -f ~/.fzf.zsh ]] && source ~/.fzf.zsh
[[ -f ~/.p10k.zsh ]] && source ~/.p10k.zsh

# LOOK unified command
commands() { "$HOME/.local/bin/lk" help; }

# LOOK Ollama — minimal on-demand chat; a resident model is reused when available.
alias lo='lk o'
