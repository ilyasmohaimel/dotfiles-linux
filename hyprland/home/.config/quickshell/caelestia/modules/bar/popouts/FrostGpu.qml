pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services

Column {
    id: root
    spacing: Tokens.spacing.small
    property var state: ({})
    property string errorText: ""
    readonly property string helper: Quickshell.env("HOME") + "/.local/bin/frost-hyprland-gpu"

    property bool expanded: false

    function toggle(): void {
        expanded = !expanded;
        if (expanded && !reader.running) reader.running = true;
    }

    StyledRect {
        id: header
        width: parent.width
        implicitHeight: heading.implicitHeight + Tokens.padding.medium * 2
        radius: Tokens.rounding.medium
        color: Colours.tPalette.m3surfaceContainer
        activeFocusOnTab: true
        Accessible.role: Accessible.Button
        Accessible.name: "GPU mode, " + (root.expanded ? "expanded" : "collapsed")
        Keys.onReturnPressed: root.toggle()
        Keys.onSpacePressed: root.toggle()
        border.width: activeFocus ? 2 : 0
        border.color: Colours.palette.m3primary

        StateLayer {
            radius: parent.radius
            onClicked: {
                header.forceActiveFocus();
                root.toggle();
            }
        }
        Column {
            id: heading
            anchors.left: parent.left
            anchors.right: chevron.left
            anchors.margins: Tokens.padding.medium
            anchors.verticalCenter: parent.verticalCenter
            spacing: Tokens.spacing.extraSmall
            StyledText { text: "GPU mode" }
            StyledText {
                width: parent.width
                wrapMode: Text.Wrap
                text: "Next login: " + (root.state.nextModeName || "Automatic")
                color: Colours.palette.m3onSurfaceVariant
            }
        }
        MaterialIcon {
            id: chevron
            anchors.right: parent.right
            anchors.rightMargin: Tokens.padding.medium
            anchors.verticalCenter: parent.verticalCenter
            text: root.expanded ? "expand_less" : "expand_more"
            fontStyle: Tokens.font.icon.medium
            color: Colours.palette.m3onSurfaceVariant
        }
    }
    Column {
        width: parent.width
        spacing: Tokens.spacing.small
        visible: root.expanded
        StyledText {
            width: parent.width
            text: "Desktop GPU: " + (root.state.desktop === "rx" ? "RX 6800M" : root.state.desktop === "igpu" ? "iGPU" : "checking")
        }
        StyledText {
            width: parent.width
            wrapMode: Text.Wrap
            text: "RX: " + (root.state.rxOff ? "off (D3cold)" : root.state.rxRuntime === "active" ? "powered on" : root.state.rxRuntime || "checking")
            color: Colours.palette.m3onSurfaceVariant
        }
        StyledText {
            width: parent.width
            text: "Next login: " + (root.state.nextModeName || "Automatic")
        }
        Grid {
            id: buttons
            width: parent.width
            columns: 2
            spacing: Tokens.spacing.small
            Repeater {
                model: [{ mode: "auto", label: "Automatic" }, { mode: "igpu", label: "iGPU" },
                        { mode: "rx", label: "RX 6800M" }, { mode: "eco", label: "Eco" }]
                TextButton {
                    required property var modelData
                    implicitWidth: (buttons.width - buttons.spacing) / 2
                    text: modelData.label
                    checked: root.state.nextMode === modelData.mode
                    isToggle: true
                    type: TextButton.Tonal
                    disabled: setter.running
                    activeFocusOnTab: true
                    Accessible.role: Accessible.Button
                    Accessible.name: modelData.label + " for next login"
                    Keys.onReturnPressed: clicked()
                    Keys.onSpacePressed: clicked()
                    onClicked: {
                        setter.command = [root.helper, modelData.mode];
                        setter.running = true;
                    }
                    border.width: activeFocus ? 2 : 0
                    border.color: Colours.palette.m3primary
                }
            }
        }
        StyledText {
            width: parent.width
            wrapMode: Text.Wrap
            text: "Applies at the next Caelestia (Hyprland) login. Automatic uses RX on barrel power and iGPU on USB-C or battery. Eco starts iGPU with Quiet."
            color: Colours.palette.m3onSurfaceVariant
        }
        StyledText {
            visible: root.errorText.length > 0
            width: parent.width
            wrapMode: Text.Wrap
            text: root.errorText
            color: Colours.palette.m3error
        }
    }
    Process {
        id: reader
        command: [root.helper, "status"]
        running: true
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.state = JSON.parse(text); }
                catch (e) { root.errorText = "GPU status unavailable"; }
            }
        }
    }
    Process {
        id: setter
        onExited: (code, status) => {
            root.errorText = code === 0 ? "" : "Could not save GPU mode";
            reader.running = true;
        }
    }
    Timer {
        interval: 3000
        repeat: true
        running: root.visible && root.expanded
        onTriggered: if (!reader.running) reader.running = true
    }
}
