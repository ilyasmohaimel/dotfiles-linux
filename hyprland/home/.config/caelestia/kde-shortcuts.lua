-- User bindings are kept outside the upstream Hyprland config.
local function run(command) return hl.dsp.exec_cmd(command) end
local function bind(key, action) hl.bind(key, action) end
local function dispatch(action) hl.dispatch(action) end

local function cycle(reverse, same_app)
    return function()
        local active, ws = hl.get_active_window(), hl.get_active_workspace()
        if not ws then return end
        local windows = {}
        for _, win in ipairs(hl.get_windows()) do
            if win.workspace and win.workspace.id == ws.id and (not same_app or not active or win.class == active.class) then
                windows[#windows + 1] = win
            end
        end
        table.sort(windows, function(a, b) return a.address < b.address end)
        for i, win in ipairs(windows) do
            if active and win.address == active.address then
                dispatch(hl.dsp.focus({ window = windows[(i - 1 + (reverse and -1 or 1)) % #windows + 1] }))
                return
            end
        end
        if windows[1] then dispatch(hl.dsp.focus({ window = windows[1] })) end
    end
end

-- Workspace names retain the source desktop across config/theme reloads.
local function restore(prefix)
    local restored = false
    for _, win in ipairs(hl.get_windows()) do
        local id = win.workspace and win.workspace.name:match("^special:" .. prefix:gsub("(%W)", "%%%1") .. "(%d+)$")
        if id then
            dispatch(hl.dsp.window.move({ window = win, workspace = tonumber(id), follow = false }))
            restored = true
        end
    end
    return restored
end
local function show_desktop()
    if restore("frost-desktop-") then return end
    local ws = hl.get_active_workspace()
    if not ws then return end
    for _, win in ipairs(hl.get_windows()) do
        if win.workspace and win.workspace.id == ws.id then
            dispatch(hl.dsp.window.move({ window = win, workspace = "special:frost-desktop-" .. ws.id, follow = false }))
        end
    end
end
local function minimize()
    local win = hl.get_active_window()
    if win and win.workspace and win.workspace.id > 0 then
        dispatch(hl.dsp.window.move({ window = win, workspace = "special:frost-minimized-" .. win.workspace.id, follow = false }))
    end
end
local function snap(direction)
    return function()
        local win, mon = hl.get_active_window(), hl.get_active_monitor()
        if not win or not mon then return end
        local width, height = mon.width / mon.scale, mon.height / mon.scale
        local x, y, w, h = mon.x + 12, mon.y + 48, width - 24, height - 60
        if direction == "left" or direction == "right" then
            w = math.floor((width - 36) / 2)
            if direction == "right" then x = mon.x + width - w - 12 end
        else
            h = math.floor((height - 72) / 2)
            if direction == "down" then y = mon.y + height - h - 12 end
        end
        if not win.floating then dispatch(hl.dsp.window.float({ window = win })) end
        dispatch(hl.dsp.window.resize({ window = win, x = w, y = h, relative = false }))
        dispatch(hl.dsp.window.move({ window = win, x = x, y = y, relative = false }))
    end
end
for _, dir in ipairs({ "Left", "Right", "Up", "Down" }) do
    hl.unbind("SUPER + " .. dir)
    bind("SUPER + " .. dir, hl.dsp.focus({ direction = dir:lower() }))
    bind("SUPER + ALT + " .. dir, hl.dsp.focus({ direction = dir:lower() }))
end
for _, keys in ipairs({
    { "H", "Left", "left", -20, 0 },
    { "J", "Down", "down", 0, 20 },
    { "K", "Up", "up", 0, -20 },
    { "L", "Right", "right", 20, 0 },
}) do
    hl.unbind("SUPER + " .. keys[1])
    bind("SUPER + " .. keys[1], hl.dsp.focus({ direction = keys[3] }))
    for _, key in ipairs({ keys[1], keys[2] }) do
        hl.unbind("SUPER + CTRL + " .. key)
        hl.bind("SUPER + CTRL + " .. key,
            hl.dsp.window.resize({ x = keys[4], y = keys[5], relative = true }),
            { repeating = true })
    end
end
-- Direct lock/sleep shortcuts are deliberately disabled.
for _, key in ipairs({ "SUPER + ALT + L", "SUPER + SHIFT + L", "SUPER + CTRL + ALT + L",
    "XF86Sleep", "XF86Hibernate", "XF86ScreenSaver" }) do
    hl.unbind(key)
end
for _, key in ipairs({ "ALT + Tab", "SUPER + Tab" }) do bind(key, cycle(false, false)) end
for _, key in ipairs({ "ALT + SHIFT + Tab", "SUPER + SHIFT + Tab" }) do bind(key, cycle(true, false)) end
bind("ALT + grave", cycle(false, true)); bind("SUPER + grave", cycle(false, true))
bind("ALT + SHIFT + grave", cycle(true, true)); bind("SUPER + SHIFT + grave", cycle(true, true))
bind("SUPER + Z", run("rog-control-center"))
bind("SUPER + D", show_desktop)
bind("SUPER + Page_Up", hl.dsp.window.fullscreen({ mode = "maximized" }))
bind("SUPER + Page_Down", minimize)
bind("SUPER + BackSpace", function() restore("frost-minimized-") end)
for i = 1, 4 do
    bind("CTRL + F" .. i, hl.dsp.focus({ workspace = i }))
    bind("SUPER + F" .. i, hl.dsp.focus({ workspace = i }))
end
bind("SUPER + ALT + Return", run("foot"))
bind("SUPER + ALT + W", run("caelestia shell frostLauncher wallpapers"))
bind("SUPER + SHIFT + W", run("caelestia wallpaper -r --no-filter"))
bind("SHIFT + XF86AudioRaiseVolume", run("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 1%+"))
bind("SHIFT + XF86AudioLowerVolume", run("wpctl set-volume @DEFAULT_AUDIO_SINK@ 1%-"))
bind("SHIFT + XF86MonBrightnessUp", run("brightnessctl set +1%"))
bind("SHIFT + XF86MonBrightnessDown", run("brightnessctl set 1%-"))
bind("XF86KbdBrightnessUp", run("brightnessctl -d asus::kbd_backlight set +1"))
bind("XF86KbdBrightnessDown", run("brightnessctl -d asus::kbd_backlight set 1-"))
-- Float before a resize only when this is the workspace's sole window.
local function begin_resize()
    local win = hl.get_active_window()
    if not win then return end
    local count = 0
    for _, other in ipairs(hl.get_windows()) do
        if other.workspace and win.workspace and other.workspace.id == win.workspace.id then
            count = count + 1
        end
    end
    if not win.floating and count == 1 then
        dispatch(hl.dsp.window.float({ window = win }))
    end
    dispatch(hl.dsp.window.resize())
end
hl.unbind("SUPER + mouse:273")
hl.bind("SUPER + mouse:273", begin_resize, { mouse = true })

-- Expose callbacks for isolated IPC smoke tests, without exporting extra shortcuts.
FrostShortcuts = { begin_resize = begin_resize, show_desktop = show_desktop, minimize = minimize, restore = function() restore("frost-minimized-") end, snap_left = snap("left"), cycle = cycle(false, false) }
