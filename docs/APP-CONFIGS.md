# Restoring my app settings

The `kde/home/` folder is a mirror of my home directory. I can preview a restore first:

```sh
rsync -an kde/home/ "$HOME"/
```

Then I copy only the parts I want. Most apps should be closed before their config is replaced.

## Codex

`kde/home/.codex/` contains my portable Codex setup:

- `config.toml` for my model, desktop, MCP, plugin, and approval preferences
- `AGENTS.md`, default rules, and keybindings

It does not contain `auth.json`, `.credentials.json`, sessions, memories, SQLite state, logs, caches, or OAuth data. After restoring it, I log in again and authenticate any MCP server that needs it:

```sh
codex login
codex mcp login <server-name>
```

The Perplexity MCP entry intentionally has no API key. I add that privately when I need it instead of putting it in this repository.

## Vencord / Vesktop

`kde/home/.config/vesktop/` keeps my Vencord settings, enabled-plugin settings, Quick CSS, and Molten theme. It does not include Discord cookies, the account session, caches, or downloaded Vencord files.

I restore it with:

```sh
rsync -a kde/home/.config/vesktop/ "$HOME/.config/vesktop/"
```

Then I launch Vesktop and sign in normally.

## Other app settings

| App | Stored files |
| --- | --- |
| ChatGPT desktop | `kde/home/.config/chatgpt-flags.conf` |
| MangoHud | `kde/home/.config/MangoHud/MangoHud.conf` |
| Millennium | `kde/home/.config/millennium/config.json` and `quick.css` |
| VLC | `kde/home/.config/vlc/` |
| VS Code / VSCodium | `kde/home/.config/Code/User/` and `kde/home/.config/VSCodium/User/` |
| WezTerm / Konsole / Alacritty | Their folders under `kde/home/.config/` plus Konsole profiles under `kde/home/.local/share/konsole/` |

## Things I intentionally do not restore

I do not keep browser profiles, Discord or Steam login data, Bitwarden data, Heroic account data, KDE Connect certificates, SSH keys, OAuth tokens, caches, downloaded plugins, chat/session databases, or network-specific settings here. Those either contain credentials or are better recreated by signing in normally.
