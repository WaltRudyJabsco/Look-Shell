# LOOK Shell

**Keep Unix. Lose some syntax.**

LOOK is an opinionated, human-readable interaction layer for a Unix workstation. It does not replace the shell, Finder, Git, Neovim, Tailscale, or Ollama. It gives the things you already use a small shared language built around intent.

The mental model is deliberately physical:

```text
l        look around here
f        find the thing I remember
lk X     tell me what I need to know about X
G        take me there
B        put this file in my clipboard
Y        give me its path
lo       talk about this workspace
lh       come home
Esc      back out
```

LOOK began as a better `ls`. It became a semantic control layer for the terminal: **find something, understand it, act on it, and keep moving.**

## Five minutes with LOOK

Look around the current directory:

```sh
l
```

Type ordinary fragments to filter. `Tab` marks things; `A` toggles all current matches: mark them all, or clear them all when they are already marked. With no marks, actions apply to the highlighted object. With marks, they apply to the marked set.

```text
Enter    open / enter folder
Tab      mark or unmark
A        mark / clear all matches
B        copy the actual file(s) to the desktop clipboard
Y        copy path(s) as text
C        copy to another filesystem location
M        move
R        remove
E        edit
O        open with
G        leave LOOK and make this the shell's real directory
Esc      clear / back
q        quit
```

On macOS, `B` uses native clipboard file objects for documents and folders and image data for a single common image, so the result can be pasted into Finder-, Mail-, chat-, and image-aware applications. `Y` is intentionally different: it copies the pathname as text.

Now find something anywhere under your home directory:

```sh
f
```

Start typing whatever you remember: part of a filename, project, directory, or phrase. LOOK uses `fd` + `fzf`, skips common cache/project junk, and hands the result back to the same LOOK action language. It does **not** immediately launch the result.

When you already know the next action is editing, `fznv` remains the direct fuzzy-to-Neovim path.

## `lk` means “look at this”

The inspection grammar is intentionally conservative:

```text
lk .                 what is here?
lk mercury_server.py inspect this file
lk python3           what is this command?
lk 8080              what owns this port?
lk process ollama    find this process
lk git               what is happening in this repository?
lk run               what can I do in this directory?
lk machine           what machine am I on?
lk disk              how is storage doing?
lk net               how am I connected?
lk tailscale         what is the tailnet doing?
lk ollama            what is Ollama doing?
lk env               what environment am I in?
lk why python        which python am I actually calling?
```

Existing paths are paths. Port-range numbers are ports. Executable names are commands. Process matching is conservative. Inspection is the default; mutation is explicit.

`lk doctor` checks the LOOK environment. `lk config`, `lk secrets`, `lk version`, and `lk help` expose the installation without revealing secret contents.

## Files without becoming a file manager

The short views are muscle-memory front doors:

```text
l / ls    smart interactive view
ll        details
ld        directories
lf        files
lt        tree
lr        recent
lz        sizes
zll WORD  zoxide jump + look
cdl WORD  zoxide jump + details
```

Bare `ls` uses LOOK. `ls` with arguments remains ordinary Unix `ls`, and `command ls` is always available.

LOOK keeps navigation in Zsh and presentation in Python. Entering folders inside LOOK does not silently change the parent shell. `G` is the explicit handoff: **go here for real**.

Escape is state-sensitive and consistent: clear a filter, cancel selection state, move back through LOOK's in-session browse history, then stay put at the starting point. `q` exits.

## Safe file actions

LOOK's local mutations are explicit and journaled:

```text
lcp [PATH]    copy
lmv [PATH]    move
lrm [PATH]    remove with confirmation
lmk PATH      make directory path
lscp [PATH]   scp (remote; outside local undo)
lk undo       undo the last LOOK local filesystem transaction
```

Multi-item browser operations are one undo transaction. Deletes go through LOOK's private trash so they can be restored when safe. Copy undo verifies the copied object has not changed; move undo refuses to overwrite a newly occupied original path.

The design rule is simple: **dangerous operations should be obvious, and mistakes should be recoverable when LOOK can prove recovery is safe.**

## Preview what you found

LOOK previews text and code directly. If `chafa` is present, common images render inside the terminal. PDFs can render page one when a local rasterizer is available; `pdftotext` also lets LOOK and LO extract text from text-bearing PDFs.

These are capabilities, not alternate interfaces. A missing preview helper degrades gracefully to text or metadata.

## LO: local AI with hands, not a shell

If Ollama is installed:

```text
lo
lo explain this project
lo search current Qwen3 tool support
lk ollama
lk ollama models
lk ollama test
lk ollama test --all
```

LO can inspect the current workspace through bounded LOOK tools: list, read, search, write, copy, move, remove, and make directories. It does not receive arbitrary shell execution. The model handles meaning; LOOK handles bytes and filesystem safety.

LO keeps five recent compressed exchange notes plus a rolling long summary in a local mode-0600 state file. Memory compression happens in a detached background worker so the prompt returns immediately.

When `OLLAMA_API_KEY` is present, `lo search` can use Ollama web search. Secrets stay in `~/.zsh_secrets`; LOOK reports their status but never prints their contents.

## Remote terminal

LOOK ships a small `webterm()` helper:

```sh
webterm
```

With `ttyd` and Tailscale available, it starts a writable Zsh terminal on local port 7681 and exposes it through Tailscale Serve on HTTPS port 8443. The point is not to invent remote administration; it is to make your own terminal available to your own devices with a tiny, memorable gesture.

## Install the latest GitHub release

For GitHub, publish the release asset with the stable name **`look-shell.zip`**. Then the newest release always has one copy/paste URL:

```sh
curl -L https://github.com/WaltRudyJabsco/Look-Shell/releases/latest/download/look-shell.zip -o look-shell.zip
unzip look-shell.zip
cd look-shell-*
chmod +x install.sh
./install.sh
```

## The opinionated installer

A fresh LOOK machine should behave like the LOOK we actually use.

```sh
chmod +x install.sh
./install.sh --dry-run
./install.sh
exec zsh
lk doctor
```

The **LOOK workstation** is installed automatically through Homebrew/Linuxbrew:

```text
zsh · python · git · zoxide · fzf · fd · neovim · bat
fortune · cowsay · fastfetch · chafa · poppler · ttyd · lsof
```

LOOK also installs Oh My Zsh, Powerlevel10k, zsh-autosuggestions, and zsh-syntax-highlighting. It backs up an existing `.zshrc`, preserves `.zsh_secrets`, installs itself under `~/.local/share/look`, and puts `lk` in `~/.local/bin`.

Two larger choices are offered separately:

- **Remote:** Tailscale is offered with a default of Yes because `webterm()` is already part of LOOK. Authentication into a tailnet remains yours.
- **AI:** Ollama is offered with a default of No. LOOK works without AI; `lo` becomes available when Ollama does.

For unattended installs, `--yes` accepts both optional offers. `--no-optional` installs only the workstation.

### Uninstall cleanly

LOOK has an exit door from the beginning:

```sh
lk uninstall
```

The uninstaller removes LOOK itself and restores the pre-LOOK `.zshrc` recorded by the installer. Before restoring it, LOOK preserves the current `.zshrc` as a timestamped `~/.zshrc.look-uninstalled.*` file so any edits made while using LOOK are still recoverable. `~/.zsh_secrets` is always preserved.

The installer also records exactly which Homebrew/Linuxbrew packages and shell add-on directories **it** created. During uninstall, LOOK offers to remove only those recorded dependencies. Anything that already existed before LOOK is left alone. Older LOOK installations without an ownership manifest err on the safe side and leave dependencies installed.

LOOK never automatically removes Homebrew/Linuxbrew itself.

### The Neovim joke, fixed

LOOK installs Neovim because a capable terminal editor should be there when `E` or `fznv` needs one. The first time LOOK itself opens Neovim, it teaches the one command Unix folklore assumes you already know:

```text
LOOK is opening Neovim.
To leave: Esc  :q  Enter
You'll only be told this once.
```

Then it never says it again.

## A little terminal personality

`lh` is LOOK's home screen: current directory, Git state, Ollama state, and a small fortune/cowsay ritual. `rs` remains the reset ritual. `rb` reloads Zsh.

LOOK 3 uses terminal-native truecolor when available and falls back to ANSI. The 2.2 interaction grammar is the compatibility constitution:

```sh
LOOK_CLASSIC=1 lk
LOOK_CLASSIC=1 l
LOOK_CLASSIC=1 lo
```

Presentation may evolve. Muscle memory should not.

## Reference

The README is the canonical explanation of LOOK: what it is, how the interaction model works, installation, major features, and the reasoning behind the system.

For the compact in-terminal command and key glossary:

```sh
lk help
```

`CHANGELOG.md` records release history. LOOK deliberately keeps its documentation footprint small rather than installing a parallel man/TLDR documentation system.

## Platform and philosophy

LOOK targets macOS and Linux with Zsh. The renderer and inspector are Python standard-library programs; external tools are used only where they provide a real capability.

The core rules:

- Keep the common path obvious.
- Inspect before mutating.
- Keep Unix underneath.
- Prefer gestures over syntax trivia.
- Make state visible.
- Let optional capabilities degrade gracefully.
- Undo what can be undone safely.
- Do not turn the terminal into a dashboard.
- Do not make the user remember machinery that LOOK can remember for them.

**Keep Unix. Lose some syntax.**
