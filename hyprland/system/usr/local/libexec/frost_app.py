#!/usr/bin/env python3
"""Launch tested app routes in the opt-in GPU session, preserving original argv."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

_spec=importlib.util.spec_from_file_location('frost_session',Path(__file__).with_name('frost_session.py'))
session=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(session)
# Only routes with visible rendering coverage default to migration. Media,
# account, extension and document workflows still need their own validation.
ROUTES={
    'brave':'chromium', 'chromium':'chromium', 'codex':'chromium',
    't3':'chromium', 'codium':'chromium', 'bitwarden':'chromium',
    'wezterm':'wezterm', 'alacritty':'gl', 'redpanda':'raster', 'rog':'rog',
    'hiddify':'gl', 'wechat':'igpu-native', 'libreoffice':'office', 'firefox':'limited-gl',
    'vesktop':'limited-chromium', 'rootapp':'limited-gl', 'spotify':'limited-gl',
}
DEFAULT={'brave','chromium','codex','t3','codium','bitwarden','wezterm','alacritty','redpanda','hiddify','wechat','rog','libreoffice'}


def selected(profile, env):
    config=Path(env.get('XDG_CONFIG_HOME',str(Path.home()/'.config')))/'frost-gpu-live/apps.json'
    try:
        settings=json.loads(config.read_text())
        if isinstance(settings.get(profile),bool): return settings[profile]
    except (OSError,ValueError,AttributeError): pass
    return profile in DEFAULT


def unwrap_env(args, env):
    # Preserve existing per-app proxy assignments and other ordinary `env`
    # launchers, while letting zss-run inspect the actual application wrapper.
    args=list(args); env=dict(env)
    if args and args[0] in ('env','/usr/bin/env','/bin/env'):
        tail=args[1:]
        while tail and re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*=.*',tail[0],re.S):
            key,value=tail.pop(0).split('=',1);env[key]=value
        if not tail or tail[0].startswith('-'): return args,env,False
        args=tail
    return args,env,True


def render_on_rx(env):
    try:
        directory = Path(env.get('XDG_RUNTIME_DIR', '/run/user/' + str(os.getuid()))) / 'frost-gpu-live'
        data = json.loads((directory / 'mode.json').read_text())
        if data.get('session') == env.get('XDG_SESSION_ID'):
            if data.get('mode') in ('igpu', 'eco'):
                return False
            if data.get('mode') == 'rx':
                return True
    except (OSError, ValueError, AttributeError):
        pass
    return session.ac_online()


def plan(profile, args, env, enabled=None):
    if not args:raise ValueError('Missing original app command')
    active=(session.opted_in(env) and session.compatible() and selected(profile,env) and session.socket_ready(env)) if enabled is None else enabled
    # Child launchers must not inherit another app's graphics interposer.
    if env.get('FROST_GPU_WRAPPED')=='1' or env.get('VK_DRIVER_FILES')==str(session.PREFIX/'share/zss_icd.json'):
        env=session.clean(env)
    # A stock session or disabled route executes precisely the original argv.
    if not active:return args,env
    args,env,ordinary=unwrap_env(args,env)
    if not ordinary:return args,env
    route=ROUTES[profile].removeprefix('limited-')
    env=dict(env)
    if route in ('igpu-native','office'):
        env=session.clean(env)
        env['FROST_GPU_WRAPPED']='1'
        if route=='igpu-native':
            # Signed-in WeChat executes unsupported query commands under Zink.
            # Its native iGPU renderer stays usable without blocking migration
            # of the desktop and other applications. This is not app migration.
            env.update(DRI_PRIME='pci-0000_07_00_0',MESA_VK_DEVICE_SELECT='1002:1638!',
                       MESA_VK_DEVICE_SELECT_FORCE_DEFAULT_DEVICE='1',QT_QPA_PLATFORM='xcb',
                       FROST_GPU_FIXED_IGPU='1')
        else:
            # The installed Qt media backend crashes while grabbing a video
            # thumbnail; GTK/GStreamer playback passed on both renderers.
            env.update(SAL_USE_VCLPLUGIN='gtk3',GDK_BACKEND='x11')
        return args,env
    if route=='raster':
        env['QT_XCB_GL_INTEGRATION']='none'
        env['QT_QPA_PLATFORM']='xcb'
        return args,env
    env['FROST_GPU_WRAPPED']='1'
    env.update(ZSS_RETAIN='ram',ZSS_START_ON=session.RX if render_on_rx(env) else session.IGPU,
               ZSS_REAL_DRIVER_FILES='/usr/share/vulkan/icd.d/radeon_icd.json')
    if route=='chromium':
        # The normal Bitwarden/VSCodium shell wrappers do not contain a literal
        # runtime path that zss-run's generic recognizer can follow. Keep those
        # security/config wrappers and supply the tested backend explicitly.
        if not any(a.startswith(('--use-angle=', '--use-gl=')) for a in args):
            args=[*args, '--use-angle=vulkan']
        feature=False
        for i,a in enumerate(args):
            if a.startswith('--enable-features='):
                feature=True
                if 'Vulkan' not in a.split('=',1)[1].split(','): args[i]=a+',Vulkan'
        if not feature: args=[*args,'--enable-features=Vulkan']
        if not any(a=='--ozone-platform' or a.startswith('--ozone-platform=') for a in args):
            args=[*args,'--ozone-platform=x11']
    if route=='rog':
        args=[str(session.PREFIX/'bin/rog-control-center'),*args[1:]]
        env.update(SLINT_BACKEND='winit-femtovg',WINIT_UNIX_BACKEND='x11')
        route='gl'
    if route=='wezterm':
        # Global command options precede `start`; all user config remains loaded.
        # Use the independently tested GL route instead of the WebGPU backend.
        args=[args[0], '--config', 'front_end="OpenGL"', '--config', 'enable_wayland=false', *(args[1:] or ['start'])]
        if 'start' in args and '--always-new-process' not in args:
            args.insert(args.index('start')+1, '--always-new-process')
        route='gl'
    if route=='gl':
        env['GDK_BACKEND']='x11'
        if 'WAYLAND_DISPLAY' in env:env['FROST_GPU_WAYLAND_DISPLAY']=env.pop('WAYLAND_DISPLAY')
        if profile=='wechat':env['QT_QPA_PLATFORM']='xcb'
        if profile=='firefox':env['MOZ_ENABLE_WAYLAND']='0'
    return [str(session.PREFIX/'bin/zss-run'), *(['--gl'] if route=='gl' else []), *args],env


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile',choices=sorted(ROUTES))
    parser.add_argument('--print',action='store_true',dest='show')
    parser.add_argument('command',nargs=argparse.REMAINDER)
    options=parser.parse_args()
    args=options.command
    if args[:1]==['--']:args=args[1:]
    command,env=plan(options.profile,args,dict(os.environ))
    if options.show:
        # Do not print per-app proxy assignments, profiles or account arguments.
        print(json.dumps({'profile':options.profile,'configuredRoute':ROUTES[options.profile],'migratingRoute':command[0]==str(session.PREFIX/'bin/zss-run'),'executable':command[0]}));return
    os.execvpe(command[0],command,env)


if __name__=='__main__':main()
