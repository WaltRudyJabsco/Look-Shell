# LOOK 1.0.2

Surgical polish release from 1.0.1.

- Help and `commands` show the stable live-filter action keys: `E`, `O`, `Y`, `P`.
- The help pager accepts `j/k`, Up/Down, PageUp/PageDown, Space, `b`, `g/G`, `q`, and Esc.
- `lo` no longer requires a model to already be resident. A loaded model is reused; otherwise `LOOK_OLLAMA_MODEL` is used (default `qwen3:8b`) and Ollama loads it on demand.
- If the configured `OLLAMA_HOST` is local and unreachable, explicit `lo` use may start `ollama serve` when the binary exists. Use `lo --no-start` for connect-only behavior.
- Filesystem rendering, filtering, previews, memory, web search, and file-tool behavior are unchanged.
