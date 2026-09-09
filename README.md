# LOOK Shell

**An opinionated, human-readable layer over the Unix terminal.**

LOOK is a portable personal shell environment for macOS and Linux. It is built around a simple idea: the terminal should make you think about **what you want to know or do**, not which combination of Unix commands happens to express it.

`lk` means **look at this**.

``` text
lk .                 what is here?
lk python3           what is this command?
lk 8080              what owns this port?
lk run               what can I do here?
lk up                what is running?
lk machine           what machine am I on?
lk net               how am I connected?
lk ollama            what is Ollama doing?
```

LOOK does not replace Unix. It sits lightly on top of it. Zsh still navigates. Git is still Git. Ollama is still Ollama. Files are still files. The ordinary commands remain available whenever you want them.

LOOK is simply opinionated about the things you do all the time: **inspect first, make the common path obvious, keep dangerous actions explicit, and get out of the way.**

![LOOK Shell doctor](screenshots/LOOK_Shell_doctor.png)

![LOOK Shell help](screenshots/LOOK_Shell_help.png)




## LOOK 3 beta.5 input cleanup

Beta.5 is deliberately surgical. `Tab` now marks/unmarks filesystem selections, so `Space` remains ordinary live-filter text and multi-word searches work without changing the existing filter flow.

LOOK also recognizes the split-keyboard home-row arrow convention alongside physical arrows: `J K L ;` = left, down, up, right wherever the filesystem selector has directional movement. Existing arrow keys and the older lowercase `j/k` selection controls remain intact.


## LOOK 3 beta.4 additions

Beta.4 completes the filesystem handoff loop: **find → mark → act**.

Inside filesystem filtering/selection, `Space` marks or unmarks the current object and `A` marks all current filter matches. Marks persist while you move and filter and are shown with `✓`. With no marks, an action applies to the highlighted object; with marks, it applies to the marked set.

- `C` copies the selected/marked object(s).
- `M` moves them.
- `R` removes them with confirmation.
- `Y` copies one path or all marked paths to the clipboard.
- `G` means **go here**: leave LOOK and make the selected directory the actual parent-shell working directory. On a file, `G` goes to its containing directory.
- `Enter` keeps its existing meaning: browse a directory or open a file.
- `Esc` remains back/out and `q` remains quit.

Multi-item copy, move, and remove operations are stored as one LOOK undo transaction. The shell-directory handoff is deliberately tiny: the renderer writes one requested path, the Zsh wrapper consumes it immediately, changes directory with `builtin cd`, and deletes the request.


## LOOK 3 beta.3 additions

Beta.3 repairs arrow-key navigation in system selectors and gives `lk processes` a proper LOOK browse/filter loop: Enter starts filtering, arrows or J/K move, PageUp/PageDown page, `Y` copies the selected PID, and Escape backs out consistently. `lk net` uses the same selector and copies the selected IP.

Copy and move can now offer to create a missing destination directory and continue. Directory creation performed as part of that copy/move is recorded in the same undo transaction, so `lk undo` restores the original filesystem shape when it is still safe to do so.

Image preview is optional and capability-based. If `chafa` is installed, LOOK renders common image formats directly in the existing preview pane. PDF page 1 can render through the same path when a local PDF rasterizer is available (`pdftoppm`, or macOS Quick Look). None of these tools are required; without them LOOK keeps its existing text/metadata preview.


## LOOK 3 beta.2 additions

Beta.2 unifies Escape as LOOK's back/out gesture while retaining `q`, makes an empty interactive filter immediately select from all visible candidates, adds overflow paging to `lk doctor`, adds selectable/copyable network and process facts (`Y` copies the natural value), adds `lk processes`, and expands file actions with two-argument `lcp` / `lmv` / `lscp` plus undoable `lmk`.

## LOOK 3 beta

LOOK 3 keeps the **2.2 command language and behavior as the compatibility core** and modernizes the presentation layer around it.

The beta adds a terminal-native truecolor palette, softer visual hierarchy, clearer live states, a composed interactive footer, active-row surfaces, and faster state animation for real waiting states. It does not add a TUI framework, mouse dependency, daemon, or new command grammar.

Modern presentation is capability-based. On common truecolor terminals LOOK uses its 24-bit palette; otherwise it falls back to the existing ANSI presentation. To force the classic presentation at any time:

```bash
LOOK_CLASSIC=1 lk
LOOK_CLASSIC=1 l
LOOK_CLASSIC=1 lo
```

The rule for 3.x is simple: **2.2 behavior is constitutional. Presentation may evolve; muscle memory does not.**


## Install

``` sh
chmod +x install.sh
./install.sh --dry-run
./install.sh
exec zsh
lk doctor
```

The installer uses Homebrew/Linuxbrew for LOOK's dependencies, backs up
an existing `.zshrc`, preserves existing secrets, installs LOOK under
`~/.local/share/look`, and exposes `lk` through `~/.local/bin`.

Ollama is optional. LOOK does not install or manage Ollama. Starting `lo` may start a missing **local** Ollama server when the `ollama` binary is installed; `lo --no-start` preserves strict connect-only behavior.

## The LOOK grammar

There are only a few ideas to remember.

``` text
lk THING             inspect something
l                     look around interactively
lo                    talk to local Ollama
lcp / lmv / lrm       explicit local file actions
lk undo               undo the last LOOK file action
lh                    come home
```

Everything else is a refinement of those ideas.

An existing path is treated as a path. A number in the port range is treated as a port. An executable name is inspected as a command. LOOK can then make a conservative process-name match. Explicit views such as `git`, `machine`, `gpu`, `net`, `tailscale`, `ollama`, `env`, and `path` are predictable shortcuts into the same inspection grammar.

The distinction matters: **inspection is the default; mutation is explicit.**

## Looking at files

LOOK began as a better answer to “what's here?” and that remains its center.

``` text
l                  interactive smart view
ll                 detailed view
ld                 directories
lf                 files
lt                 tree
lr                 recently modified
lz                 size view

zll WORD           zoxide jump + smart view
cdl WORD           zoxide jump + detail view
fznv               fuzzy-find into Neovim
```

Small directories get a readable folders/files presentation. Larger directories collapse into a compact grouped grid. The renderer uses the actual terminal dimensions rather than assuming a fixed width.

LOOK's file vocabulary is intentionally visual but terminal-native:

``` text
◆  directory
▸  executable
↗  symlink
·  regular file
```

No patched font is required.

### Filtering and navigation

The short views stay interactive even when a directory contains only a few items. Press `Enter` or `/` to filter. Multiple words form an order-independent AND search, so `cache safari` finds names containing both terms.

``` text
Up / Down     choose
PageUp/Down   move through long results
Enter         browse directory / open file
E             edit
O             open with another installed application
Y             copy absolute path
P             print absolute path and exit
Esc           clear / leave filtering
q             quit
```

Lowercase letters remain ordinary search text; capital letters are actions.

Tree filtering searches recursively through the displayed depth and keeps parent directories as context. Wide terminals place previews beside results; narrow terminals place them below.

### Previews and file cards

LOOK keeps previews useful and bounded:

- text and source files show a chunk of readable text;
- directories show compact contents;
- PDFs show extracted text when `pdftotext` is available;
- images, media, archives, and binaries show useful type and size metadata.

`lk FILE` opens a richer interactive file card with metadata, a pageable preview, and explicit actions:

``` text
Enter   open
E       edit
Y       copy path
P       print path
M       move
C       copy
S       send with scp
R       remove
q       quit
```

LOOK opens executable files; it does not execute them merely because you inspected them.

## Looking at the computer

The same grammar extends beyond files.

``` text
lk run [PATH]        recognize a project and suggest useful actions
lk up / ports        show listening processes and ports
lk port NUMBER       inspect one port
lk process TERM      find a running process
lk pid NUMBER        inspect one process ID
lk git [PATH]        repo root, branch, origin, changes
lk machine / box     OS, CPU, RAM, disk, GPU capability
lk gpu               focused GPU status
lk disk              disk usage
lk net / network     local network + Tailscale identity
lk tailscale         tailnet status
lk ollama            Ollama server, model, and memory status
lk ollama models     list/select installed models
lk ollama test       benchmark the current model
lk ollama test --all compare installed models
lk env               useful environment
lk path              PATH entries, duplicates, missing directories
lk why COMMAND       explain command resolution and conflicts
```

`lk run` answers “what can I do here?” by recognizing markers such as `package.json`, `pyproject.toml`, `Cargo.toml`, `Makefile`, Docker files, and `index.html`. It suggests likely project commands but **never executes them**.

`lk up` answers the complementary question: “what is already running?”

`lk why COMMAND` reports the executable LOOK finds, its resolved symlink target, permissions, and alternate executable matches on PATH. Shell aliases and functions belong to the parent Zsh process, so LOOK points to `type -a COMMAND` when the shell itself needs to answer.

These system views are inspection tools. LOOK does not quietly start services, kill processes, edit PATH, or change system configuration.

## Acting on files

LOOK makes local filesystem actions explicit:

``` text
lcp [PATH]           copy
lmv [PATH]           move or rename
lrm [PATH]           remove
lscp [PATH]          send with scp
```

Without a path, the commands open a small `fzf` chooser in the current directory. With a path, they act on that path directly.

Removal uses a small confirmation:

``` text
remove file.txt? [r/Enter cancels] › r
```

The interactive `lk FILE` card and `lo` filesystem tools use the same underlying local mutation layer.

### Undo

``` text
lk undo
```

LOOK records its most recent local copy, move/rename, remove, and directory-creation operations. `lk undo` reverses the latest one regardless of whether it came from `lcp` / `lmv` / `lrm`, the interactive file card, or `lo`.

Removal is recoverable: LOOK moves the object into its private undo store instead of immediately destroying it. Undo is conservative. If reversing an action would overwrite something, remove a changed copy, or otherwise make an unsafe assumption, LOOK refuses.

The journal retains the most recent 20 LOOK transactions.

This is deliberately **LOOK undo**, not shell-wide magic. Ordinary `cp`, `mv`, `rm`, and other Unix commands remain untouched and are not added to LOOK's history. `lscp` is also outside undo because a remote filesystem change cannot be safely reversed locally.

## Ollama: `lo`

`lo` is a deliberately small terminal conversation interface for local Ollama.

``` sh
lo
lk o
lo explain this error
```

It reuses a resident model when one is available. If the local Ollama server is not running but the `ollama` binary exists, explicit `lo` use can start it; `lo --no-start` is strict connect-only behavior.

Bare `lk ollama` is inspection rather than chat:

``` text
ollama
  binary  /usr/local/bin/ollama
  server  ready
  model   qwen3:8b
  memory  idle
```

### Models and the LOOK benchmark

LOOK leaves the Ollama server itself alone. Model switching happens inside the running server:

``` text
lk ollama models
```

In an interactive terminal this opens a tiny Ollama control panel. `Enter` selects and preloads a model; `X` toggles whether that model participates in LOOK's `test --all` sweep. Disabled models remain installed and can still be selected directly — LOOK is keeping a personal benchmark list, not policing Ollama.

The list also shows Ollama-declared capabilities such as tools, thinking, and vision when the server reports them, plus resident and preferred state.

You can also select directly:

``` text
lk ollama models qwen3:4b
```

LOOK remembers the selection as the preferred `lo` model. `lk ollama` distinguishes that preferred model from every model Ollama currently has resident, since other programs may keep their own models loaded.

To compare responsiveness and terminal-assistant reliability:

``` text
lk ollama test
lk ollama test --all
```

The benchmark measures a warm model's time to first token and generation rate, then checks the tool judgments LOOK actually depends on: choosing `read_file` for a read request, `copy_path` instead of reconstructing a copy, and `web_search` for current information. If Ollama explicitly reports that a model has no tool capability, LOOK skips those tool requests and records `n/a` instead of treating the model as broken. If tool support is declared or unknown, LOOK measures what the model actually does. `--all` tests only models enabled in the control panel and restores the preferred model afterward.

This deliberately separates **declared capability** from **measured behavior**. A model can be an excellent fast chat model without qualifying as a full LOOK tool model.

This is not a general intelligence benchmark. It answers the more useful LOOK question: **which model is fast enough to disappear into the terminal while remaining reliable at the work LOOK asks it to do?**

### Workspace awareness

`lo` knows the directory in which it was started. It receives a bounded snapshot and, when supported by the model, can use a deliberately small filesystem toolset rooted to that workspace:

``` text
list_files       inspect directories
read_file        read bounded text
search_files     search names and bounded text
write_file       intentional UTF-8 text creation/editing
copy_path        exact copy; file copies are SHA-256 verified
move_path        move or rename
remove_path      explicit recoverable removal
make_directory   create a directory
```

Paths cannot escape the starting workspace. Binary and oversized reads are rejected or bounded. Existing files are protected unless replacement is explicitly requested. Arbitrary shell execution is not exposed.

The distinction between `write_file` and `copy_path` is intentional: **the model manipulates meaning; filesystem tools manipulate bytes.**

### Persistent memory without the wait

`lo` carries a small amount of memory across sessions: five compressed recent exchanges plus a rolling long-term summary.

``` text
~/.local/share/look/ollama_memory.json
```

Memory compression is housekeeping, so it does not sit on the interactive path. After an answer, the exchange is durably queued and a single detached LOOK worker remembers it in the background. You can keep talking or leave `lo` immediately.

``` text
lo › Here's the answer.

  · remembering in background

you ›
```

The worker processes queued exchanges serially and exits when there is nothing left to do. There is no daemon or persistent service. `lk ollama` reports whether memory is idle, queued, or remembering.

The memory file uses private permissions (`0600`).

### Web search

If `OLLAMA_API_KEY` is present in the shell environment, tool-capable models can use Ollama web search.

``` sh
lo search
lo search latest Ollama changes
```

`lo search` searches first on each turn. The key is inherited from the shell and is never copied into LOOK's configuration or memory.

## Home

``` text
lk home
lh
```

HOME is LOOK's small landing screen: current directory, Git branch when present, lightweight Ollama state, and a random fortune/cowsay. Then it immediately gives the shell back.

It is intentionally not a dashboard.

`rs` remains the old-school reset ritual: clear the screen, show machine information, fortune/cowsay, and return to work.

## Diagnostics and configuration

``` text
lk doctor            is LOOK healthy?
lk config            where is everything?
lk secrets           are secrets configured safely?
lk help              what can LOOK do?
lk version           what is installed?
```

`lk doctor` checks the core shell environment and reports optional capabilities such as Ollama without treating them as required.

Real secrets belong in:

``` text
~/.zsh_secrets
```

Only `zsh_secrets.example` belongs in Git. `lk secrets` reports the file's status and permissions, never its contents.

## Requirements

The installer handles LOOK's normal dependencies. The core environment uses Zsh, Python 3, Git, zoxide, fzf, Neovim, and a handful of small terminal utilities. Powerlevel10k and the configured Zsh plugins are installed as part of the shell setup.

Ollama is optional. PDF text previews are enhanced when `pdftotext` is available.

LOOK's Python side is otherwise deliberately boring: standard-library code, ordinary subprocesses, terminal dimensions, ANSI color, and native operating-system facilities where useful.

## Philosophy

LOOK is opinionated, but it is not possessive.

It does not try to replace the shell with an application, turn the terminal into a dashboard, hide the filesystem behind a database, or invent a new abstraction for every Unix command. It notices a smaller problem: many ordinary terminal tasks begin with a human question and end with remembering machinery.

**What's here?**

**Where is that file?**

**What owns this port?**

**Why is this command resolving there?**

**What can I run in this project?**

**What is Ollama doing?**

LOOK gives those questions a consistent surface. The cleverness stays underneath. When LOOK acts, the action is explicit and, where practical, reversible. When ordinary Unix is clearer, Unix remains right there.

Zsh handles navigation and composition. Python handles presentation and inspection. Small native tools do the jobs they already do well.

**Keep Unix. Lose some syntax.**
