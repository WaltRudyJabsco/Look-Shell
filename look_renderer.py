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
import subprocess
import sys
import termios
import tty
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

RESET='\x1b[0m'; BOLD='\x1b[1m'; DIM='\x1b[2m'
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


def read_entries(target:Path, hidden:bool=True)->list[Entry]:
    out=[]
    try:
        items=list(target.iterdir())
    except OSError as e:
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


def column_grid(entries:list[Entry], width:int)->list[str]:
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
            pieces.append(color_for(e)+plain+RESET+padding)
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


def tree_rows(target:Path, depth:int, width:int, hidden:bool, query:str='')->list[str]:
    rows=[]
    def walk(path:Path,prefix:str,level:int):
        try: kids=read_entries(path,hidden)
        except SystemExit: return
        kids=sorted(kids,key=lambda e:(not e.is_dir,e.name.lower()))
        if query:
            needle=query.casefold()
            kids=[e for e in kids if e.name.casefold().startswith(needle)]
        for i,e in enumerate(kids):
            branch='└─' if i==len(kids)-1 else '├─'
            line=f'{prefix}{branch} {marker(e)} {e.name}{"/" if e.is_dir else ""}'
            rows.append(color_for(e)+fit(line,width)+RESET)
            if e.is_dir and level<depth:
                walk(e.path,prefix+('   ' if i==len(kids)-1 else '│  '),level+1)
    walk(target,'',1)
    return rows


def build_view(target:Path, mode:str, hidden:bool, width:int, tree_depth:int, query:str='')->list[str]:
    entries=read_entries(target,hidden)
    if query:
        needle=query.casefold()
        entries=[e for e in entries if e.name.casefold().startswith(needle)]
    dirs=sorted((e for e in entries if e.is_dir),key=lambda e:e.name.lower())
    files=sorted((e for e in entries if not e.is_dir),key=lambda e:e.name.lower())
    if mode=='dirs': entries=dirs
    elif mode=='files': entries=files
    elif mode=='recent': entries=sorted(entries,key=lambda e:e.mtime,reverse=True)
    elif mode=='size': entries=sorted(entries,key=lambda e:(e.is_dir,-e.size,e.name.lower()))
    else: entries=dirs+files

    try: display=str(target.resolve().relative_to(Path.home()))
    except ValueError: display=str(target.resolve())
    if not display.startswith('/'): display='~/'+display if display!='.' else '~'
    header=f'{BOLD}{CYAN}LOOK{RESET} {DIM}{display}{RESET}  {GRAY}· {len(dirs)} dirs · {len(files)} files{RESET}'
    rule=DIM+('─'*min(width, max(20,len(strip_ansi(header)))))+RESET
    rows=[header,rule]
    if mode=='tree':
        rows+=tree_rows(target,tree_depth,width,hidden,query)
    elif mode in {'detail','recent','size'}:
        rows+=detail_rows(entries,width)
    else:
        # Smart mode: small sets get labeled sections; larger sets become one compact grouped grid.
        if mode=='smart' and len(entries)<=18:
            if dirs:
                rows += [f'{DIM}folders{RESET}'] + column_grid(dirs,width)
            if dirs and files: rows.append('')
            if files:
                rows += [f'{DIM}files{RESET}'] + column_grid(files,width)
        else:
            rows += column_grid(entries,width)
    if len(rows)==2: rows.append(DIM+'(empty)'+RESET)
    return rows


def read_key()->str:
    fd=sys.stdin.fileno(); old=termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch=os.read(fd,1)
        if ch==b'\x1b':
            seq=ch+os.read(fd,2)
            return seq.decode('latin1')
        return ch.decode('utf-8','ignore')
    finally:
        termios.tcsetattr(fd,termios.TCSADRAIN,old)


def matching_paths(target:Path, mode:str, hidden:bool, query:str='')->list[Path]:
    entries=read_entries(target,hidden)
    if query:
        needle=query.casefold()
        entries=[e for e in entries if e.name.casefold().startswith(needle)]
    dirs=sorted((e for e in entries if e.is_dir),key=lambda e:e.name.lower())
    files=sorted((e for e in entries if not e.is_dir),key=lambda e:e.name.lower())
    if mode=='dirs': entries=dirs
    elif mode=='files': entries=files
    elif mode=='recent': entries=sorted(entries,key=lambda e:e.mtime,reverse=True)
    elif mode=='size': entries=sorted(entries,key=lambda e:(e.is_dir,-e.size,e.name.lower()))
    else: entries=dirs+files
    return [e.path for e in entries]


def open_default(path:Path)->None:
    try:
        if sys.platform=='darwin': subprocess.Popen(['open',str(path)])
        elif os.name=='nt': os.startfile(str(path))  # type: ignore[attr-defined]
        else: subprocess.Popen(['xdg-open',str(path)])
    except (OSError,FileNotFoundError) as e:
        print(f'look: cannot open {path}: {e}',file=sys.stderr)


def edit_path(path:Path)->None:
    editor=os.environ.get('EDITOR') or ('nvim' if shutil.which('nvim') else 'vi')
    try: subprocess.call([editor,str(path)])
    except OSError as e: print(f'look: cannot edit {path}: {e}',file=sys.stderr)


def copy_path(path:Path)->bool:
    value=str(path.resolve())
    try:
        if sys.platform=='darwin': subprocess.run(['pbcopy'],input=value,text=True,check=True)
        elif shutil.which('wl-copy'): subprocess.run(['wl-copy'],input=value,text=True,check=True)
        elif shutil.which('xclip'): subprocess.run(['xclip','-selection','clipboard'],input=value,text=True,check=True)
        else: return False
        return True
    except (OSError,subprocess.CalledProcessError): return False


def pager(rows:list[str],height:int,width:int,rebuild=None,candidates=None,on_browse=None)->None:
    # Interactive state machine: browse -> filter -> select.
    usable=max(3,height-2)
    if len(rows)<=height-1 or not (sys.stdin.isatty() and sys.stdout.isatty()):
        print('\n'.join(rows)); return
    top=0; query=''; filtering=False; selecting=False; selected=0
    current=rows
    matches:list[Path]=[]
    notice=''

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
            page=current[top:top+usable]
            sys.stdout.write(CLEAR)
            sys.stdout.write('\n'.join(fit(r,width) for r in page))
            last=min(len(current),top+usable)
            picked=selected_path()
            if filtering:
                status=f'{CYAN}  filter: {query}█{RESET}  {DIM}Enter select · Backspace edit · Esc clear{RESET}'
            elif selecting:
                name=picked.name if picked else '(no matches)'
                kind='folder' if picked and picked.is_dir() else 'file'
                status=(f'{CYAN}  ▶ {name}{RESET} {GRAY}· {kind}{RESET}  '
                        f'{DIM}j/k choose · Enter open · e edit · y copy · p path · Esc filter · q quit{RESET}')
            elif query:
                status=f'{CYAN}  filter: {query}{RESET}  {DIM}{last}/{len(current)} · Enter select · / edit · Esc clear · q quit{RESET}'
            else:
                status=f'{DIM}  {last}/{len(current)}  Enter filter · space/pgdn next · b/pgup back · g/G ends · q quit{RESET}'
            if notice:
                status=f'{status}  {YELLOW}{notice}{RESET}'
                notice=''
            sys.stdout.write('\n'+fit(status,width)); sys.stdout.flush()
            key=read_key()

            if filtering:
                if key in {'\r','\n'}:
                    filtering=False; selecting=True; refresh_filter()
                elif key=='\x1b' or key.startswith('\x1b['):
                    query=''; filtering=False; selecting=False; refresh_filter()
                elif key in {'\x7f','\b'}:
                    if query: query=query[:-1]; refresh_filter()
                elif key=='\x03': break
                elif len(key)==1 and key.isprintable(): query+=key; refresh_filter()
                continue

            if selecting:
                if key in {'q','Q','\x03'}: break
                if key=='\x1b' or key.startswith('\x1b['): selecting=False; filtering=True; continue
                if key in {'j','\x1b[B'} and matches: selected=(selected+1)%len(matches); continue
                if key in {'k','\x1b[A'} and matches: selected=(selected-1)%len(matches); continue
                picked=selected_path()
                if not picked: continue
                if key in {'\r','\n'}:
                    if picked.is_dir() and on_browse:
                        on_browse(picked); return
                    open_default(picked); break
                if key=='e':
                    sys.stdout.write(SHOW+RESET+'\n'); sys.stdout.flush(); edit_path(picked); return
                if key=='y': notice='copied' if copy_path(picked) else 'clipboard unavailable'; continue
                if key=='p':
                    sys.stdout.write(SHOW+RESET+'\n'+str(picked.resolve())+'\n'); sys.stdout.flush(); return
                continue

            if key in {'q','Q','\x03'}: break
            if key in {'\r','\n','/'}: filtering=True
            elif key=='\x1b':
                if query: query=''; selecting=False; refresh_filter()
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
    ap.add_argument('-h','--help',action='help')
    args=ap.parse_args()
    target=Path(os.path.expanduser(args.path))
    hidden=not args.no_hidden

    while True:
        if not target.is_dir():
            print(f'look: not a directory: {target}',file=sys.stderr); return 1
        sz=shutil.get_terminal_size((100,30))
        rows=build_view(target,args.mode,hidden,sz.columns,args.depth)
        browsed:Path|None=None
        def choose_dir(path:Path)->None:
            nonlocal browsed
            browsed=path
        pager(rows,sz.lines,sz.columns,
              rebuild=lambda q: build_view(target,args.mode,hidden,sz.columns,args.depth,q),
              candidates=lambda q: matching_paths(target,args.mode,hidden,q),
              on_browse=choose_dir)
        if browsed is None: return 0
        target=browsed

if __name__=='__main__': raise SystemExit(main())
