# FROST_GPU_SHELL_HOOK_V1
if [ -r /usr/local/libexec/frost-gpu-interactive.sh ]; then . /usr/local/libexec/frost-gpu-interactive.sh; fi
#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

# Go module proxy — Google's proxy.golang.org is unreachable from China.
# goproxy.cn is a domestic mirror; falls back to direct VCS fetch.
export GOPROXY=https://goproxy.cn,direct
export GOSUMDB=sum.golang.google.cn

# Added by LM Studio CLI (lms)
export PATH="$PATH:/home/lookfrost/.lmstudio/apps/bionic/bin"
# End of LM Studio CLI section


# Keep normal cd paths and add zoxide's directory history matching.
if [[ $- == *i* ]] && command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init bash --cmd cd)"
    alias z=cd zi=cdi
fi
