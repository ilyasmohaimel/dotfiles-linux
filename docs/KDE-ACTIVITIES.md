# My KDE Activities

I use three Activities to separate what I am doing without changing the rest of my desktop setup:

| Activity | Use | Wallpaper |
| --- | --- | --- |
| Normal | Browser, files, chat, and everything else | `169.jpg` |
| Coding | VS Code, terminals, and project work | `EVA/3494593.jpg` |
| Gaming | Steam, games, and media | `midpoint.png` |

The matching KDE color schemes are documented in [My Activity color themes](ACTIVITY-THEMES.md).

The panel stays shared between them on purpose. It keeps the task manager, system tray, clock, audio, and KDE Connect available everywhere instead of creating duplicate panels and duplicate notifications.

## Switching

- `Meta+A` goes to the next Activity.
- `Meta+Shift+A` goes to the previous Activity.
- `Meta+Q` opens the Activity switcher.

Apps do not need to be killed when I change Activity. I use Activities as separate contexts, then launch coding or gaming apps while I am in the matching one. If I want a specific window tied to an Activity, I can use its title-bar menu and choose **Activities**.

## Restoring them

First restore the wallpaper collection from the repository root:

```sh
rsync -a Wallpapers/ "$HOME/Pictures/Wallpapers/"
```

Then run:

```sh
bash kde/scripts/setup-activities.sh
```

The script reuses existing Activities when it finds them, renames a fresh Plasma `Default` Activity to `Normal`, creates anything missing, applies the three wallpapers, and returns to Normal. It does not delete Activities or overwrite the shared panel.
