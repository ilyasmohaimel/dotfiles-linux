function launchUnit(unit) {
  callDBus(
    'org.freedesktop.systemd1',
    '/org/freedesktop/systemd1',
    'org.freedesktop.systemd1.Manager',
    'StartUnit',
    unit,
    'replace'
  )
}

registerShortcut(
  'lookfrost-launch-wezterm',
  'Launch WezTerm',
  'Meta+Return',
  function () {
    launchUnit('lookfrost-launch-wezterm.service')
  }
)

registerShortcut(
  'lookfrost-launch-brave',
  'Launch Brave',
  'Meta+B',
  function () {
    launchUnit('lookfrost-launch-brave.service')
  }
)
