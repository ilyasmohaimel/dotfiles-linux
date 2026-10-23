#!/usr/bin/python3
"""Independent Hyprland GPU choices, applied only when starting a new login."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

MODES = ('auto', 'igpu', 'rx', 'eco')
NAMES = {'auto': 'Automatic', 'igpu': 'iGPU', 'rx': 'RX 6800M', 'eco': 'Eco'}


def config_path():
    return Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config'))) / 'frost-hyprland/gpu.json'


def runtime_path():
    return Path(os.environ.get('XDG_RUNTIME_DIR', '/run/user/'+str(os.getuid()))) / 'frost-hyprland/session.json'


def read_json(path):
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def mode(path=None):
    value = read_json(path or config_path()).get('mode', 'auto')
    return value if value in MODES else 'auto'


def select(requested, source):
    if requested not in MODES:
        raise ValueError('Invalid GPU mode')
    return ('rx' if source['useRX'] else 'igpu') if requested == 'auto' else 'igpu' if requested == 'eco' else requested


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix='.gpu-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream);stream.write('\n')
        Path(temporary).replace(path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def request(value, path=None):
    if value not in MODES:
        raise ValueError('Invalid GPU mode')
    atomic_json(path or config_path(), {'mode': value})


def power_source():
    spec=importlib.util.spec_from_file_location('frost_power', '/usr/local/libexec/frost_power.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.power_source()


def text(path):
    try:return path.read_text().strip()
    except OSError:return 'unknown'


def active_session(data):
    # A mode saved by an older desktop must never be presented as this login.
    return (bool(os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'))
            and data.get('signature') == os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
            and data.get('token') == os.environ.get('FROST_HYPRLAND_TOKEN')
            and data.get('selected') in ('igpu', 'rx'))


def status():
    data=read_json(runtime_path());active=active_session(data)
    source=power_source();next_mode=mode()
    rx=Path('/sys/bus/pci/devices/0000:03:00.0')
    runtime=text(rx/'power/runtime_status');pci=text(rx/'power_state')
    return {'active':active, 'desktop':data.get('selected') if active else 'unknown',
            'loginMode':data.get('mode') if active else 'unknown',
            'nextMode':next_mode, 'nextModeName':NAMES[next_mode],
            'nextGPU':select(next_mode,source), 'powerSource':source['source'],
            'rxRuntime':runtime,'rxPCI':pci,'rxOff':runtime=='suspended' and pci=='D3cold',
            'profile':text(Path('/sys/firmware/acpi/platform_profile')),
            'liveMigration':False, 'applies':'next-login'}


def activate():
    env=os.environ
    if env.get('XDG_CURRENT_DESKTOP')!='Hyprland' or not env.get('FROST_HYPRLAND_TOKEN'):
        raise ValueError('Not a Frost Hyprland login')
    signature=env.get('HYPRLAND_INSTANCE_SIGNATURE')
    rows=json.loads(subprocess.check_output(['/usr/bin/hyprctl','instances','-j'],text=True,timeout=3))
    row=next((r for r in rows if r.get('instance')==signature),None)
    if row is None:raise ValueError('Current Hyprland instance is unavailable')
    selected=env.get('FROST_HYPRLAND_GPU');login_mode=env.get('FROST_HYPRLAND_MODE')
    if selected not in ('igpu','rx') or login_mode not in MODES:raise ValueError('Missing login GPU selection')
    atomic_json(runtime_path(),{'mode':login_mode,'selected':selected,'pid':int(row['pid']),
                              'session':env.get('XDG_SESSION_ID',''), 'signature':signature,
                              'token':env['FROST_HYPRLAND_TOKEN']})
    # Only the dedicated Eco login sets a profile; status reads do not write.
    if login_mode=='eco':
        subprocess.run(['/usr/bin/asusctl','profile','set','Quiet'],check=True,timeout=8,capture_output=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=(*MODES,'status','activate'))
    args=parser.parse_args()
    try:
        if args.action=='status':print(json.dumps(status()))
        elif args.action=='activate':activate()
        else:request(args.action);print('Saved for next Caelestia login: '+NAMES[args.action])
    except (OSError,ValueError,subprocess.SubprocessError) as error:
        parser.exit(1,str(error)+'\n')

if __name__=='__main__':main()
