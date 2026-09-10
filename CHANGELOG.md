# LOOK Shell changelog

## 3.1.4 — documentation reconciliation

- Audited the executable command dispatch, Zsh shortcuts, Ollama host/share/key grammar, and interactive file controls against the documentation.
- `lk help` is now the complete in-terminal command/key glossary, including Ollama `share status/off`, `key/status`, host selection/forget, uninstall, undo, webterm, and the full selection action language.
- README Reference now carries the same canonical command map, organized by intent.
- No runtime behavior changed.


## 3.1.3

- Make Ollama model choice host-aware: keep the preferred model when installed on the selected host, otherwise use a resident or installed model instead of surfacing Ollama's model-not-found 404.
- Restore `O open with` to the wrapped interactive filter/select footer; the action itself was never removed.


## 3.1.2 — Tailscale permission handoff

- `lk ollama share` keeps the localhost Host-rewrite proxy alive when Tailscale Serve requires root/operator permission.
- On that permission failure, LOOK prints the exact one-time `sudo tailscale serve --bg 11435` handoff instead of tearing the proxy back down.
- `lk ollama share off` gives the matching sudo handoff when needed.
- LOOK never invokes `sudo` itself and does not alter Tailscale operator configuration.


## 3.1.1 — Ollama share fix

- `lk ollama share` now places a tiny localhost-only proxy between Tailscale Serve and Ollama.
- The proxy rewrites the public tailnet `Host` header to `localhost:11434`, preserving Ollama's host protection while allowing private Tailscale Serve access.
- No new dependency, installer layer, command grammar, or unrelated behavior changes.


## 3.1.0 — Ollama anywhere

- Adds named Ollama host profiles while keeping `local` as the permanent built-in default.
- `lk ollama host` lists saved hosts and discovers reachable Ollama servers on Tailscale peers using their device hostnames.
- `lk ollama host NAME` selects a persistent default; `lk ollama host NAME URL` saves/selects an explicit endpoint.
- `lo @NAME` uses a host for one session without changing the default.
- `lk ollama share` shares localhost Ollama inside the tailnet through Tailscale Serve; `share status` and `share off` are included.
- Ollama inspection, model control, benchmarks, web search, memory, and workspace tools follow the selected host.
- Tailscale remains optional; local LOOK behavior is unchanged when it is absent.


## 3.0.5 — escape polish

- Hidden Ollama key entry: Esc, Ctrl-C, Ctrl-D, or empty Enter cancels cleanly.
- LO: Ctrl-C during thinking/searching cancels the current turn and returns control instead of tearing down the session.
- Filter typing captures queued keystrokes before redraw with a 12 ms idle gap instead of 55 ms.
- No command grammar, selection semantics, clipboard behavior, undo, or installer scope changed.


## 3.0.4 — Ollama key setup

- Adds `lk ollama key` and `lk ollama key status`.
- Excludes `key` from the historical long-form Ollama chat route, so these commands are handled locally rather than sent to `lo`.
- README encourages optional free Ollama account/API-key setup for web search.
- No other LOOK behavior changed.


## 3.0.3 — GitHub install instructions

- Removes the brittle guessed `/releases/latest/download/look-shell.zip` recipe.
- Documents two dependable install paths: GitHub Releases and Code → Download ZIP.
- Explains why `chmod +x install.sh` is needed after GitHub ZIP downloads.
- Makes clear that the installer is folder-name agnostic; `look-shell-main` and versioned release folders both work.
- No LOOK interaction, clipboard, selection, undo, uninstall, installer dependency, or LO behavior changed.


## 3.0.2 — clean exit

- Adds `lk uninstall`.
- Installer records exact package/add-on ownership for safe removal later.
- Uninstall restores the recorded pre-LOOK `.zshrc`, while preserving the current LOOK-era `.zshrc` as a timestamped recovery copy.
- `~/.zsh_secrets` is never removed.
- Homebrew/Linuxbrew itself is never automatically removed.
- README adds a copy/paste GitHub `releases/latest/download/look-shell.zip` installation path.
- No browser, clipboard, mark, navigation, undo, or LO grammar changed.


## 3.0.1 — complete mark toggle

- `A` now toggles the entire current match set: mark all when any are unmarked; clear all when all are already marked.
- This works with live filters, so `A` can select or deselect exactly the visible match set.
- No other selection, clipboard, navigation, undo, installer, or LO behavior changed.


## 3.0.0-beta.16 — onboarding and installer

No filesystem/browser grammar changed.

- The installer now explicitly treats LOOK as an opinionated workstation: `fd`, Chafa, Poppler, `ttyd`, and `lsof` join the existing core toolset.
- Tailscale is offered as the Remote layer (default Yes); Ollama is offered as the AI layer (default No).
- `--yes` accepts optional layers; `--no-optional` installs only the workstation.
- `webterm()` now explains missing requirements instead of falling through to shell errors.
- The first LOOK-initiated Neovim edit teaches `Esc`, `:q`, `Enter` once.
- README is rewritten around LOOK's present-day mental model rather than release archaeology.
- Documentation stays deliberately small: `README.md`, `CHANGELOG.md`, and the built-in `lk help`.

