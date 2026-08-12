if status is-interactive
    set -g fish_greeting

    set -g fish_color_normal '#ffffff'
    set -g fish_color_command '#ffffff' --bold
    set -g fish_color_keyword '#ff5a1f' --bold
    set -g fish_color_param '#ffffff'
    set -g fish_color_quote '#25d9e8'
    set -g fish_color_redirection '#ff5a1f'
    set -g fish_color_end '#ff5a1f'
    set -g fish_color_error '#d8141c' --bold
    set -g fish_color_comment '#80666a'
    set -g fish_color_operator '#ff5a1f'
    set -g fish_color_escape '#25d9e8'
    set -g fish_color_autosuggestion '#80666a'
    set -g fish_color_selection --background='#b0000a' '#ffffff'
    set -g fish_pager_color_prefix '#ff5a1f' --bold
    set -g fish_pager_color_completion '#ffffff'
    set -g fish_pager_color_description '#bdaaaa'
    set -g fish_pager_color_selected_background --background='#b0000a'
    set -g fish_pager_color_selected_completion '#ffffff'
    set -g fish_pager_color_selected_description '#ffffff'

    fish_add_path $HOME/.local/bin

    abbr -a -- ll 'eza -lah --group-directories-first --icons=auto'
    abbr -a -- la 'eza -a --group-directories-first --icons=auto'
    abbr -a -- lt 'eza --tree --level=2 --group-directories-first --icons=auto'
    abbr -a -- cat bat
    abbr -a -- gs 'git status'
    abbr -a -- gd 'git diff'
    abbr -a -- gl 'git log --oneline --graph --decorate -12'
    abbr -a -- lg lazygit
    abbr -a -- top btop
    abbr -a -- .. 'cd ..'
    abbr -a -- ... 'cd ../..'

    function which
        type -a $argv
    end

    function reload
        source ~/.config/fish/config.fish
    end

    zoxide init fish | source
    starship init fish | source

    set -gx FZF_DEFAULT_OPTS '--height 40% --layout=reverse --border --info=inline --color=bg+:#220b0c,bg:#070505,spinner:#ff5a1f,hl:#ff5a1f --color=fg:#ffffff,header:#ff5a1f,info:#ffffff,pointer:#d8141c,marker:#ff5a1f,fg+:#ffffff,prompt:#ff5a1f,hl+:#25d9e8'

    bind up history-search-backward
    bind down history-search-forward
    bind \cf accept-autosuggestion
    bind \cd delete-or-exit
    bind \cw backward-kill-word
    bind \e\[1\;5D backward-word
    bind \e\[1\;5C forward-word

    if set -q WEZTERM_EXECUTABLE; or test "$TERM" = alacritty
        if test "$SHLVL" = 1
            fastfetch
        end
    end
end
