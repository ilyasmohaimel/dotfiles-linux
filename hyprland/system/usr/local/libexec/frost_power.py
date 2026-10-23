"""Machine power-source policy shared by startup, launchers and live switching."""
from pathlib import Path
import json


def power_source(root=Path('/sys/class/power_supply')):
    """UCSI input wins over the firmware's aggregate ADP0 online bit."""
    active = []
    try:
        supplies = list(Path(root).iterdir())
    except OSError:
        supplies = []
    for supply in supplies:
        try:
            kind = (supply/'type').read_text().strip()
            online = int((supply/'online').read_text().strip()) > 0
        except (OSError, ValueError):
            continue
        if kind == 'Battery' or not online:
            continue
        active.append({'name': supply.name, 'type': kind})
    usb = any(s['type'].startswith('USB') or s['name'].startswith('ucsi-source-psy-') for s in active)
    # ADP0 also goes online on USB-C PD. Never use it as barrel evidence while
    # a USB supply is active; this also conservatively selects iGPU with both.
    barrel = not usb and any(s['name'] == 'ADP0' and s['type'] == 'Mains' for s in active)
    return {'source': 'usb-c' if usb else 'barrel' if barrel else 'external-unknown' if active else 'battery',
            'externalPower': bool(active), 'useRX': barrel, 'onlineSupplies': active}


if __name__ == '__main__':
    print(json.dumps(power_source()))
