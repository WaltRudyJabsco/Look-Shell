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
