# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Ranendall Ma
# Copyright (c) 2012-2014 Tycho Anders
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
# Peermission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from libqtile import bar, layout, qtile, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

mod = "mod4"
terminal = guess_terminal()

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),

    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="d window"),
    Key([mod], "f",lazy.window.toggle_fullscreen(),desc="Toggle fullscreen on the focused window",),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "y", lazy.window.toggle_floating()),  # Toggle floating on the focused window
    Key([mod], "q", lazy.spawn("rofi -show drun -show-icons"), desc="Spawn a command using a prompt widget"),
    Key([mod], "s", lazy.spawn("flameshot gui"), desc="Spawn a command using a prompt widget"),
    Key([mod], "m", lazy.spawn("cherrytree"), desc="Spawn a command using a prompt widget"),
]

group_default_layout = "columns"
groups = []
group_names = ["a", "z", "e", "r", "t"]
group_labels = ["a", "z", "e", "r", "t"]

for i in range(len(group_names)):
    groups.append(
        Group(
            name=group_names[i],
            layout=group_default_layout,
            label=group_labels[i],
        )
    )

    keys.extend([
        # mod1 + group number = switch to group
        Key([mod], group_names[i], lazy.group[group_names[i]].toscreen(), desc="Switch to group {}".format(group_names[i]),),
        # mod1 + shift + group number = switch to & move focused window to group
        Key([mod, "shift"], group_names[i], lazy.window.togroup(group_names[i], switch_group=True), desc="Switch to & move focused window to group {}".format(group_names[i]),),
    ])

system_font = "MartianMono Nerd Font"
font_size = 10
panel_size = 18
gap_size = 3
border_size = 3

colors = dict(
        background = "#080808",
        foreground = "#bdbdbd",
        disabled = "#323437",
        accent = "#8f61ff",
        )

borders = dict(
        margin = gap_size,
        single_margin = gap_size,
        border_width = border_size,
        border_on_single = True,
        border_focus = colors["accent"],
        border_normal = colors["disabled"],
        )

layouts = [
        layout.Columns(**borders),
        layout.Max(**borders),
        ]
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),

widget_defaults = dict(
        font = system_font,
        fontsize = font_size,
        padding = 8,
        margin = 0,
        foreground = colors["foreground"]
        )

extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        bottom=bar.Bar(
            widgets=[
                widget.CurrentLayoutIcon(),
                widget.GroupBox(disable_drag=True),
                widget.WindowName(),
                widget.Wallpaper(directory= '/home/lookf/wallpapers', background='#080808', label='wallpaper'),
                widget.Systray(),
                widget.Volume(mouse_callbacks={'Button1': lazy.spawn("pavucontrol") }),
                widget.Clock(format="%d-%m-%Y %a %H:%M "),
                widget.QuickExit(),
            ],
            size=panel_size,
            margin=[gap_size, 0, 0, 0],
            background=colors["background"],
        ),
        left=bar.Gap(gap_size),
        right=bar.Gap(gap_size),
        top=bar.Gap(gap_size),

        # set static wallpaper
        # wallpaper= '/home/lookf/wallpapers/ll1.jpg',

        # set wallpaper mode to 'fill' or 'stretch'
        # wallpaper_mode= 'fill',
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = False
bring_front_dclick = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
