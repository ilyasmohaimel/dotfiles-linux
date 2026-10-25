#!/usr/bin/env python3
"""Refresh the explicit desktop-config allowlist. Never commit or push automatically."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
SETUP = HOME / '.local/share/frost-hyprland-setup'
SKIP = {'__pycache__', '.git', 'node_modules', 'Cache', 'GPUCache'}
captured_payload = set()


def copy(source, destination):
    if not source.exists() and not source.is_symlink():
        raise FileNotFoundError(source)
    if source.is_symlink():
        target = os.readlink(source)
        if os.path.isabs(target):
            raise ValueError(f'Review absolute symlink before backup: {source}')
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_symlink() or destination.exists():
            destination.unlink()
        destination.symlink_to(target)
    elif source.is_dir():
        for child in sorted(source.iterdir()):
            if child.name not in SKIP and child.suffix not in {'.pyc', '.log'}:
                copy(child, destination / child.name)
        return
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    if destination.is_relative_to(ROOT/'home') or destination.is_relative_to(ROOT/'system'):
        captured_payload.add(destination)


def home(relative):
    copy(HOME / relative, ROOT / 'home' / relative)


def output(args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


for relative in [
    '.config/caelestia', '.config/hypr', '.config/quickshell/caelestia',
    '.config/frost-hyprland', '.config/wezterm', '.config/foot',
    '.config/fastfetch', '.config/starship', '.config/starship.toml',
    '.config/fish/config.fish', '.bashrc', '.bash_profile',
    '.config/lookfrost/active-activity', '.config/lookfrost/terminal-themes',
    '.config/xdg-desktop-portal/hyprland-portals.conf',
    '.config/micro/settings.json', '.config/Thunar/uca.xml',
    '.config/safeeyes/safeeyes.json', '.config/spicetify/config-xpui.ini',
    '.config/spicetify/Themes/caelestia',
    '.config/gtk-3.0/settings.ini', '.config/gtk-4.0/settings.ini',
    '.local/state/caelestia/scheme.json', '.local/state/caelestia/theme/foot-colors.ini',
    '.local/state/caelestia/wallpaper/path.txt',
    '.local/libexec/frost-hyprland/gpu.py', '.local/libexec/frost_usb_charge.py',
]:
    home(relative)

for name in [
    'frost-hyprland-session', 'frost-hyprland-autostart', 'frost-hyprland-gpu',
    'frost-theme-hook', 'frost-browser-colors', 'frost-clipboard-paste',
    'caelestia-foot-colors', 'caelestia-foot-shell', 'caelestia-safeeyes',
    'caelestia-spotify', 'brave', 'lookfrost-prepare-brave-theme', 'fastfetch',
]:
    home('.local/bin/' + name)

for name in ['frost-hyprland-session.target', 'frost-usb-charge-profile.service',
             'caelestia-spicetify.service', 'frost-disable-sleep-keys.service']:
    home('.config/systemd/user/' + name)

home('.config/systemd/user/default.target.wants/frost-disable-sleep-keys.service')

for name in ['hiddify.desktop', 'net.blip.Blip.desktop',
             'io.github.slgobinath.SafeEyes.desktop',
             'org.opengamingcollective.rog-control-center.desktop']:
    home('.config/autostart/' + name)

for name in ['brave-browser.desktop', 'spotify.desktop', 'spotify-adblock.desktop']:
    home('.local/share/applications/' + name)

for path in [
    '/usr/local/libexec/frost_power.py', '/usr/local/libexec/frost-brave-theme',
    '/usr/local/libexec/frost-gpu-app', '/usr/local/libexec/frost_app.py',
    '/usr/local/libexec/frost_session.py',
    '/usr/share/wayland-sessions/hyprland-caelestia.desktop',
    '/usr/share/wayland-sessions/hyprland-caelestia-igpu.desktop',
    '/usr/share/wayland-sessions/hyprland-caelestia-rx.desktop',
    '/etc/brave/policies/managed/caelestia.json',
    '/usr/lib/firefox/distribution/policies.json',
]:
    copy(Path(path), ROOT / 'system' / path.lstrip('/'))

# The live sudoers rule is root-readable. Keep the reviewed installation source,
# clearly separate from verified copies of live system files.
copy(SETUP/'frost-brave-theme.sudoers', ROOT/'reference/frost-brave-theme.sudoers')

for image in sorted((HOME/'Pictures/Wallpapers/Caelestia').iterdir()):
    if image.is_file() and image.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}:
        copy(image, ROOT.parent/'Wallpapers/Caelestia'/image.name)

for image in sorted((SETUP/'output/shortcuts').glob('Frost-shortcuts-page-*.png')):
    copy(image, ROOT/'docs/shortcuts'/image.name)
copy(SETUP/'output/shortcuts/Frost-Hyprland-shortcuts.pdf', ROOT/'docs/shortcuts/Frost-Hyprland-shortcuts.pdf')
copy(SETUP/'create-shortcuts-sheet.py', ROOT/'reference/create-shortcuts-sheet.py')
for name in ['wallpaper-downloads.json', 'firefox-addon-release.json']:
    copy(SETUP/name, ROOT/'reference'/name)

manifests = ROOT/'manifests'
manifests.mkdir(exist_ok=True)
upstream = {}
urls = {
    'dots': 'https://github.com/caelestia-dots/caelestia.git',
    'shell': 'https://github.com/caelestia-dots/shell.git',
    'cli': 'https://github.com/caelestia-dots/cli.git',
    'quickshell': 'https://git.outfoxxed.me/quickshell/quickshell.git',
    'm3shapes': 'https://github.com/soramanew/m3shapes.git',
    'spicetify': 'https://github.com/spicetify/cli.git',
}
for name, url in urls.items():
    repo = SETUP/'sources'/name
    upstream[name] = {'url': url, 'commit': output(['git','rev-parse','HEAD'],repo)}
    patch = output(['git','diff','--binary','HEAD'], repo)
    if patch:
        target = ROOT/'build/patches'/f'{name}.patch'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(patch+'\n')
    for path in output(['git','ls-files','--others','--exclude-standard'],repo).splitlines():
        if path:
            copy(repo/path, ROOT/'build/overlays'/name/path)
    license_path = repo/'LICENSE'
    if license_path.is_file():
        copy(license_path, ROOT/'licenses'/f'{name}-LICENSE')
(manifests/'upstream.json').write_text(json.dumps(upstream,indent=2)+'\n')

for recipe in ['caelestia-shell-local', 'caelestia-cli-local', 'quickshell-local',
               'qt6-m3shapes-git', 'libcava', 'python-materialyoucolor', 'ttf-rubik-vf']:
    copy(SETUP/'aur'/recipe/'PKGBUILD',ROOT/'build/recipes'/recipe/'PKGBUILD')

# Package inventories are references, never an automatic driver/install list.
for kind, flags in [('pacman-native.txt',['-Qqn']),('pacman-foreign.txt',['-Qqm']),
                    ('package-versions.txt',['-Q'])]:
    (manifests/kind).write_text(output(['pacman',*flags])+'\n')

# Only these two trees are collector-owned; never retain deleted upstream files
# as if they still belonged to the current snapshot.
for area in ['home','system']:
    for path in (ROOT/area).rglob('*'):
        if (path.is_file() or path.is_symlink()) and path not in captured_payload:
            path.unlink()

entries=[]
for area in ['home','system']:
    for p in sorted((ROOT/area).rglob('*')):
        if p.is_symlink():
            entries.append({'path':str(p.relative_to(ROOT)),'symlink':os.readlink(p)})
        elif p.is_file():
            entries.append({'path':str(p.relative_to(ROOT)),
                            'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                            'mode':oct(p.stat().st_mode & 0o777)})
(manifests/'files.json').write_text(json.dumps(entries,indent=2)+'\n')
(manifests/'snapshot.json').write_text(json.dumps({
    'captured_at':datetime.now(timezone.utc).isoformat(),
    'source_home':str(HOME), 'desktop':'Hyprland / Caelestia',
    'hardware':'ASUS ROG G513QY; Ryzen 9 5900HX; Radeon RX 6800M + integrated Radeon',
    'file_count':len(entries),
    'scope':'Explicit desktop configuration and support scripts; no accounts, VPN profiles, histories, or browser data',
},indent=2)+'\n')
print(f'Captured {len(entries)} home/system files and symlinks. Review the diff and scan before publishing.')
