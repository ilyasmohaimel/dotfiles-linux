# My Linux dotfiles

My Arch Linux setup, split by desktop/window manager so I can keep old configurations around without mixing them together.

| Profile | Status | Contents |
| --- | --- | --- |
| [`kde/`](kde/) | Current | My Plasma, KWin, GTK, terminals, Fish, Fastfetch, editor, launcher, NVIDIA, zram, and memory settings |
| [`qtile/`](qtile/) | Archived | My older Qtile, Rofi, Fish, and Alacritty setup |
| [`hyprland/`](hyprland/) | Later | Kept ready for a future Hyprland setup |

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

## What I do not keep here

I leave out credentials, SSH keys, browser profiles, cookies, tokens, session databases, caches, mount details, printer secrets, Sunshine state, and other machine/account-specific data.

Some paths and hardware choices are still specific to my laptop: Intel UHD 620 + NVIDIA MX150 hybrid graphics with the `nvidia-580xx` driver stack.
