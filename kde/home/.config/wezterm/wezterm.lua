local wezterm = require 'wezterm'
local config = wezterm.config_builder()

config.default_prog = { '/usr/bin/fish', '--login' }
config.default_cwd = wezterm.home_dir

config.colors = {
  foreground = '#ffffff',
  background = '#000000',
  cursor_bg = '#ff5a1f',
  cursor_fg = '#070505',
  cursor_border = '#ff5a1f',
  selection_bg = '#b0000a',
  selection_fg = '#ffffff',
  scrollbar_thumb = '#22110b',
  split = '#22110b',
  ansi = {
    '#000000', '#b0000a', '#ff5a1f', '#ff5a1f',
    '#25d9e8', '#d8141c', '#25d9e8', '#ffffff',
  },
  brights = {
    '#22110b', '#ff6b36', '#ff6b36', '#ff8a5b',
    '#6eeaf4', '#ef3340', '#6eeaf4', '#ffffff',
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
