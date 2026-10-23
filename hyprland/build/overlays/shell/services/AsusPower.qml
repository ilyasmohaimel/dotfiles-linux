pragma Singleton
pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Services.UPower

Singleton {
    id: root

    property int profile: PowerProfile.Balanced
    readonly property int degradationReason: PerformanceDegradationReason.None

    // ASUS already owns platform profiles on this laptop. Reading never sets a profile.
    function setProfile(value: int): void {
        const name = value === PowerProfile.PowerSaver ? "Quiet"
                   : value === PowerProfile.Performance ? "Performance" : "Balanced";
        if (!setter.running) {
            setter.command = ["asusctl", "profile", "set", name];
            setter.running = true;
        }
    }

    Process {
        id: reader
        running: true
        command: ["asusctl", "profile", "get"]
        stdout: StdioCollector {
            onStreamFinished: {
                const match = text.match(/Active profile:\s*(Quiet|Balanced|Performance)/);
                if (match)
                    root.profile = match[1] === "Quiet" ? PowerProfile.PowerSaver
                                 : match[1] === "Performance" ? PowerProfile.Performance
                                 : PowerProfile.Balanced;
            }
        }
    }

    Process {
        id: setter
        onExited: reader.running = true
    }

    Timer {
        interval: 5000
        running: true
        repeat: true
        onTriggered: reader.running = true
    }

    IpcHandler {
        target: "asusPower"
        function current(): string {
            return root.profile === PowerProfile.PowerSaver ? "Quiet"
                 : root.profile === PowerProfile.Performance ? "Performance" : "Balanced";
        }
    }
}
