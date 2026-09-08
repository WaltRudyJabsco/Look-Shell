# LOOK 1.0.6

A surgical Ollama-interface polish release.

- `lo` now explicitly knows that LOOK renders lightweight Markdown and encourages concise terminal-readable formatting.
- The system prompt now describes the available workspace file tools, optional web search, and their boundaries so the model does not have to infer its environment.
- Markdown `http/https` links use OSC 8 terminal hyperlinks when supported, allowing labeled links to be clicked directly in compatible terminals.
- No changes to model loading, memory policy, search semantics, filesystem-tool behavior, navigation, filtering, or installer behavior.


## 1.0.6

- Web-result instructions now require exact returned URLs in complete Markdown links.
- Prevents pseudo-citations such as `[source]` or styled site names with no clickable target.
- OSC 8 rendering, search transport, memory, tools, and filesystem behavior are unchanged.


## 1.0.6

- Web links now keep the full literal URL visible instead of relying on hidden OSC 8 hyperlink metadata.
- `lk help` gains restrained ANSI color for its header, sections, and command/key vocabulary.
- Model, memory, search transport, filesystem, navigation, and installer behavior are unchanged.


## 1.0.7

- Fixes `lk help` `NameError: re is not defined` introduced by the 1.0.6 help-color formatter.
- No behavior changes beyond this fix.


## 1.0.8

- Adds `lk home` and the `lh` shortcut.
- HOME paints a clean LOOK landing screen, current folder, optional Git branch, lightweight Ollama status, and a cowsay fortune, then returns to the shell.
- `rs`, filesystem behavior, Ollama chat, memory, and installer behavior are unchanged.


## 2.0.0

LOOK now treats `lk` as a general inspection verb while preserving the 1.x filesystem interface. New read-only views include `run`, `up`/`ports`, `git`, `machine`/`box`, `gpu`, `net`/`network`, `tailscale`, `ollama`, `env`, `path`, and `why COMMAND`. A single unknown argument is conservatively classified as an existing path, port, executable command, or matching process.

Compatibility note: `lo` and `lk o` remain the Ollama chat interface. Bare `lk ollama` is now the Ollama inspection view; `lk ollama search ...` and `lk ollama <prompt>` still enter chat.

## 2.0.1

- Packaging sync release for the canonical GitHub 2.0 files.
- Preserves the user-added `webterm()` Zsh helper for ttyd + Tailscale Serve.
- No LOOK runtime behavior changes from 2.0.0.

## 2.1.0

- `lk FILE` now shows a richer file card with bounded text/source preview and first-page PDF text when available.
- Adds explicit LOOK-assisted file verbs: `lmv`, `lcp`, `lscp`, and `lrm`.
- With no path, file verbs use a current-directory `fzf` picker; with a path they act directly.
- Move/copy preserve Unix interactive collision handling; directory copies are recursive.
- `lrm` requires typing `REMOVE` before calling Unix `rm`.
- Existing `mv`, `cp`, `scp`, `rm`, filesystem views, inspection grammar, `lo`, `rs`, `webterm()`, and HOME remain unchanged.

## 2.1.1

- Fixes the 2.1.0 file-card interaction bug: `lk FILE` no longer prints a card and immediately returns to the shell.
- File cards are now interactive and paged until `q`/Esc.
- Live keys: Enter open, E edit, Y copy path, P print path, M move, C copy, S scp, R remove.
- File mutation remains explicit; removal still requires typing `REMOVE`.
- Directory LOOK behavior and all other 2.1.0 features are unchanged.

## 2.1.2

- Adds bounded `copy_path`, `move_path`, `remove_path`, and `make_directory` tools to `lo`.
- `copy_path` uses filesystem copy semantics rather than model-mediated read/write reconstruction.
- File copies are SHA-256 verified before success is reported.
- `write_file` is now explicitly reserved for intentional UTF-8 text creation/editing and should never be used to duplicate an existing file.
- Move/remove/mkdir stay inside the starting LOOK workspace; removal requires an explicit user request.
- No arbitrary shell execution was added.
