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
