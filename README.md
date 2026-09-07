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

## 0.6.5 — macOS installer compatibility

`lo` now receives the actual starting working directory and a bounded top-level directory snapshot as system context, so references such as “this folder” and “here” have a concrete meaning.

Tool-capable local models also receive four intentionally small filesystem tools rooted to that starting directory: list folders/files (up to three levels), read bounded text files, search filenames and bounded text content, and create/write UTF-8 text files. Paths outside the starting workspace are rejected, binary reads are rejected, large reads/searches are bounded, existing files are protected unless replacement is explicitly requested, and arbitrary shell execution is not exposed.
