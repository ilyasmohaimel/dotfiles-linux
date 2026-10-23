#!/usr/bin/env python3
"""Keep ASUS Quiet mode on USB-C; restore ASUS defaults when leaving USB-C."""
import importlib.util
from pathlib import Path
import subprocess
import time
import os
import json

PROFILE_NAMES = {'Quiet': 'quiet', 'Balanced': 'balanced', 'Performance': 'performance'}
PROFILE_PATH = Path('/sys/firmware/acpi/platform_profile')


def defaults():
    result = subprocess.run(['/usr/bin/asusctl', 'profile', 'get'],
                            capture_output=True, text=True, check=True, timeout=8)
    values = {}
    for line in result.stdout.splitlines():
        for key in ('AC', 'Battery'):
            prefix = key + ' profile '
            if line.startswith(prefix):
                name = line[len(prefix):].strip()
                if name in PROFILE_NAMES:
                    values[key] = name
    return values


def desired(source, previous, get_defaults=defaults):
    if source == 'usb-c':
        return 'Quiet'
    if previous == 'usb-c':
        key = {'barrel': 'AC', 'battery': 'Battery'}.get(source)
        if key:
            name = get_defaults().get(key)
            if name not in PROFILE_NAMES:
                raise RuntimeError('ASUS default profile unavailable for ' + key)
            return name
    return None


def reconcile(source, previous, read_profile, set_profile, get_defaults=defaults):
    target = desired(source, previous, get_defaults)
    if target and read_profile() != PROFILE_NAMES[target]:
        set_profile(target)
        return target
    return None


def set_profile(name):
    subprocess.run(['/usr/bin/asusctl', 'profile', 'set', name],
                   capture_output=True, text=True, check=True, timeout=8)


def main():
    spec = importlib.util.spec_from_file_location('frost_power', '/usr/local/libexec/frost_power.py')
    power = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(power)
    previous = None
    while True:
        try:
            source = power.power_source()['source']
            try:
                directory = Path(os.environ.get('XDG_RUNTIME_DIR', '/run/user/' + str(os.getuid()))) / 'frost-gpu-live'
                mode = json.loads((directory / 'mode.json').read_text())
                eco = mode.get('mode') == 'eco' and mode.get('session') == os.environ.get('XDG_SESSION_ID')
            except (OSError, ValueError, AttributeError):
                eco = False
            # The Eco controller owns Quiet until the user leaves Eco.
            changed = None if eco else reconcile(source, previous, lambda: PROFILE_PATH.read_text().strip(), set_profile)
            if changed:
                print(source + ': selected ASUS ' + changed, flush=True)
            previous = source
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
            # Retry a failed transition without discarding the source to restore.
            print('Power profile update failed: ' + type(error).__name__, flush=True)
            time.sleep(15)
        time.sleep(2)


if __name__ == '__main__':
    main()
