$HOME/.local/bin/caelestia-foot-colors --stdout
function fish_greeting
    # The existing KDE Fish config already printed the fetch in this case.
    if set -q WEZTERM_EXECUTABLE; and test "$SHLVL" = 1
        return
    end
    if type -q fastfetch
        command fastfetch --config "$HOME/.config/caelestia/fastfetch.jsonc"
    end
end

set -gx STARSHIP_CONFIG "$HOME/.config/caelestia/starship.toml"
starship init fish | source

if type -q direnv
    direnv hook fish | source
end
function mark_prompt_start --on-event fish_prompt
    printf "\e]133;A\e\\"
end
