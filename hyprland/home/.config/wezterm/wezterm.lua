local wezterm = require 'wezterm'
local config = wezterm.config_builder()

config.default_prog = { '/usr/bin/fish', '--login' }
config.default_cwd = wezterm.home_dir

config.colors = require 'activity-colors'

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

-- Match the Caelestia terminal in Hyprland; retain the KDE activity theme.
local desktop = ':' .. (os.getenv('XDG_CURRENT_DESKTOP') or '') .. ':'
if desktop:find(':Hyprland:', 1, true) then
  config.default_prog = {
    '/usr/bin/fish', '--login', '--init-command',
    'source ~/.config/caelestia/foot-init.fish',
  }
  config.font_size = 12.0
  config.window_background_opacity = 0.78
  config.window_padding = { left = 25, right = 25, top = 25, bottom = 25 }
  config.window_decorations = 'RESIZE'
  config.default_cursor_style = 'BlinkingBar'
  config.enable_scroll_bar = false
  config.inactive_pane_hsb = { saturation = 0.9, brightness = 0.85 }

  local state = os.getenv('XDG_STATE_HOME') or (wezterm.home_dir .. '/.local/state')
  local palette_path = state .. '/caelestia/scheme.json'
  wezterm.add_to_config_reload_watch_list(palette_path)
  local file = io.open(palette_path, 'r')
  if file then
    local ok, scheme = pcall(wezterm.json_parse, file:read('*a'))
    file:close()
    if ok and type(scheme.colours) == 'table' then
      local c = scheme.colours
      local function color(name) return '#' .. c[name] end
      local ansi, brights = {}, {}
      for i = 0, 7 do
        ansi[i + 1] = color('term' .. i)
        brights[i + 1] = color('term' .. (i + 8))
      end
      config.colors = {
        foreground = color('onSurface'), background = color('surface'),
        cursor_bg = color('secondary'), cursor_fg = color('surface'),
        cursor_border = color('secondary'), selection_bg = color('secondary'),
        selection_fg = color('onSecondary'), split = color('outlineVariant'),
        ansi = ansi, brights = brights,
        indexed = { [16] = color('primary'), [17] = color('secondary'), [18] = color('tertiary') },
        tab_bar = {
          background = color('surfaceContainer'),
          active_tab = { bg_color = color('primaryContainer'), fg_color = color('onPrimaryContainer'), intensity = 'Bold' },
          inactive_tab = { bg_color = color('surfaceContainer'), fg_color = color('onSurfaceVariant') },
          inactive_tab_hover = { bg_color = color('surfaceContainerHigh'), fg_color = color('onSurface') },
          new_tab = { bg_color = color('surfaceContainer'), fg_color = color('onSurfaceVariant') },
          new_tab_hover = { bg_color = color('secondaryContainer'), fg_color = color('onSecondaryContainer') },
        },
      }
    end
  end
end

return config
