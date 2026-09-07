# LOOK Shell

A portable personal shell environment for macOS and Linux. LOOK combines a responsive filesystem renderer, zoxide navigation, fuzzy finding, Neovim integration, diagnostics, and a small interactive file navigator.

## Install

```sh
chmod +x install.sh
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

The short commands (`l`, `ll`, `ld`, `lf`, `lt`, `lr`, `lz`) enter the interactive LOOK view. Press `Enter` or `/` to start a live filter. Filtering uses substring matching; separate words with spaces to require every term, such as `cache safari`. The highlighted match can be changed immediately with the arrow keys, so nearly identical names never have to be typed to uniqueness.

```text
Up / Down    choose highlighted match
PageUp/Down  move through long result sets
Enter        directory: browse deeper · file: open with OS default
E            edit highlighted file
O            choose another application to open the file
Y            copy the absolute path
P            print the absolute path and exit
Backspace    delete filter text
Esc          clear / leave filtering
q            quit
```

Capital action keys are intentional while filtering: lowercase letters remain ordinary search text. In the older explicit selection state, lowercase action keys remain accepted as aliases.

Bare `lk` and explicit `lk detail`, `lk tree`, and similar commands keep the quick print-and-return behavior when the view fits. LOOK deliberately opens executable files rather than executing them; running code remains an explicit shell action.

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

## 0.4.4

- `ls` invokes LOOK only when used with no arguments.
- `ls -l`, `ls -la`, `ls FILE`, and other normal Unix `ls` forms pass through unchanged.
- `~/.local/bin` is explicitly added to `PATH`, so `lk` remains available after starting a fresh Zsh session.

## 0.4.5

Packaging fix: the ZIP now preserves executable permissions for `install.sh`
and `lk` on Unix systems, so `./install.sh` works immediately after extraction.

## 0.5.0 — LOOK Ollama

A surgical local-AI shortcut:

```bash
lo
lk o
lk ollama
```

If Ollama is reachable and a model is already loaded, LOOK opens a minimal
terminal chat using that model. It does not start Ollama, load models, or
manage them.


## 0.5.1 — Ollama web search

`lo` keeps normal local chat and exposes web search to tool-capable models when `OLLAMA_API_KEY` is available in the environment. `lo search` searches first on every turn, then answers from the current results. The key is inherited from the shell and is never stored by LOOK.


## 0.6.0 — Ollama memory + capability checks

`lk doctor` now reports optional Ollama state: binary, local server, loaded model, web-search key, and persistent memory. The installer creates LOOK's private memory state file but does not install Ollama automatically.

`lo` now carries bounded persistent memory across sessions: five recent compressed exchanges plus one rolling long-term summary. When a sixth recent exchange is added, the oldest is folded into long memory and the recent window stays at five.

Memory lives at `~/.local/share/look/ollama_memory.json` with mode `0600`.


## 0.6.1

Renderer fixes:

- Tree mode silently skips protected/unreadable macOS folders instead of flooding the terminal with permission errors.
- Bare `Esc` reliably exits/clears filter mode; arrow and paging escape sequences still work.
- `lt` filtering now searches recursively through the same tree depth being displayed, so visible descendants can be found by typing their names.


## 0.6.3

- Filtering now matches substrings, not only filename prefixes.
- Selection mode adds a responsive preview pane: right-side on wide terminals, bottom on narrow terminals. Text is previewed directly; directories show contents; PDFs use first-page text when `pdftotext` is available; other binaries show type/size metadata.
- `l WORD` now means smart navigation: explicit directories are entered directly, otherwise Zoxide resolves a previously visited directory before LOOK renders it.

## 0.6.11 — filter polish

Rapid filter typing is lightly debounced to avoid expensive redraws on every character. In live filter mode, `E` edits the highlighted file while lowercase letters remain available for searching.

## 0.6.8 — live filter selection

`lo` now receives the actual starting working directory and a bounded top-level directory snapshot as system context, so references such as “this folder” and “here” have a concrete meaning.

Tool-capable local models also receive four intentionally small filesystem tools rooted to that starting directory: list folders/files (up to three levels), read bounded text files, search filenames and bounded text content, and create/write UTF-8 text files. Paths outside the starting workspace are rejected, binary reads are rejected, large reads/searches are bounded, existing files are protected unless replacement is explicitly requested, and arbitrary shell execution is not exposed.


## 1.0.0 — stable LOOK

LOOK 1.0.0 marks the stable filesystem/navigation interface. Live filtering now exposes the complete non-destructive action set without colliding with search text: `E` edit, `O` open with another application, `Y` copy absolute path, and `P` print absolute path and exit. The existing default-open, preview, recursive filtering, navigation, Ollama workspace tools, memory, and installer behavior are otherwise unchanged.
