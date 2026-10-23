#!/usr/bin/env python3
"""Verify the snapshot and preview home restoration; --apply explicitly writes files.

Existing files are backed up first. System files and package installation remain manual.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import uuid

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    entries = json.loads((ROOT/'manifests/files.json').read_text())
    names = set()
    for entry in entries:
        path = PurePosixPath(entry['path'])
        if path.is_absolute() or '..' in path.parts or path.parts[0] not in {'home','system'}:
            raise ValueError(f'Invalid manifest path: {path}')
        if str(path) in names:
            raise ValueError(f'Duplicate manifest entry: {path}')
        names.add(str(path))
        source = ROOT/path
        if 'symlink' in entry:
            if not source.is_symlink() or os.readlink(source) != entry['symlink']:
                raise ValueError(f'Symlink verification failed: {path}')
            if os.path.isabs(entry['symlink']) or not source.resolve().is_relative_to(ROOT/path.parts[0]):
                raise ValueError(f'Symlink leaves payload: {path}')
            if not source.exists():
                raise ValueError(f'Broken payload symlink: {path}')
        elif source.is_symlink() or not source.is_file() or digest(source) != entry['sha256']:
            raise ValueError(f'Checksum verification failed: {path}')
    actual = {str(p.relative_to(ROOT)) for area in ('home','system')
              for p in (ROOT/area).rglob('*') if p.is_file() or p.is_symlink()}
    if actual != names:
        raise ValueError(f'Payload/manifest mismatch: {sorted(actual ^ names)}')
    print(f'Verified {len(entries)} files and symlinks.')
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Verify only; no restore plan')
    parser.add_argument('--apply', action='store_true', help='Apply home files after making backups')
    parser.add_argument('--target-home', type=Path, default=Path.home(), help='Destination home; supports disposable rehearsal directories')
    args = parser.parse_args()
    if args.verify and args.apply:
        parser.error('--verify and --apply are mutually exclusive')
    entries = verify()
    if args.verify:
        return
    target = args.target_home.expanduser().absolute()
    if target.is_symlink() or target == Path('/'):
        raise ValueError('Target must be a real home directory, not / or a symlink')
    planned = []
    for entry in entries:
        if not entry['path'].startswith('home/'):
            continue
        relative = Path(entry['path']).relative_to('home')
        destination = target/relative
        for parent in destination.parents:
            if parent.is_symlink():
                raise ValueError(f'Review destination symlink before restoring: {parent}')
        if destination.exists() and destination.is_dir():
            raise ValueError(f'A directory blocks the destination file: {destination}')
        unchanged = (destination.is_symlink() and 'symlink' in entry and os.readlink(destination) == entry['symlink'])
        if 'sha256' in entry and destination.is_file() and not destination.is_symlink():
            unchanged = digest(destination) == entry['sha256'] and (destination.stat().st_mode & 0o777) == int(entry['mode'],8)
        if not unchanged:
            planned.append((entry,relative,destination))
    print(f'{len(planned)} home files would change beneath {target}. System files will not be applied.')
    if not args.apply:
        for _,relative,_ in planned:
            print(relative)
        print('Preview only. Use --apply after installing dependencies and reviewing machine-specific paths.')
        return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    backup = target/'.local/state/frost-dotfiles-restore'/stamp
    for parent in [backup, *backup.parents]:
        if parent.is_symlink():
            raise ValueError(f'Review backup destination symlink before restoring: {parent}')
    for entry,relative,destination in planned:
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists() or destination.is_symlink():
            saved = backup/relative
            saved.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(destination,saved,follow_symlinks=False)
        temporary = destination.with_name('.frost-restore-'+uuid.uuid4().hex)
        try:
            if 'symlink' in entry:
                temporary.symlink_to(entry['symlink'])
            else:
                # Create privately, then restore captured permissions after content is written.
                fd = os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
                with os.fdopen(fd,'wb') as stream:
                    stream.write((ROOT/entry['path']).read_bytes())
                temporary.chmod(int(entry['mode'],8))
            os.replace(temporary,destination)
        finally:
            temporary.unlink(missing_ok=True)
    print(f'Applied {len(planned)} home files. Existing changed files saved under {backup}.')
    print('No packages, services, system paths or compositor reloads were changed.')


if __name__ == '__main__':
    main()
