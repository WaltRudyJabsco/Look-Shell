#!/usr/bin/env python3
"""LOOK — responsive terminal filesystem renderer.

Install manually:
    mkdir -p ~/.local/bin
    cp look.py ~/.local/bin/look.py
    chmod +x ~/.local/bin/look.py

Normally installed by the repository's ./install.sh.
"""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import select
import subprocess
import sys
import termios
import tty
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

RESET='\x1b[0m'; BOLD='\x1b[1m'; DIM='\x1b[2m'; REVERSE='\x1b[7m'
BLUE='\x1b[38;5;75m'; CYAN='\x1b[38;5;81m'; GREEN='\x1b[38;5;114m'; YELLOW='\x1b[38;5;221m'; MAGENTA='\x1b[38;5;176m'; RED='\x1b[38;5;203m'; WHITE='\x1b[38;5;252m'; GRAY='\x1b[38;5;244m'
CLEAR='\x1b[2J\x1b[H'; HIDE='\x1b[?25l'; SHOW='\x1b[?25h'

@dataclass
class Entry:
    path: Path
    name: str
    is_dir: bool
    is_link: bool
    size: int
    mtime: float
    mode: int

    @property
    def executable(self) -> bool:
        return bool(self.mode & stat.S_IXUSR) and not self.is_dir


def human_size(n:int)->str:
    units=['B','K','M','G','T']
    v=float(n)
    for unit in units:
        if v < 1024 or unit == units[-1]:
            return f'{int(v)}{unit}' if unit=='B' or v>=10 else f'{v:.1f}{unit}'
        v/=1024
    return f'{n}B'


def age_text(ts:float)->str:
    dt=datetime.fromtimestamp(ts); now=datetime.now(); delta=now-dt
    if delta < timedelta(days=1) and dt.date()==now.date():
        return dt.strftime('%H:%M')
    if delta < timedelta(days=7):
        return dt.strftime('%a %H:%M')
    if dt.year==now.year:
        return dt.strftime('%b %d')
    return dt.strftime('%Y-%m-%d')


def read_entries(target:Path, hidden:bool=True, quiet:bool=False)->list[Entry]:
    out=[]
    try:
        items=list(target.iterdir())
    except OSError as e:
        if quiet:
            return []
        print(f'look: {e}', file=sys.stderr); raise SystemExit(1)
    for p in items:
        if not hidden and p.name.startswith('.'):
            continue
        try:
            s=p.lstat()
        except OSError:
            continue
        out.append(Entry(p,p.name,p.is_dir(),p.is_symlink(),s.st_size,s.st_mtime,s.st_mode))
    return out


def color_for(e:Entry)->str:
    if e.is_dir: return BLUE+BOLD
    if e.is_link: return CYAN
    if e.executable: return GREEN+BOLD
    ext=e.path.suffix.lower()
    if ext in {'.py','.js','.ts','.jsx','.tsx','.sh','.zsh','.rb','.go','.rs','.c','.cpp','.h'}: return GREEN
    if ext in {'.md','.txt','.rtf','.pdf','.doc','.docx'}: return WHITE
    if ext in {'.jpg','.jpeg','.png','.gif','.webp','.svg','.heic'}: return MAGENTA
    if ext in {'.mp3','.wav','.flac','.m4a','.aiff','.mp4','.mov','.mkv'}: return YELLOW
    if ext in {'.zip','.gz','.tar','.7z','.dmg','.pkg'}: return RED
    return WHITE


def marker(e:Entry)->str:
    # Deliberately use normal Unicode, never private-use Nerd Font codepoints.
    if e.is_dir: return '◆'
    if e.is_link: return '↗'
    if e.executable: return '▸'
    return '·'


def strip_ansi(s:str)->str:
    import re
    return re.sub(r'\x1b\[[0-9;?]*[ -/]*[@-~]', '', s)


def fit(s:str,width:int)->str:
    raw=strip_ansi(s)
    if len(raw)<=width: return s
    keep=max(1,width-1)
    # Most content lines have color only at the beginning and RESET at the end.
    if s.startswith('\x1b['):
        # crude but safe: preserve prefix through final m
        end=s.find('m')+1
        prefix=s[:end]; body=strip_ansi(s)
        return prefix+body[:keep]+'…'+RESET
    return raw[:keep]+'…'


def column_grid(entries:list[Entry], width:int, highlight_path:Path|None=None)->list[str]:
    if not entries: return []
    labels=[]
    for e in entries:
        suffix='/' if e.is_dir else ''
        labels.append((e, f'{marker(e)} {e.name}{suffix}'))
    maxw=min(max(len(t) for _,t in labels)+3, 38)
    cols=max(1,width//maxw)
    cellw=max(1,width//cols)
    rows=[]
    for start in range(0,len(labels),cols):
        pieces=[]
        for e,text in labels[start:start+cols]:
            plain=text
            if len(plain)>cellw-2:
                plain=plain[:max(1,cellw-3)]+'…'
            padding=' ' * max(1,cellw-len(plain))
            style=REVERSE if highlight_path is not None and e.path==highlight_path else color_for(e)
            pieces.append(style+plain+RESET+padding)
        rows.append(''.join(pieces).rstrip())
    return rows


def detail_rows(entries:list[Entry], width:int)->list[str]:
    rows=[]
    for e in entries:
        suffix='/' if e.is_dir else ''
        left=f'{marker(e)} {e.name}{suffix}'
        size='—' if e.is_dir else human_size(e.size)
        when=age_text(e.mtime)
        right=f'{size:>7}  {when:>10}'
        avail=max(10,width-len(right)-3)
        if len(left)>avail: left=left[:max(1,avail-1)]+'…'
        rows.append(f'{color_for(e)}{left:<{avail}}{RESET} {GRAY}{right}{RESET}')
    return rows


def query_matches(name:str, query:str)->bool:
    """AND-match whitespace-separated terms anywhere in a name."""
    terms=query.casefold().split()
    folded=name.casefold()
    return all(term in folded for term in terms)


def tree_rows(target:Path, depth:int, width:int, hidden:bool, query:str='', highlight_path:Path|None=None)->list[str]:
    rows=[]

    def collect(path:Path,prefix:str,level:int)->tuple[list[str], bool]:
        # Protected macOS folders are normal. Tree views silently skip anything
        # the current user cannot inspect instead of flooding stderr.
        kids=sorted(read_entries(path,hidden,quiet=True),key=lambda e:(not e.is_dir,e.name.lower()))
        rendered=[]
        any_match=False
        for i,e in enumerate(kids):
            child_prefix=prefix+('   ' if i==len(kids)-1 else '│  ')
            descendants=[]
            descendant_match=False
            if e.is_dir and level<depth:
                descendants,descendant_match=collect(e.path,child_prefix,level+1)

            self_match=not query or query_matches(e.name,query)
            include=self_match or descendant_match
            if not include:
                continue

            branch='└─' if i==len(kids)-1 else '├─'
            line=f'{prefix}{branch} {marker(e)} {e.name}{"/" if e.is_dir else ""}'
            style=REVERSE if highlight_path is not None and e.path==highlight_path else color_for(e)
            rendered.append(style+fit(line,width)+RESET)
            rendered.extend(descendants)
            any_match=True
        return rendered,any_match

    rows,_=collect(target,'',1)
    return rows


def build_view(target:Path, mode:str, hidden:bool, width:int, tree_depth:int, query:str='', highlight_path:Path|None=None)->list[str]:
    entries=read_entries(target,hidden)
    if query:
        entries=[e for e in entries if query_matches(e.name,query)]
    dirs=sorted((e for e in entries if e.is_dir),key=lambda e:e.name.lower())
    files=sorted((e for e in entries if not e.is_dir),key=lambda e:e.name.lower())

    # A filtered tree searches recursively. Its header should count the same
    # actual matches the user can select, not only matching top-level entries.
    if mode=='tree' and query:
        tree_matches=matching_paths(target,'tree',hidden,query,tree_depth)
        tree_dir_count=sum(1 for path in tree_matches if path.is_dir())
        tree_file_count=len(tree_matches)-tree_dir_count
    else:
        tree_dir_count=len(dirs)
        tree_file_count=len(files)
    if mode=='dirs': entries=dirs
    elif mode=='files': entries=files
    elif mode=='recent': entries=sorted(entries,key=lambda e:e.mtime,reverse=True)
    elif mode=='size': entries=sorted(entries,key=lambda e:(e.is_dir,-e.size,e.name.lower()))
    else: entries=dirs+files

    try: display=str(target.resolve().relative_to(Path.home()))
    except ValueError: display=str(target.resolve())
    if not display.startswith('/'): display='~/'+display if display!='.' else '~'
    header=f'{BOLD}{CYAN}LOOK{RESET} {DIM}{display}{RESET}  {GRAY}· {tree_dir_count} dirs · {tree_file_count} files{RESET}'
    rule=DIM+('─'*min(width, max(20,len(strip_ansi(header)))))+RESET
    rows=[header,rule]
    if mode=='tree':
        rows+=tree_rows(target,tree_depth,width,hidden,query,highlight_path)
    elif mode in {'detail','recent','size'}:
        rows+=detail_rows(entries,width)
    else:
        # Smart mode: small sets get labeled sections; larger sets become one compact grouped grid.
        if mode=='smart' and len(entries)<=18:
            if dirs:
                rows += [f'{DIM}folders{RESET}'] + column_grid(dirs,width,highlight_path)
            if dirs and files: rows.append('')
            if files:
                rows += [f'{DIM}files{RESET}'] + column_grid(files,width,highlight_path)
        else:
            rows += column_grid(entries,width,highlight_path)
    if len(rows)==2: rows.append(DIM+'(empty)'+RESET)
    return rows


def read_key(timeout:float|None=None)->str:
    fd=sys.stdin.fileno(); old=termios.tcgetattr(fd)
    try:
        # cbreak gives us immediate keystrokes without changing terminal output
        # processing. A short readiness check distinguishes bare Esc from an
        # arrow/PageUp/PageDown escape sequence.
        tty.setcbreak(fd)
        if timeout is not None:
            ready,_,_=select.select([fd],[],[],timeout)
            if not ready:
                return ''
        ch=os.read(fd,1)
        if ch==b'\x1b':
            seq=bytearray(ch)
            while len(seq)<6:
                ready,_,_=select.select([fd],[],[],0.025)
                if not ready:
                    break
                seq.extend(os.read(fd,1))
                if seq[-1:] in b'~ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
                    break
            return bytes(seq).decode('latin1')
        return ch.decode('utf-8','ignore')
    finally:
        termios.tcsetattr(fd,termios.TCSADRAIN,old)


def matching_paths(target:Path, mode:str, hidden:bool, query:str='', tree_depth:int=2)->list[Path]:

    if mode=='tree':
        matches=[]
        def walk(path:Path,level:int)->None:
            entries=sorted(read_entries(path,hidden,quiet=True),key=lambda e:(not e.is_dir,e.name.lower()))
            for e in entries:
                if not query or query_matches(e.name,query):
                    matches.append(e.path)
                if e.is_dir and level<tree_depth:
                    walk(e.path,level+1)
        walk(target,1)
        return matches

    entries=read_entries(target,hidden)
    if query:
        entries=[e for e in entries if query_matches(e.name,query)]
    dirs=sorted((e for e in entries if e.is_dir),key=lambda e:e.name.lower())
    files=sorted((e for e in entries if not e.is_dir),key=lambda e:e.name.lower())
    if mode=='dirs': entries=dirs
    elif mode=='files': entries=files
    elif mode=='recent': entries=sorted(entries,key=lambda e:e.mtime,reverse=True)
    elif mode=='size': entries=sorted(entries,key=lambda e:(e.is_dir,-e.size,e.name.lower()))
    else: entries=dirs+files
    return [e.path for e in entries]



def preview_rows(path:Path, width:int, height:int)->list[str]:
    """Small, dependency-light preview for selection mode."""
    width=max(20,width)
    height=max(3,height)
    title=f'{BOLD}{CYAN}{path.name}{RESET}'
    rows=[fit(title,width)]

    try:
        st=path.stat()
    except OSError as exc:
        return rows+[fit(f'{DIM}{exc}{RESET}',width)]

    if path.is_dir():
        rows.append(f'{DIM}folder{RESET}')
        try:
            kids=sorted(path.iterdir(), key=lambda q:(not q.is_dir(),q.name.casefold()))
            for child in kids[:max(1,height-2)]:
                mark='◆' if child.is_dir() else '·'
                rows.append(fit(f'{mark} {child.name}{"/" if child.is_dir() else ""}',width))
            if len(kids)>height-2:
                rows.append(f'{DIM}… {len(kids)-(height-2)} more{RESET}')
        except OSError as exc:
            rows.append(f'{DIM}{exc}{RESET}')
        return rows[:height]

    # Prefer actual text when the file looks textual. Avoid dumping binary bytes.
    try:
        sample=path.read_bytes()[:65536]
    except OSError as exc:
        return rows+[fit(f'{DIM}{exc}{RESET}',width)]

    textual=(b'\x00' not in sample)
    if textual:
        try:
            text=sample.decode('utf-8')
        except UnicodeDecodeError:
            try: text=sample.decode('latin1')
            except Exception: text=''
        if text:
            rows.append(f'{DIM}{human_size(st.st_size)} · text{RESET}')
            for line in text.expandtabs(4).splitlines():
                rows.append(fit(line,width))
                if len(rows)>=height: break
            return rows[:height]

    # For PDFs/images/other binaries, show useful type metadata without requiring
    # a terminal-specific image protocol. pdftotext is used opportunistically.
    suffix=path.suffix.casefold()
    if suffix=='.pdf' and shutil.which('pdftotext'):
        try:
            proc=subprocess.run(['pdftotext','-f','1','-l','1',str(path),'-'],
                                capture_output=True,text=True,timeout=2)
            text=proc.stdout.strip()
            if text:
                rows.append(f'{DIM}{human_size(st.st_size)} · PDF · page 1 text{RESET}')
                for line in text.splitlines():
                    rows.append(fit(line,width))
                    if len(rows)>=height: break
                return rows[:height]
        except (OSError,subprocess.SubprocessError):
            pass

    kind=suffix[1:].upper() if suffix else 'binary file'
    if shutil.which('file'):
        try:
            proc=subprocess.run(['file','-b',str(path)],capture_output=True,text=True,timeout=1)
            if proc.stdout.strip(): kind=proc.stdout.strip()
        except (OSError,subprocess.SubprocessError):
            pass
    rows.append(f'{DIM}{human_size(st.st_size)}{RESET}')
    for line in kind.splitlines(): rows.append(fit(line,width))
    return rows[:height]

def open_default(path:Path)->tuple[bool,str]:
    """Ask the OS to open a file, returning a short user-facing failure."""
    try:
        if sys.platform=='darwin':
            proc=subprocess.run(['open',str(path)],capture_output=True,text=True)
            if proc.returncode:
                ext=path.suffix or 'this file type'
                return False, f'no application is registered to open {ext}'
        elif os.name=='nt':
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            proc=subprocess.run(['xdg-open',str(path)],capture_output=True,text=True)
            if proc.returncode:
                return False, f'no application could open {path.suffix or "this file type"}'
        return True,''
    except (OSError,FileNotFoundError):
        return False,'system opener unavailable'


def edit_path(path:Path)->None:
    editor=os.environ.get('EDITOR') or ('nvim' if shutil.which('nvim') else 'vi')
    try: subprocess.call([editor,str(path)])
    except OSError as e: print(f'look: cannot edit {path}: {e}',file=sys.stderr)


def open_with(path:Path)->tuple[bool,str]:
    """Choose an application for a file without changing the system default."""
    if path.is_dir():
        return False,'folders are browsed with Enter'
    if not shutil.which('fzf'):
        return False,'open-with requires fzf'
    try:
        if sys.platform=='darwin':
            roots=[Path('/Applications'),Path('/System/Applications'),Path.home()/'Applications']
            apps=[]
            seen=set()
            for root in roots:
                if not root.is_dir():
                    continue
                for app in sorted(root.glob('*.app')):
                    name=app.stem
                    if name.casefold() in seen:
                        continue
                    seen.add(name.casefold()); apps.append((name,app))
            if not apps:
                return False,'no applications found'
            proc=subprocess.run(
                ['fzf','--prompt','open with › ','--height','40%','--reverse','--border'],
                input='\n'.join(name for name,_ in apps),text=True,capture_output=True)
            choice=proc.stdout.strip()
            if proc.returncode or not choice:
                return False,'open-with cancelled'
            app_path=next((app for name,app in apps if name==choice),None)
            if not app_path:
                return False,'application not found'
            launch=subprocess.run(['open','-a',str(app_path),str(path)],capture_output=True,text=True)
            return (True,'') if launch.returncode==0 else (False,f'could not open with {choice}')

        # Linux: use desktop MIME handlers when gio is available.
        if shutil.which('xdg-mime') and shutil.which('gio'):
            mime=subprocess.run(['xdg-mime','query','filetype',str(path)],capture_output=True,text=True).stdout.strip()
            if not mime:
                return False,'file type is unknown'
            roots=[Path.home()/'.local/share/applications',Path('/usr/local/share/applications'),Path('/usr/share/applications')]
            handlers=[]
            seen=set()
            for root in roots:
                if not root.is_dir():
                    continue
                for desktop in root.glob('*.desktop'):
                    try:
                        text=desktop.read_text(errors='ignore')
                    except OSError:
                        continue
                    if f'{mime};' not in text and f'MimeType={mime}' not in text:
                        continue
                    name=desktop.stem
                    for line in text.splitlines():
                        if line.startswith('Name='):
                            name=line[5:].strip() or name; break
                    key=(name.casefold(),str(desktop))
                    if key in seen:
                        continue
                    seen.add(key); handlers.append((name,desktop))
            if not handlers:
                return False,'no alternate application found for this file type'
            proc=subprocess.run(
                ['fzf','--prompt','open with › ','--height','40%','--reverse','--border'],
                input='\n'.join(name for name,_ in handlers),text=True,capture_output=True)
            choice=proc.stdout.strip()
            if proc.returncode or not choice:
                return False,'open-with cancelled'
            desktop=next((d for name,d in handlers if name==choice),None)
            if not desktop:
                return False,'application not found'
            launch=subprocess.run(['gio','launch',str(desktop),str(path)],capture_output=True,text=True)
            return (True,'') if launch.returncode==0 else (False,f'could not open with {choice}')
        return False,'open-with is unavailable on this system'
    except (OSError,subprocess.SubprocessError):
        return False,'open-with failed'


def copy_path(path:Path)->bool:
    value=str(path.resolve())
    try:
        if sys.platform=='darwin': subprocess.run(['pbcopy'],input=value,text=True,check=True)
        elif shutil.which('wl-copy'): subprocess.run(['wl-copy'],input=value,text=True,check=True)
        elif shutil.which('xclip'): subprocess.run(['xclip','-selection','clipboard'],input=value,text=True,check=True)
        else: return False
        return True
    except (OSError,subprocess.CalledProcessError): return False


def pager(rows:list[str],height:int,width:int,rebuild=None,candidates=None,on_browse=None,on_back=None,force_interactive=False)->None:
    # Interactive state machine: browse -> filter -> select.
    usable=max(3,height-2)
    if (len(rows)<=height-1 and not force_interactive) or not (sys.stdin.isatty() and sys.stdout.isatty()):
        print('\n'.join(rows)); return
    top=0; query=''; filtering=False; selecting=False; selected=0
    current=rows
    matches:list[Path]=[]
    notice=''
    pending=''

    def refresh_filter()->None:
        nonlocal current,top,matches,selected
        current=rebuild(query) if rebuild else rows
        matches=candidates(query) if candidates else []
        selected=min(selected,max(0,len(matches)-1))
        top=0

    def selected_path()->Path|None:
        return matches[selected] if matches and 0<=selected<len(matches) else None

    try:
        sys.stdout.write(HIDE)
        while True:
            picked=selected_path()
            if filtering and rebuild:
                # Side previews consume terminal width. Reflow the grid to the
                # visible list pane so highlighted matches cannot live beneath
                # the preview in an off-screen column.
                render_width=max(38,int(width*0.58)) if picked and width>=96 else width
                current=rebuild(query, picked, render_width)
            page=current[top:top+usable]
            sys.stdout.write(CLEAR)
            if (selecting or filtering) and picked:
                if width>=96:
                    left_w=max(38,int(width*0.58))
                    right_w=max(28,width-left_w-3)
                    left=[fit(r,left_w) for r in page]
                    right=preview_rows(picked,right_w,usable)
                    rendered=[]
                    for i in range(max(len(left),len(right))):
                        l=left[i] if i<len(left) else ''
                        r=right[i] if i<len(right) else ''
                        pad=max(0,left_w-len(strip_ansi(l)))
                        rendered.append(l+' '*pad+' │ '+r)
                    sys.stdout.write('\n'.join(rendered[:usable]))
                else:
                    preview_h=max(4,usable//3)
                    list_h=max(3,usable-preview_h-1)
                    rendered=[fit(r,width) for r in page[:list_h]]
                    rendered.append(DIM+('─'*width)+RESET)
                    rendered.extend(preview_rows(picked,width,preview_h))
                    sys.stdout.write('\n'.join(rendered[:usable]))
            else:
                sys.stdout.write('\n'.join(fit(r,width) for r in page))
            last=min(len(current),top+usable)
            if filtering:
                match_word='match' if len(matches)==1 else 'matches'
                status=(f'{CYAN}  filter: {query}█{RESET}  {GRAY}{len(matches)} {match_word}{RESET}  '
                        f'{DIM}↑/↓ choose · Enter open · E edit · O with · Y copy · P path · Esc clear{RESET}')
            elif selecting:
                name=picked.name if picked else '(no matches)'
                kind='folder' if picked and picked.is_dir() else 'file'
                status=(f'{CYAN}  ▶ {name}{RESET} {GRAY}· {kind}{RESET}  '
                        f'{DIM}j/k choose · Enter open · E edit · O with · Y copy · P path · Esc filter · q quit{RESET}')
            elif query:
                status=f'{CYAN}  filter: {query}{RESET}  {DIM}{last}/{len(current)} · Enter select · / edit · Esc clear · q quit{RESET}'
            else:
                status=f'{DIM}  {last}/{len(current)}  Enter filter · space/pgdn next · b/pgup page · g/G ends' + (f' · Esc back' if on_back else '') + f' · q quit{RESET}'
            if notice:
                status=f'{status}  {YELLOW}{notice}{RESET}'
                notice=''
            sys.stdout.write('\n'+fit(status,width)); sys.stdout.flush()
            if pending:
                key,pending=pending,''
            else:
                key=read_key()

            if filtering:
                if key in {'\r','\n'}:
                    picked=selected_path()
                    if picked:
                        if picked.is_dir() and on_browse:
                            on_browse(picked); return
                        opened,message=open_default(picked)
                        if opened:
                            break
                        notice=message
                    continue
                elif key in {'\x1b[B'} and matches:
                    selected=min(len(matches)-1,selected+1)
                    top=min(max(0,len(current)-usable),top+1)
                elif key in {'\x1b[A'} and matches:
                    selected=max(0,selected-1)
                    top=max(0,top-1)
                elif key=='\x1b[6~' and matches:
                    selected=min(len(matches)-1,selected+usable)
                    top=min(max(0,len(current)-usable),top+usable)
                elif key=='\x1b[5~' and matches:
                    selected=max(0,selected-usable)
                    top=max(0,top-usable)
                elif key=='\x1b':
                    query=''; filtering=False; selecting=False; refresh_filter()
                elif key.startswith('\x1b['):
                    # Ignore other terminal escape sequences without leaving filter mode.
                    pass
                elif key=='E' and matches:
                    picked=selected_path()
                    if picked and not picked.is_dir():
                        sys.stdout.write(SHOW+RESET+'\n'); sys.stdout.flush(); edit_path(picked); return
                    notice='folders are browsed with Enter'
                elif key=='O' and matches:
                    picked=selected_path()
                    if picked:
                        sys.stdout.write(SHOW+RESET+'\n'); sys.stdout.flush()
                        opened,message=open_with(picked)
                        sys.stdout.write(HIDE); sys.stdout.flush()
                        if not opened and message!='open-with cancelled': notice=message
                elif key=='Y' and matches:
                    picked=selected_path()
                    if picked: notice='copied' if copy_path(picked) else 'clipboard unavailable'
                elif key=='P' and matches:
                    picked=selected_path()
                    if picked:
                        sys.stdout.write(SHOW+RESET+'\n'+str(picked.resolve())+'\n'); sys.stdout.flush(); return
                elif key in {'\x7f','\b'}:
                    if query: query=query[:-1]; refresh_filter()
                elif key=='\x03': break
                elif len(key)==1 and key.isprintable():
                    # Debounce rapid typing: collect a short burst before rebuilding.
                    # LOOK still feels live, but large recursive filters no longer
                    # redraw once per character while the user is mid-word.
                    query+=key
                    while True:
                        nxt=read_key(0.055)
                        if not nxt:
                            break
                        if nxt in {'\x7f','\b'}:
                            if query: query=query[:-1]
                            continue
                        if len(nxt)==1 and nxt.isprintable():
                            query+=nxt
                            continue
                        # Preserve a non-text key for the next input cycle.
                        pending=nxt
                        break
                    refresh_filter()
                continue

            if selecting:
                if key in {'q','Q','\x03'}: break
                if key=='\x1b': selecting=False; filtering=True; continue
                if key.startswith('\x1b['): continue
                if key in {'j','\x1b[B'} and matches: selected=(selected+1)%len(matches); continue
                if key in {'k','\x1b[A'} and matches: selected=(selected-1)%len(matches); continue
                picked=selected_path()
                if not picked: continue
                if key in {'\r','\n'}:
                    if picked.is_dir() and on_browse:
                        on_browse(picked); return
                    opened,message=open_default(picked)
                    if opened:
                        break
                    notice=message
                    continue
                if key in {'e','E'}:
                    if picked.is_dir(): notice='folders are browsed with Enter'; continue
                    sys.stdout.write(SHOW+RESET+'\n'); sys.stdout.flush(); edit_path(picked); return
                if key in {'o','O'}:
                    sys.stdout.write(SHOW+RESET+'\n'); sys.stdout.flush()
                    opened,message=open_with(picked)
                    sys.stdout.write(HIDE); sys.stdout.flush()
                    if not opened and message!='open-with cancelled': notice=message
                    continue
                if key in {'y','Y'}: notice='copied' if copy_path(picked) else 'clipboard unavailable'; continue
                if key in {'p','P'}:
                    sys.stdout.write(SHOW+RESET+'\n'+str(picked.resolve())+'\n'); sys.stdout.flush(); return
                continue

            if key in {'q','Q','\x03'}: break
            if key in {'\r','\n','/'}: filtering=True
            elif key=='\x1b':
                if query:
                    query=''; selecting=False; refresh_filter()
                elif on_back:
                    on_back()
                    return
            elif key in {' ','\x1b[6~'}:
                if last>=len(current): break
                top=min(max(0,len(current)-usable),top+usable)
            elif key in {'b','\x1b[5~'}: top=max(0,top-usable)
            elif key in {'j','\x1b[B'}: top=min(max(0,len(current)-usable),top+1)
            elif key in {'k','\x1b[A'}: top=max(0,top-1)
            elif key=='g': top=0
            elif key=='G': top=max(0,len(current)-usable)
    finally:
        sys.stdout.write(SHOW+RESET+'\n'); sys.stdout.flush()

def main():
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('path',nargs='?',default='.')
    ap.add_argument('--mode',choices=['smart','detail','dirs','files','tree','recent','size'],default='smart')
    ap.add_argument('--depth',type=int,default=2)
    ap.add_argument('--no-hidden',action='store_true')
    ap.add_argument('--interactive',action='store_true')
    ap.add_argument('-h','--help',action='help')
    args=ap.parse_args()
    target=Path(os.path.expanduser(args.path))
    hidden=not args.no_hidden

    browsed_once=False
    history:list[Path]=[]
    while True:
        if not target.is_dir():
            print(f'look: not a directory: {target}',file=sys.stderr); return 1
        sz=shutil.get_terminal_size((100,30))
        rows=build_view(target,args.mode,hidden,sz.columns,args.depth)
        browsed:Path|None=None
        went_back=False
        def choose_dir(path:Path)->None:
            nonlocal browsed
            browsed=path
        def choose_back()->None:
            nonlocal went_back
            went_back=True
        pager(rows,sz.lines,sz.columns,
              rebuild=lambda q,h=None,w=None: build_view(target,args.mode,hidden,w or sz.columns,args.depth,q,h),
              candidates=lambda q: matching_paths(target,args.mode,hidden,q,args.depth),
              on_browse=choose_dir,
              on_back=choose_back if history else None,
              force_interactive=(args.interactive or browsed_once))
        if went_back:
            target=history.pop()
            browsed_once=True
            continue
        if browsed is None: return 0
        history.append(target)
        target=browsed
        browsed_once=True

if __name__=='__main__': raise SystemExit(main())
