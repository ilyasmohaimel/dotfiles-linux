-- Keep KDE app integration and the existing cursor theme in this session.
hl.env("QT_QPA_PLATFORMTHEME", "kde")
hl.monitor({ output = "eDP-1", mode = "1920x1080@300", position = "auto", scale = 1 })
hl.config({
    input = { touchpad = { natural_scroll = true, scroll_factor = 0.3 } },
    cursor = { no_hardware_cursors = 1 },
    misc = { vrr = 0, disable_hyprland_logo = true, disable_splash_rendering = true },
})
require("kde-shortcuts")

hl.device({
    name = "logitech-g502-hero-gaming-mouse",
    sensitivity = -0.2,
    accel_profile = "flat",
    middle_button_emulation = true,
})
