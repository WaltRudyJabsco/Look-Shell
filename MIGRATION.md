# LOOK 0.6.4

Surgical upgrade from 0.6.3. Existing shell configuration, Ollama memory, secrets, filesystem UI, navigation, and web-search behavior are unchanged.

`lo` now knows the directory it was launched from and can use bounded local filesystem tools inside that workspace: list, read, search, and write text files. It cannot escape the starting workspace and it has no arbitrary command-execution tool.
