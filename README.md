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

## Install from GitHub

The dependable route is deliberately simple.

### From a Release

1. Open the repository's **Releases** page.
2. Download the LOOK ZIP attached to the newest release.
3. Unzip it.
4. In Terminal, `cd` into the folder you just unzipped.
5. Run:

```sh
chmod +x install.sh
./install.sh
```

GitHub downloads do not always preserve executable permissions, which is why the `chmod` step is included.

### From the green Code button

You can also use **Code → Download ZIP** on the repository page. Unzip it, enter the resulting folder (GitHub will usually name it something like `look-shell-main`), then run the same two commands:

```sh
chmod +x install.sh
./install.sh
```

The installer uses its own location as the source directory, so the checkout folder can have any name. You do **not** need to rename it.

### Terminal-only download

If you want to use `curl`, copy the actual ZIP URL shown by GitHub for the release you want rather than relying on a guessed asset name. For example:

```sh
curl -L "PASTE-THE-RELEASE-ZIP-URL-HERE" -o look-shell.zip
unzip look-shell.zip
cd <the-folder-that-was-created>
chmod +x install.sh
./install.sh
```

LOOK intentionally does not document a magic `/releases/latest/download/look-shell.zip` URL because that only works when the release maintainer has uploaded an asset with exactly that filename.

### Ollama anywhere: local, remote, or tailnet

LOOK 3.1 separates the `lo` interface from the machine doing the inference. Local Ollama remains the default and nothing remote is required.

```sh
lk ollama host
```

lists the current host, saved host profiles, and reachable Ollama servers LOOK discovers on your Tailscale peers. Tailscale device hostnames become the profile names automatically.

Select one persistently:

```sh
lk ollama host workstation
```

or use it for just one chat session:

```sh
lo @workstation
lo @workstation explain this project
```

Return to the current machine with `lk ollama host local`.

A host can also be saved explicitly:

```sh
lk ollama host workstation https://workstation.example.ts.net
```

Remove a saved profile with `lk ollama host forget workstation`.

To share the current machine's localhost Ollama only inside your tailnet:

```sh
lk ollama share
```

This uses Tailscale Serve in the background through a localhost-only LOOK proxy that preserves Ollama’s host protection. If Tailscale requires root/operator permission for Serve changes, LOOK keeps the proxy ready and prints the exact one-time `sudo tailscale serve --bg 11435` handoff. `lk ollama share status` shows the Serve state and `lk ollama share off` turns off this Ollama share.

Tailscale is optional. Without it, local Ollama and manually saved host URLs continue to work normally. LOOK still speaks the Ollama API only; 3.1 does not add provider-specific OpenAI or Anthropic adapters.

### Optional Ollama web search

If you use `lo`, a free Ollama account/API key enables its built-in web search. After installation:

```sh
lk ollama key
```

The key is stored privately in `~/.zsh_secrets`. `lk ollama key status` checks whether one is configured without revealing it.

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

LOOK keeps documentation in three layers:

1. **README** — the mental model, installation, and feature guide.
2. **`lk help` / `commands`** — the complete in-terminal command and key glossary.
3. **Contextual footers** — only the keys that matter in the state you are currently using.

There is intentionally no separate installed man/TLDR tree to drift out of sync. This section and `lk help` are the canonical reference.

### Complete command map

```text
LOOK / VIEWS
  lk [THING]                 inspect a path, command, port, or process
  lk detail [PATH]           detailed filesystem view
  lk dirs [PATH]             directories
  lk files [PATH]            files
  lk tree [PATH]             tree
  lk recent [PATH]           newest first
  lk size [PATH]             size-oriented
  lk run [PATH]              project/run inspection
  lk project [PATH]          alias of lk run

SYSTEM INSPECTION
  lk up | ports | services   listening services
  lk port NUMBER             one port
  lk process TERM | proc     process search
  lk processes | procs       interactive process list; Y copies PID
  lk pid NUMBER              one PID
  lk git [PATH]              Git state
  lk machine                 machine capabilities
  lk gpu                     GPU information
  lk disk                    disk usage
  lk net                     interactive addresses; Y copies IP
  lk tailscale               tailnet status
  lk env                     environment
  lk path                    PATH diagnostics
  lk why COMMAND             command resolution

OLLAMA / LO
  lo [ASK]                   local/default-host chat
  lo search [ASK]            chat with Ollama web search
  lo @HOST [ASK]             temporary host for one LO session
  lk o --no-start ...        do not auto-start missing local Ollama
  lk ollama                  Ollama and selected-host status
  lk ollama models           select/enable installed models
  lk ollama test             benchmark current model
  lk ollama test --all       compare enabled installed models
  lk ollama host             list saved/discovered hosts
  lk ollama host NAME        select persistent default
  lk ollama host local       return to localhost
  lk ollama host NAME URL    save and select an explicit endpoint
  lk ollama host forget NAME remove a saved remote profile
  lk ollama share            expose local Ollama through Tailscale Serve
  lk ollama share status     Serve + localhost rewrite-proxy status
  lk ollama share off        stop the Ollama tailnet share
  lk ollama key              securely write OLLAMA_API_KEY
  lk ollama key status       report key configuration without revealing it

MAINTENANCE
  lk home                    LOOK home
  lk doctor                  environment check
  lk config                  installed/state paths
  lk secrets                 secret-file status, never contents
  lk undo                    undo last safe local filesystem transaction
  lk uninstall               uninstall LOOK; optionally remove owned deps
  lk version                 version
  lk help                    complete in-terminal glossary
```

### Shell vocabulary

```text
l / ls      smart interactive view       ll       details
ld          directories                  lf       files
lt          tree                         lr       recent
lz          sizes                        zll WORD jump + look
cdl WORD    jump + details               f        find anywhere → LOOK
fznv        fuzzy find → Neovim          lh       LOOK home
lcp         assisted copy                lmv      assisted move
lscp        assisted scp                 lrm      assisted remove
lmk PATH    make directory path          mkd DIR  make + enter
lo          Ollama chat                  webterm  terminal over Tailscale
rs          reset ritual                 rb       reload Zsh
commands    same complete glossary as lk help
```

Bare `ls` is LOOK; `ls` with arguments and `command ls` reach ordinary Unix `ls`.

### Interactive file language

```text
Type        filter immediately
j/k/↑/↓     move selection; J/K/L/; also provide home-row directions
Tab         mark / unmark
A           mark all current matches / clear all marked matches
Enter       open file / enter folder
E           edit
O           open with
C           copy to filesystem destination
M           move
R           remove
B           copy actual file object(s) to desktop clipboard
Y           copy absolute path(s) as text
P           print absolute path and exit
G           leave LOOK and make this the shell's real directory
Esc         clear / back / cancel
q           quit
```

In a file card, `S` adds SCP. Long LOOK/help views use `Space`/`b` for paging, `j`/`k` or arrows for lines, `g`/`G` for the ends, and `q`/`Esc` to leave.

`CHANGELOG.md` records release history. The command map above is deliberately redundant with `lk help`: the README explains the system; the terminal glossary is the fast operational reference.

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
