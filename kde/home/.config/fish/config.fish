if status is-interactive
    set -g fish_greeting

    set -l lookfrost_activity Normal
    if test -r "$HOME/.config/lookfrost/active-activity"
        read -l lookfrost_activity < "$HOME/.config/lookfrost/active-activity"
    end

    switch $lookfrost_activity
        case Coding
            set -l accent '#DBA96B'; set -l accent2 '#FBF6A0'; set -l selection '#935741'; set -l muted '#515850'; set -l background '#181D1C'
        case Gaming
            set -l accent '#FFB21A'; set -l accent2 '#FF5A1F'; set -l selection '#B0000A'; set -l muted '#80666A'; set -l background '#070505'
        case '*'
            set lookfrost_activity Normal
            set -l accent '#B09C6D'; set -l accent2 '#7399BB'; set -l selection '#2F3233'; set -l muted '#666C63'; set -l background '#1E1E26'
    end

    set -g fish_color_normal '#FFFFFF'
    set -g fish_color_command '#FFFFFF' --bold
    set -g fish_color_keyword $accent --bold
    set -g fish_color_param '#FFFFFF'
    set -g fish_color_quote $accent2
    set -g fish_color_redirection $accent
    set -g fish_color_end $accent
    set -g fish_color_error '#D8141C' --bold
    set -g fish_color_comment $muted
    set -g fish_color_operator $accent
    set -g fish_color_escape $accent2
    set -g fish_color_autosuggestion $muted
    set -g fish_color_selection --background=$selection '#FFFFFF'
    set -g fish_pager_color_prefix $accent --bold
    set -g fish_pager_color_completion '#FFFFFF'
    set -g fish_pager_color_description $muted
    set -g fish_pager_color_selected_background --background=$selection
    set -g fish_pager_color_selected_completion '#FFFFFF'
    set -g fish_pager_color_selected_description '#FFFFFF'

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

    set -gx FZF_DEFAULT_OPTS "--height 40% --layout=reverse --border --info=inline --color=bg+:$background,bg:$background,spinner:$accent,hl:$accent --color=fg:#FFFFFF,header:$accent,info:#FFFFFF,pointer:#D8141C,marker:$accent,fg+:#FFFFFF,prompt:$accent,hl+:$accent2"
    set -gx STARSHIP_CONFIG "$HOME/.config/starship/$lookfrost_activity.toml"

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
