<p align="center">
  <a href="https://github.com/ilyasmohaimel/dotfiles-linux/blob/main/previews/hyprland-desktop-1080p.mp4">
    <img src="../previews/hyprland-desktop-preview.webp?v=2" alt="Frost's Hyprland and Caelestia desktop tour playing on the G513QY laptop model. Click for the full 66-second video with sound." width="100%">
  </a>
</p>

<p align="center"><a href="../previews/hyprland-desktop-1080p.mp4">Watch the full 66-second video with sound, 1080p / 60 FPS</a></p>

# Frost's Hyprland setup

Snapshot of my working Arch Linux / Caelestia configuration on 23 October 2026. This replaces the old Hyprland placeholder. KDE remains available on the laptop; this directory does not replace the older `kde/` snapshot.

The laptop is an ASUS ROG G513QY with Ryzen 9 5900HX, integrated Radeon graphics and Radeon RX 6800M. The internal display is configured for 1920×1080 at 300 Hz. The session wrappers and device paths are specific to this machine.

## Desktop recording

The full-length preview above loops automatically. [Watch the 1080p / 60 FPS laptop showcase with sound](../previews/hyprland-desktop-1080p.mp4). The edited recording of this actual desktop plays on the 3D G513QY laptop's display. It shows LF Fastfetch, WezTerm and Foot, window controls, window transfers between desktops, wallpaper and palette changes, the theme picker, app search, the current music widget, weather for your city and the next-login GPU menu. The music widget was retaken with the working album artwork. The phone shortcut sheets appear near the end. Captions sit below the desktop image so they keep clear of the interface. Personal browser/chat windows and notification contents are outside the capture.

[Standalone edited screen recording](../previews/hyprland-screen-recording-1080p.mp4) · [Unedited desktop captures](../previews/hyprland-desktop-unedited.mp4) · [Still image](../previews/hyprland-desktop.jpg). The edit has a new original electronic soundtrack; desktop audio was not recorded.

Frames from the film: [weather](../previews/hyprland-weather.jpg), [themes](../previews/hyprland-themes.jpg), and [phone shortcut sheets](../previews/hyprland-shortcuts.jpg).

## Original work

The shell and underlying dotfiles are **Caelestia by [soramane](https://github.com/soramanew) and contributors**.

> A fluid, morphing interface to your Linux desktop

From [Caelestia's project description](https://github.com/caelestia-dots/caelestia).

The [original Reddit showcase](https://www.reddit.com/r/unixporn/comments/1l5ll27/hyprland_i_3_quickshell/) was posted by u/Rexcrazy804 on soramane's behalf. That work inspired this setup. Frost's shortcuts, hardware integration, terminal changes and video presentation are local customizations. [Full credits and sources](CREDITS.md).

## Included

- Hyprland Lua configuration and the complete installed Caelestia QML tree, including the local launcher, weather, GPU menu and startup fixes.
- Customized window focus, resize, floating, desktop, screenshot and app shortcuts; three-finger horizontal desktop gestures.
- WezTerm, Foot, Fish, Bash, zoxide, Starship and the minimal Fastfetch with LF, snowflakes, CPU and main GPU lines.
- Wallpaper/theme helpers, Spotify theme, Brave theme/proxy-backend wrapper, Firefox extension policy, Safe Eyes and Hiddify/Blip autostart entries.
- GPU choices under Battery → GPU mode. Changes apply at the next login. This snapshot does not install the separate experimental KDE live-GPU stack.
- Selected system helpers and login entries, exact upstream source revisions, source patches, build recipes, package inventories and checksums.
- Six phone shortcut images and a PDF. Every one of the 183 user-facing live desktop bindings was represented when the sheets were made. Terminal controls and launcher commands are included too.

This is a configuration backup, not a disk image or unattended installer. Account sign-ins, VPN/proxy profiles and credentials, browser profiles, cookies, wallet data, SSH keys, histories, caches, logs, notification databases, Spotify binaries and application account data are excluded. Hiddify autostart is included; its connections and subscription URLs are not.

## Shortcuts on a phone

[Download the PDF](docs/shortcuts/Frost-Hyprland-shortcuts.pdf).

| Sheet | Contents |
| --- | --- |
| [1. Windows](docs/shortcuts/Frost-shortcuts-page-1.png) | Focus, switch, move, resize, float, minimize |
| [2. Desktops and apps](docs/shortcuts/Frost-shortcuts-page-2.png) | Number keys, app launchers, hidden workspaces |
| [3. Capture and appearance](docs/shortcuts/Frost-shortcuts-page-3.png) | Screenshots, recording, wallpapers, clipboard |
| [4. Media and gestures](docs/shortcuts/Frost-shortcuts-page-4.png) | Volume, brightness, touchpad, sleep keys |
| [5. Panels and advanced](docs/shortcuts/Frost-shortcuts-page-5.png) | Lock, shell restart, window/workspace groups |
| [6. Launcher and terminal](docs/shortcuts/Frost-shortcuts-page-6.png) | Search commands, power actions, Fish, Foot |

Meta means the Windows/Super key. Meta+L focuses right; Meta+Alt+L locks. Meta+1…0 selects desktops, and adding Shift moves the active window there. Meta+I toggles floating. Meta+right-drag floats first only when the window is alone on its desktop. Meta+M opens the hidden music workspace containing Spotify.

## Layout

```text
hyprland/
  home/        Selected files relative to the home directory
  system/      Selected files relative to /; review and install manually
  manifests/   Snapshot metadata, SHA-256 checksums, versions and source pins
  build/       Original PKGBUILDs, source patches and untracked source overlays
  licenses/    Upstream licenses
  reference/   Wallpaper sources, extension release and original helper sources
  docs/        Shortcut sheets and build notes
  tools/       Explicit backup collector and checked home-restore helper
```

The six added static wallpapers live in [`../Wallpapers/Caelestia/`](../Wallpapers/Caelestia/). The Steam Workshop item is a static preview; Wallpaper Engine animation assets are not part of this setup. Older wallpapers in the parent collection are retained.

## Verify and preview a restore

From the repository root, using Python 3:

```sh
python3 hyprland/tools/restore.py --verify
python3 hyprland/tools/restore.py
```

The default is a preview. Verification checks every home/system file against its captured SHA-256 checksum and checks relative symlink targets. It also rejects unlisted payload files. Restore refuses destination paths that pass through symlinked directories.

For a disposable rehearsal:

```sh
python3 hyprland/tools/restore.py --target-home /tmp/frost-restore-rehearsal --apply
```

Do not log into that rehearsal directory or run its startup scripts. Some files contain `/home/lookfrost` paths, so a different account needs a manual path review before use.

## Restore on this laptop

Save current work and use the retained KDE session while restoring. Review the diff and install the matching dependencies first; the package lists are inventories, not commands to reinstall every recorded package. The current setup uses Lua-based Hyprland configuration and pinned Quickshell/Caelestia source revisions. Replacing them with a random release can break the config. See [build notes](docs/BUILD.md).

After reviewing the home payload:

```sh
python3 hyprland/tools/restore.py --apply
systemctl --user daemon-reload
```

The helper saves existing changed files beneath `~/.local/state/frost-dotfiles-restore/<timestamp>/` before replacement. It does not delete unrelated files, install packages, start services, reload Hyprland, or write to system paths.

Review and restore `system/` separately. Its wrappers, login entries and browser policies depend on the installed packages. Keep helpers owned by root. The original, reviewed Brave helper sudoers rule is under `reference/`, because the live rule is root-readable; it is not claimed as a fresh verified copy of `/etc/sudoers.d`. Validate it with `visudo -cf` before installing it as root. Do not copy or change sudoers ownership blindly.

Install the official Caelestiafox 2.0 extension referenced by `reference/firefox-addon-release.json` at the local path in the Firefox policy before enabling that policy. No Firefox profile is included. Brave uses the existing Hiddify system-proxy settings through a per-process desktop-backend override; configure Hiddify's private connections separately.

For themed Spotify, install Spotify and Spicetify, create a user-owned copy of `/opt/spotify` at `~/.local/share/caelestia-spotify`, then apply the included Spicetify theme as the normal user. The binaries and original account preferences are not in Git. Refresh that copy after Spotify package updates. The launch wrapper uses the themed copy only in Hyprland.

Restore wallpapers to `~/Pictures/Wallpapers/`. Generated initial Foot/Hyprland colors are included so the first launch has a palette; Caelestia regenerates them after changing wallpaper.

Select **Caelestia (Hyprland)** at login. Check the launcher, display mode, cursor, wallpaper, audio, autostarts, lock, suspend/resume and screen sharing on the actual machine. A file restore alone does not prove those hardware/session behaviors.

## Refresh this backup

```sh
python3 hyprland/tools/backup.py
python3 hyprland/tools/restore.py --verify
git diff --stat
git status --short
```

The collector reads only the allowlisted desktop paths. It does not read GitHub authentication, browser accounts, Hiddify connection data, keyrings, SSH keys or histories. It does not commit or push. Review added files and run a secret scanner with redaction before publishing a refresh. Keep changes to the older KDE/Qtile snapshots out of a Hyprland refresh.

## Source and updates

The desktop is based on [Caelestia dots](https://github.com/caelestia-dots/caelestia), [Caelestia shell](https://github.com/caelestia-dots/shell), [Caelestia CLI](https://github.com/caelestia-dots/cli) and [Quickshell](https://quickshell.outfoxxed.me/). Upstream licenses are retained. Shell package updates can replace local integrations; preserve or reapply this QML tree and check version compatibility rather than assuming an AUR update keeps the customizations.
