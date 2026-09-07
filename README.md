# LOOK Shell

A portable personal shell environment for macOS and Linux. LOOK combines a responsive filesystem renderer, zoxide navigation, fuzzy finding, Neovim integration, diagnostics, and a small interactive file navigator.

## Install

```sh
./install.sh --dry-run
./install.sh
exec zsh
lk doctor
```

## Core commands

```text
lk                 smart filesystem view
lk detail          detailed view
lk dirs            directories
lk files           files
lk tree            tree
lk recent          newest first
lk size            size-oriented
lk doctor          environment health
lk config          installed paths
lk secrets         secrets status, never contents
lk help            full command screen
lk version         version
```

The fast vocabulary remains: `l`, `ll`, `ld`, `lf`, `lt`, `lr`, `lz`, `zll`, `cdl`, `fznv`, `f`, `rs`, and `commands`.

## Interactive LOOK

In a long listing, press `Enter` (or `/`) to begin filtering. Type a filename prefix; `Backspace` edits it. Press `Enter` again to accept the filter and enter selection mode.

```text
j / k       choose among matching items
Enter       directory: browse deeper · file: open with OS default
e           edit selected item with $EDITOR / nvim / vi
y           copy the selected item's absolute path
p           print the selected item's absolute path and exit
Esc         return to filtering / clear
q           quit
```

Normal paging remains `Space`, `b`, `j/k`, `g/G`, and `q`.

LOOK deliberately opens executable files rather than executing them. Running code remains an explicit shell action.

## Secrets

Real secrets stay in `~/.zsh_secrets`; only `zsh_secrets.example` belongs in Git.


## 0.4.1

`lk help` now uses a lightweight built-in pager only when the help text exceeds the current terminal height. `doctor`, `config`, and `version` remain immediate.

## 0.4.2

Fixed the `lk help` pager's staircase/zig-zag terminal output. The pager now
uses cbreak input mode instead of raw mode, preserving normal newline handling
while retaining single-key controls.


## 0.4.3

Restored the ASCII `LK` header in `lk help`. Paging behavior from 0.4.2 is unchanged.
