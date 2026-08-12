#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

export PATH="$HOME/.local/bin:$PATH"

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

# Show system info once when a graphical terminal opens.
if [[ -t 1 && ${SHLVL:-0} -eq 1 ]] && { [[ ${TERM_PROGRAM:-} == WezTerm ]] || [[ ${TERM:-} == alacritty ]]; }; then
    command fastfetch
fi
