local wezterm = require 'wezterm'
local config = wezterm.config_builder()

config.default_prog = { '/usr/bin/fish', '--login' }
config.default_cwd = wezterm.home_dir

config.colors = {
  foreground = '#ded6e1',
  background = '#1e1e26',
  cursor_bg = '#7399bb',
  cursor_fg = '#1e1e26',
  cursor_border = '#7399bb',
  selection_bg = '#7399bb',
  selection_fg = '#1e1e26',
  scrollbar_thumb = '#2f3233',
  split = '#2f3233',
  ansi = {
    '#1e1e26', '#b09c6d', '#7399bb', '#a9b9c8',
    '#7399bb', '#869596', '#a9b9c8', '#ded6e1',
  },
  brights = {
    '#2f3233', '#d0bd8f', '#9bb7d1', '#ded6e1',
    '#a9b9c8', '#a9b9c8', '#ded6e1', '#ffffff',
  },
}

config.font = wezterm.font_with_fallback({
  'JetBrainsMono Nerd Font',
  'Symbols Nerd Font',
})
config.font_size = 11.0

config.window_background_opacity = 0.5
config.wayland_window_background_blur = true
config.window_padding = { left = 15, right = 15, top = 15, bottom = 15 }
config.window_decorations = 'TITLE | RESIZE'
config.hide_tab_bar_if_only_one_tab = true
config.use_fancy_tab_bar = false
config.initial_cols = 120
config.initial_rows = 34

config.front_end = 'WebGpu'
config.webgpu_power_preference = 'LowPower'

config.keys = {
  {
    key = 'Enter',
    mods = 'SHIFT',
    action = wezterm.action.SendString('\x1b\r'),
  },
}

config.scrollback_lines = 10000
config.audible_bell = 'Disabled'
config.window_close_confirmation = 'NeverPrompt'

return config
