# Frost's Linux dotfiles

Desktop configuration snapshots for Arch Linux, organized by desktop or window manager.

| Profile | Status | Contents |
| --- | --- | --- |
| [`kde/`](kde/) | Current | Plasma, KWin, GTK, terminals, Fish, Fastfetch, editor settings, user services, launchers, NVIDIA offload, zram, and memory tuning |
| [`qtile/`](qtile/) | Archived | Qtile, Rofi, Fish, and Alacritty configuration from the earlier setup |
| [`hyprland/`](hyprland/) | Reserved | Placeholder for a future Hyprland profile |

## KDE snapshot

The KDE profile mirrors the destination filesystem:

```text
kde/
├── home/       # copy into $HOME
├── etc/        # review, then copy into /etc as root
└── manifests/  # package, Flatpak, and enabled-unit snapshots
```

Preview a home restore:

```sh
rsync -an kde/home/ "$HOME"/
```

Apply selected user files only after reviewing the preview:

```sh
rsync -a kde/home/ "$HOME"/
systemctl --user daemon-reload
```

System files are hardware-specific. Review them before applying:

```sh
sudo rsync -an kde/etc/ /etc/
sudo rsync -a kde/etc/ /etc/
sudo mkinitcpio -P
sudo sysctl --system
```

Install the official Arch package snapshot:

```sh
sudo pacman -S --needed - < kde/manifests/pacman-official.txt
```

The AUR and Flatpak manifests are inventories, not unattended install scripts. Review versions and package sources before using them. Enabled-unit manifests are also snapshots; do not enable every listed unit blindly.

## Safety

This repository intentionally excludes credentials, SSH keys, browser profiles, cookies, tokens, session databases, caches, network mount details, printer secrets, Sunshine state, and other machine identity or account data.

Some files contain Frost's local paths and hardware choices. In particular, the KDE profile targets an Intel UHD 620 + NVIDIA MX150 hybrid laptop and uses the `nvidia-580xx` stack.
