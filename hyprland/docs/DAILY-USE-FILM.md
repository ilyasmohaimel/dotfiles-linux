# Between windows

A 3:28 film of an afternoon using my Hyprland desktop, recorded on 25 October 2026. Both versions are 1920×1080 at 60 FPS with sound.

- [Exterior laptop film](https://github.com/ilyasmohaimel/dotfiles-linux/releases/download/hyprland-daily-use-r2/hyprland-daily-use-1080p.mp4)
- [Screen-only edit](https://github.com/ilyasmohaimel/dotfiles-linux/releases/download/hyprland-daily-use-r2/hyprland-daily-use-screen-1080p.mp4)
- [Poster](../../previews/hyprland-daily-use.jpg)

The README uses one lightweight 8-second animated preview at 854×480 and 24 FPS, about 1.07 MB. The older tours use clickable still thumbnails so they do not add more background animations. Full films remain 1920×1080 at 60 FPS. The earlier [66-second setup tour](../../previews/hyprland-desktop-1080p.mp4) remains separate.

The full-quality movies are release downloads so their bitrate is not constrained by the repository file limit.

## Chapters

| Time | What happens |
| --- | --- |
| 0:00 | Between windows |
| 0:03 | WezTerm, LF Fastfetch, idle settings and Neovim |
| 0:28 | Brave, Mtab, Caelestia's source and Hyprland documentation |
| 0:50 | Vimium scrolling and link hints |
| 1:07 | Open, edit and syntax-check the window shortcuts in VSCodium |
| 1:40 | Move the editor between desktops and read beside the browser |
| 1:58 | Float, move and resize the editor, then return to tiling |
| 2:19 | Browse and filter the project files in Dolphin |
| 2:34 | Spotify and media controls while working |
| 2:56 | Check the idle settings in Neovim and finish in Mtab |

## What was recorded

This is the real Hyprland session, including native desktop transitions, window animations, mouse movement and app interactions. Brave uses my normal profile, Mtab start page, Bing search engine and installed extensions. Vimium uses my existing J/K scrolling and R link-hint mapping.

The editor shows copies of the installed configuration. A comment is added to the working copy, saved, and checked with Lua's parser. The live desktop configuration is not changed for the demonstration. Neovim, VSCodium and Dolphin use colors matched to the active Caelestia palette.

The floating shortcut bubbles are part of the video edit. Each lasts two seconds and follows a performed key or mouse action. Their measured bounds include all text, icons, keycaps and padding. They are not a keyboard-listening service installed on the desktop.

The edit trims pauses and unrelated browser autocomplete suggestions. The revised cut removes the repeated Brave desktop handoff. Camera moves use eased keyframes with fractional-pixel sampling, with longer moves and readable holds. The original Dolphin timing is retained. The shortcut graphics and licensed soundtrack are added in the edit. It is not an unedited recording. No browser profile, session database or raw daily-use capture is published here.

## Laptop presentation

The edited recording plays on the display of the exterior G513QY model from the earlier Frost GPU film. The laptop sits in a small 3D studio with a shared surface, contact shadows, recessed wall panels and soft lighting. The opening and closing shots are rendered camera moves. The middle sections use screen projections from the same Blender scene, with occasional changes of angle.

Rendering runs locally on the Radeon RX 6800M and CPU, with GPU selection scoped to the render processes. Screen edits use lossless RGB intermediates and the Blender camera moves use lossless 16-bit PNG frames. Each full version receives a single high-quality H.264 delivery encode. The source captures were already compressed, so flat gradients receive a light, edge-preserving cleanup before the camera transforms; a higher export bitrate alone cannot recover information lost in the capture.

## Credits

The desktop shell is [Caelestia by soramane and contributors](https://github.com/caelestia-dots/caelestia). Its upstream design, widgets and animations remain theirs. Frost's personal configuration and the film edit are documented in this repository.

“Signal to Noise” by Scott Buckley is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The soundtrack uses an excerpt with volume normalization and fades. [Track page](https://www.scottbuckley.com.au/library/signal-to-noise/) · [Full sources and credits](../CREDITS.md).
