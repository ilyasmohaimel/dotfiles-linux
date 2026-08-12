# My Activity color themes

I keep the desktop in three contexts. Each one has its own wallpaper and KDE color scheme.

| Activity | KDE color scheme | Main colors |
| --- | --- | --- |
| Normal | `Slate169` | `#869596`, `#A9B9C8`, `#DED6E1`, `#666C63`, `#2F3233`, `#1E1E26`, `#B09C6D`, `#7399BB` |
| Coding | `Coding3494593` | `#2A3639`, `#242E30`, `#3A494C`, `#515850`, `#181D1C`, `#8A7B5E`, `#DBA96B`, `#FBF6A0`, `#935741` |
| Gaming | `MoltenGold` | My existing red Molten theme and midpoint wallpaper |

`lookfrost-activity-theme.service` starts with Plasma and checks the active Activity every two seconds. It only changes things when I switch Activity, so it does not waste resources while I stay in one place.

KDE and GTK update immediately. Fastfetch reads the active Activity every time it runs. New Fish shells also pick matching Fish, fzf, and Starship colours. WezTerm and Alacritty use small activity colour files, so they can reload their palette without replacing my terminal settings.

Brave keeps Catppuccin Macchiato for Normal and Coding, then uses the red Gaming colour theme. Chromium only loads its browser chrome theme when it starts, so the selected Brave theme applies on the next clean launch instead of interrupting open tabs.

## Preview

[![16-second preview of my KDE activity themes](../previews/how-my-setup-looks.gif)](../previews/how-my-setup-looks.mp4)

[Watch the 1080p / 30 FPS version](../previews/how-my-setup-looks.mp4)

## Restoring it

After restoring `kde/home/`, run:

```sh
chmod +x "$HOME/.local/bin/lookfrost-apply-activity-theme"
chmod +x "$HOME/.local/bin/lookfrost-activity-theme-monitor"
chmod +x "$HOME/.local/bin/fastfetch"
chmod +x "$HOME/.local/bin/brave"
chmod +x "$HOME/.local/bin/lookfrost-prepare-brave-theme"
systemctl --user daemon-reload
systemctl --user enable --now lookfrost-activity-theme.service
```

The service needs the `Slate169.colors`, `Coding3494593.colors`, and `MoltenGold.colors` files in `~/.local/share/color-schemes/`.
