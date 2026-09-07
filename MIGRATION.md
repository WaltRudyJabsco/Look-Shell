# LOOK 0.6.5

Installer compatibility release.

- Fixes macOS system Bash 3.2 failing at installer line 17 with `zsh: unbound variable`.
- Replaces the Bash 4 associative-array dependency map with a Bash 3.2-compatible `case` mapper.
- Runtime behavior is otherwise unchanged from 0.6.4.

