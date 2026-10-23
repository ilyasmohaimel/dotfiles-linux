<p align="center">
  <a href="https://github.com/ilyasmohaimel/dotfiles-linux/blob/main/previews/hyprland-desktop-1080p.mp4">
    <img src="previews/hyprland-desktop-preview.webp?v=3" alt="Frost's Hyprland and Caelestia desktop tour playing on the G513QY laptop model. Click for the full 66-second video with sound." width="100%">
  </a>
</p>

<p align="center"><a href="previews/hyprland-desktop-1080p.mp4">Watch the full 66-second video with sound, 1080p / 60 FPS</a></p>

# My Linux dotfiles

My Arch Linux setup, split by desktop/window manager so I can keep old configurations around without mixing them together.

I write these notes so I can restore things if I forget how I set them up. They should also be useful if someone wants to understand my setup, back up their own system with the same approach, or use parts of my dotfiles in their own configuration.

This repo only holds safe configs and notes. My actual backups are kept on my encrypted local NAS, including private files, project archives, SSH keys, app data, browser profiles, and session databases.

## How My Setup Looks

Current Hyprland / Caelestia desktop:

The full-length preview above loops automatically. [Watch the 1080p / 60 FPS laptop showcase with sound](previews/hyprland-desktop-1080p.mp4): the edited desktop recording plays on the 3D G513QY laptop's display. It includes the LF fetch, window controls, wallpaper and theme pickers, the music widget, weather for your city and the next-login GPU menu. The [standalone screen recording](previews/hyprland-screen-recording-1080p.mp4) and [unedited captures](previews/hyprland-desktop-unedited.mp4) are available too.

The original desktop shell and dotfiles are **Caelestia by [soramane](https://github.com/soramanew) and contributors**:

> A fluid, morphing interface to your Linux desktop

From [Caelestia's project description](https://github.com/caelestia-dots/caelestia). See the [original Reddit showcase](https://www.reddit.com/r/unixporn/comments/1l5ll27/hyprland_i_3_quickshell/), [upstream shell](https://github.com/caelestia-dots/shell), and [full credits](hyprland/CREDITS.md). This repository adds my configuration and local integrations.

Earlier KDE snapshot:

[![14-second, 15 FPS preview of my KDE setup, themes, and apps](previews/setup-preview-14s-15fps.gif)](previews/setup-preview-14s-1080p.mp4)

[Watch the 1080p / 30 FPS version](previews/setup-preview-14s-1080p.mp4)

| Profile | Status | Contents |
| --- | --- | --- |
| [`kde/`](kde/) | Previous snapshot | My Plasma, KWin, GTK, terminals, Fish, Fastfetch, editor, launcher, NVIDIA, zram, and memory settings |
| [`qtile/`](qtile/) | Archived | My older Qtile, Rofi, Fish, and Alacritty setup |
| [`hyprland/`](hyprland/) | Current, 23 October 2026 | Caelestia, customized shortcuts, AMD GPU login choices, 300 Hz display, terminals, launcher, themes, and phone shortcut sheets |

## Wallpapers

My wallpaper collection is in [`Wallpapers/`](Wallpapers/), at the top level so it is easy to browse or download. To put it back in my home folder:

```sh
rsync -a Wallpapers/ "$HOME/Pictures/Wallpapers/"
```

## KDE

The KDE folder mirrors where files belong on the system:

```text
kde/
├── home/       # copy into $HOME
├── etc/        # review, then copy into /etc as root
└── manifests/  # package, Flatpak, and enabled-unit snapshots
```

I can preview a home restore with:

```sh
rsync -an kde/home/ "$HOME"/
```

Then restore only the files I actually want:

```sh
rsync -a kde/home/ "$HOME"/
systemctl --user daemon-reload
```

The files in `etc/` are hardware-specific, so I review them before applying them:

```sh
sudo rsync -an kde/etc/ /etc/
sudo rsync -a kde/etc/ /etc/
sudo mkinitcpio -P
sudo sysctl --system
```

To install the official Arch packages from this setup:

```sh
sudo pacman -S --needed - < kde/manifests/pacman-official.txt
```

The AUR and Flatpak files are just inventories, not scripts I should run blindly. The same goes for the enabled-service lists.

## Hardware notes

- [Restoring my Intel + NVIDIA hybrid GPU setup](docs/GPU-HYBRID-RESTORE.md)
- [Restoring app settings](docs/APP-CONFIGS.md)
- [Restoring my KDE Activities](docs/KDE-ACTIVITIES.md)
- [My Activity color themes](docs/ACTIVITY-THEMES.md)
- [Backing up and restoring the whole system](docs/SYSTEM-BACKUP.md)

## What I do not keep here

I leave out credentials, SSH keys, browser profiles, cookies, tokens, session databases, caches, mount details, printer secrets, Sunshine state, and other machine/account-specific data.

The older KDE snapshot targets Intel UHD 620 + NVIDIA MX150. The current Hyprland snapshot targets an ASUS ROG G513QY with Ryzen 9 5900HX and Radeon RX 6800M. Read each desktop's notes before restoring hardware-specific files.
