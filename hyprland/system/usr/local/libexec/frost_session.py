#!/usr/bin/env python3
"""Opt-in Plasma session dispatch; ordinary Plasma always uses stock binaries."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

PREFIX = Path('/opt/frost-gpu')
DISPATCH = '/usr/local/libexec/frost-gpu-dispatch'
import importlib.util as _power_import
_power_spec = _power_import.spec_from_file_location('frost_power', Path(__file__).with_name('frost_power.py'))
_power_module = _power_import.module_from_spec(_power_spec)
_power_spec.loader.exec_module(_power_module)
power_source = _power_module.power_source

RX = '0000:03:00.0'
IGPU = '0000:07:00.0'
FLAG = 'FROST_GPU_LIVE_SESSION'


def runtime(env):
    return Path(env.get('XDG_RUNTIME_DIR', '/run/user/' + str(os.getuid()))) / 'frost-gpu-live'


def ac_online():
    # Compatibility name: true means barrel-performance power, not any charger.
    return power_source()['useRX']


def compatible(prefix=PREFIX):
    try:
        manifest = json.loads((prefix/'share/manifest.json').read_text())
        for package, version in manifest['packages'].items():
            actual = subprocess.check_output(['/usr/bin/pacman', '-Q', package], text=True, stderr=subprocess.DEVNULL).strip().split(maxsplit=1)[1]
            if actual != version:
                return False
        return all((prefix/part).is_file() for part in ('kwin/bin/kwin_wayland', 'kwin/bin/kwin_wayland_wrapper', 'bin/zss-run', 'bin/zssd', 'lib/libzss_airlock.so','kwin/lib/libkwin.so.6','kwin/lib/libexec/plasma-setup-xwayland'))
    except (OSError, ValueError, KeyError, IndexError, subprocess.CalledProcessError):
        return False


def opted_in(env):
    config = Path(env.get('XDG_CONFIG_HOME', str(Path.home()/'.config')))
    sid=env.get('XDG_SESSION_ID')
    try: same_login=bool(sid) and env.get('FROST_GPU_LIVE_SESSION_ID')==sid and (runtime(env)/'login-session').read_text().strip()==sid
    except OSError: same_login=False
    return env.get(FLAG) == '1' and same_login and not (config/'frost-gpu-live/disabled').exists() and not (runtime(env)/'fallback').exists()


def mark_login(env):
    sid=env.get('XDG_SESSION_ID','')
    if not sid or not sid.isalnum():raise RuntimeError('A logind login session is required')
    directory=runtime(env)
    directory.mkdir(mode=0o700,parents=True,exist_ok=True)
    marker=directory/'login-session'
    fd=os.open(marker,os.O_CREAT|os.O_TRUNC|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream:stream.write(sid+'\n')
    env['FROST_GPU_LIVE_SESSION_ID']=sid


def clean(env):
    """Remove our child-only backend settings before invoking a stock program."""
    env = dict(env)
    if env.pop('FROST_GPU_FIXED_IGPU', None)=='1':
        # Do not hide RX from another application launched by the iGPU-only app.
        env['MESA_VK_DEVICE_SELECT']='1002:1638'
        env['MESA_VK_DEVICE_SELECT_FORCE_DEFAULT_DEVICE']='0'
    for key in ('KWIN_ENABLE_EXPERIMENTAL_GPU_SWITCH', 'KWIN_XWAYLAND_RENDER_DEVICE', 'VK_DRIVER_FILES', 'VK_ICD_FILENAMES', 'ZSS_START_ON', 'ZSS_RETAIN', 'ZSS_REAL_DRIVER_FILES', 'ZSS_MANIFEST', 'QSG_RHI_BACKEND', 'MESA_LOADER_DRIVER_OVERRIDE', 'GALLIUM_DRIVER', '__GLX_VENDOR_LIBRARY_NAME', '__EGL_VENDOR_LIBRARY_FILENAMES', 'LIBGL_KOPPER_DRI2'):
        env.pop(key, None)
    for key in ('PATH', 'QT_PLUGIN_PATH', 'QML_IMPORT_PATH', 'QML2_IMPORT_PATH', 'XDG_DATA_DIRS'):
        if key in env:
            env[key] = ':'.join(p for p in env[key].split(':') if not p.startswith(str(PREFIX)) and p != DISPATCH)
            if not env[key]: env.pop(key)
    if env.get('FROST_GPU_WRAPPED')=='1':
        for key in ('GDK_BACKEND','QT_QPA_PLATFORM','QT_XCB_GL_INTEGRATION'):
            env.pop(key,None)
    previous=env.pop('FROST_GPU_WAYLAND_DISPLAY',None)
    if previous is not None:env['WAYLAND_DISPLAY']=previous
    env.pop('FROST_GPU_WRAPPED',None)
    return env


def session_environment(env, ac=None):
    env = clean(env)
    ac = ac_online() if ac is None else ac
    gpus = (RX, IGPU) if ac else (IGPU, RX)
    nodes = {gpu: os.path.realpath('/dev/dri/by-path/pci-'+gpu+'-render') for gpu in gpus}
    cards = {gpu: os.path.realpath('/dev/dri/by-path/pci-'+gpu+'-card') for gpu in gpus}
    if not all(Path(p).is_char_device() for p in (*nodes.values(), *cards.values())):
        raise RuntimeError('Both expected GPUs must be available')
    env.update({FLAG: '1', 'KWIN_ENABLE_EXPERIMENTAL_GPU_SWITCH': '1', 'KWIN_XWAYLAND_RENDER_DEVICE': nodes[IGPU],
                'KWIN_DRM_DEVICES': ':'.join(cards[g] for g in gpus), 'KWIN_RENDER_NODES': ':'.join(nodes[g] for g in (IGPU, RX)),
                'ZSS_SOCKET': str(runtime(env)/'render.sock'), 'FROST_SESSION_GPU': 'live'})
    # KWin picks its explicit-sync device from the first render node. Keep
    # syncobj ioctls on the panel GPU even when RX is the initial renderer;
    # otherwise every frame wakes RX after a later battery migration. The
    # initial renderer remains selected independently by KWIN_DRM_DEVICES.
    # Unwrapped graphics clients have no migration contract: keep their default
    # on the panel GPU. Our app dispatcher selects current power for each new
    # wrapped process. Never hide either device with a forced Vulkan filter.
    env['DRI_PRIME'] = 'pci-0000_07_00_0'
    # KDE imports retained manager variables back into the session. Present
    # safe values must overwrite the old login policy's forced filter.
    env['MESA_VK_DEVICE_SELECT'] = '1002:1638'
    env['MESA_VK_DEVICE_SELECT_FORCE_DEFAULT_DEVICE'] = '0'
    return env


def socket_ready(env, wait=0):
    end = time.monotonic()+wait
    while True:
        try:
            with socket.socket(socket.AF_UNIX) as connection:
                connection.settimeout(.3)
                connection.connect(env['ZSS_SOCKET'])
            return True
        except (OSError, KeyError):
            if time.monotonic() >= end: return False
            time.sleep(.1)


def fallback(env, reason):
    directory = runtime(env)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    (directory/'fallback').write_text(reason+'\n')
    print('Frost GPU: using stock renderer: '+reason, file=sys.stderr, flush=True)


def plan(mode, args, env, enabled=None, daemon_ready=None):
    """Return an argv/environment pair; kept separate for bounded routing tests."""
    active = opted_in(env) and compatible() if enabled is None else enabled
    if mode == 'kwin-wrapper':
        if active:
            env = dict(env)
            env['PATH'] = DISPATCH+':'+env.get('PATH', '/usr/bin')
            return [str(PREFIX/'kwin/bin/kwin_wayland_wrapper'), *args], env
        return ['/usr/bin/kwin_wayland_wrapper', *args], clean(env)
    if mode == 'kwin':
        if active and env.get('KWIN_RESTART_COUNT', '0') == '0':
            env = dict(env)
            env['QT_PLUGIN_PATH'] = str(PREFIX/'kwin/lib/plugins')+':'+env.get('QT_PLUGIN_PATH', '/usr/lib/qt6/plugins')
            return [str(PREFIX/'kwin/bin/kwin_wayland'), *args], env
        if active:
            fallback(env, 'custom KWin restarted after a crash')
        return ['/usr/bin/kwin_wayland', *args], clean(env)
    if mode == 'plasma':
        ready = socket_ready(env, 8) if active and daemon_ready is None else daemon_ready
        if active and ready:
            env = dict(env)
            env.update(QSG_RHI_BACKEND='vulkan', ZSS_START_ON=RX if ac_online() else IGPU, ZSS_RETAIN='ram', ZSS_REAL_DRIVER_FILES='/usr/share/vulkan/icd.d/radeon_icd.json')
            return [str(PREFIX/'bin/zss-run'), '/usr/bin/plasmashell', *args], env
        if active: fallback(env, 'session render daemon was unavailable before Plasma startup')
        return ['/usr/bin/plasmashell', *args], clean(env)
    raise ValueError(mode)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['session', 'kwin-wrapper', 'kwin', 'plasma', 'check'])
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    env = dict(os.environ)
    if args.mode == 'check':
        valid = compatible() and opted_in(env)
        print(json.dumps({'compatible': compatible(), 'optedIn': opted_in(env), 'fallback': (runtime(env)/'fallback').exists()})); return 0 if valid else 1
    if args.mode == 'session':
        directory = runtime(env)
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        # Remove only the state from our preceding login, never another
        # process's lock or socket. The display manager starts this once.
        (directory/'fallback').unlink(missing_ok=True)
        env[FLAG] = '1'
        try:
            mark_login(env)
        except RuntimeError as error:
            env[FLAG] = '0'
            print('Frost GPU: '+str(error),file=sys.stderr)
        if compatible() and opted_in(env):
            try:
                env = session_environment(env)
            except RuntimeError as error:
                env[FLAG] = '0'
                print('Frost GPU: '+str(error)+'; starting ordinary Plasma', file=sys.stderr)
        else:
            env[FLAG] = '0'
            print('Frost GPU: package versions changed or stack missing; starting ordinary Plasma', file=sys.stderr)
        os.execve('/usr/lib/plasma-dbus-run-session-if-needed', ['/usr/lib/plasma-dbus-run-session-if-needed', '/usr/bin/startplasma-wayland', *args.args], env)
    command, env = plan(args.mode, args.args, env)
    os.execve(command[0], command, env)


if __name__ == '__main__':
    raise SystemExit(main())
