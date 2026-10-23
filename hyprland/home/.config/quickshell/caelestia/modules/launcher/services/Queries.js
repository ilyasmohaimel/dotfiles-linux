.pragma library

// Plain-language aliases resolve to the shell's existing session actions.
function session(text) {
    const query = String(text).replace(/^\s+|\s+$/g, "").replace(/\s+/g, " ").toLowerCase();
    if (query.length < 2)
        return null;
    const actions = [
        { name: "Shutdown", word: "shutdown", aliases: ["shutdown", "shut down", "poweroff", "power off", "turn off"] },
        { name: "Reboot", word: "reboot", aliases: ["reboot", "restart"] },
        { name: "Logout", word: "log out", aliases: ["logout", "log out", "signout", "sign out", "exit session"] },
        { name: "Lock", word: "lock", aliases: ["lock", "lock screen", "lock session"] },
        { name: "Sleep", word: "sleep", aliases: ["sleep"] },
        { name: "Suspend", word: "suspend", aliases: ["suspend"] },
        { name: "Hibernate", word: "hibernate", aliases: ["hibernate", "hibernation"] }
    ];
    const matches = actions.filter(action => action.aliases.some(alias => alias.indexOf(query) === 0));
    if (!matches.length)
        return null;
    return matches.length === 1 ? { search: matches[0].name, word: matches[0].word } : { search: query, word: String(text) };
}

// Match only keyword prefixes, so names such as "themepark" remain app searches.
function keyword(text) {
    const match = String(text).replace(/^\s+/, "").match(/^(\S+)(?:\s+(.*))?$/);
    if (!match || match[1].length < 2)
        return null;
    const word = match[1].toLowerCase();
    for (const name of ["wallpapers", "themes", "schemes"]) {
        if (name.indexOf(word) === 0) {
            const label = name.slice(0, -1);
            return { action: name === "wallpapers" ? "wallpaper" : "scheme", label: label, filter: match[2] || "" };
        }
    }
    return null;
}

// Show results immediately, while leaving the user's typed text untouched.
function resolve(text, prefix) {
    const result = keyword(text);
    if (result)
        return prefix + result.action + " " + result.filter;
    const action = session(text);
    return action ? prefix + action.search : String(text);
}

function complete(text) {
    const result = keyword(text);
    if (result)
        return result.label + " " + result.filter;
    const action = session(text);
    return action ? action.word : String(text);
}
