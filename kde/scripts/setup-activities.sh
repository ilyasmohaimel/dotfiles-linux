#!/usr/bin/env bash

set -euo pipefail

activity_service=org.kde.ActivityManager
activity_path=/ActivityManager/Activities
activity_interface=org.kde.ActivityManager.Activities
wallpapers_dir="$HOME/Pictures/Wallpapers"

activity_ids() {
    busctl --user call "$activity_service" "$activity_path" "$activity_interface" ListActivities \
        | grep -oE '"[^"]+"' | tr -d '"'
}

activity_name() {
    busctl --user call "$activity_service" "$activity_path" "$activity_interface" ActivityName s "$1" \
        | sed -n 's/^s "\(.*\)"$/\1/p'
}

set_activity_info() {
    busctl --user call "$activity_service" "$activity_path" "$activity_interface" SetActivityName ss "$1" "$2" >/dev/null
    busctl --user call "$activity_service" "$activity_path" "$activity_interface" SetActivityDescription ss "$1" "$3" >/dev/null
    busctl --user call "$activity_service" "$activity_path" "$activity_interface" SetActivityIcon ss "$1" "$4" >/dev/null
}

ensure_activity() {
    local name=$1 description=$2 icon=$3 id

    while IFS= read -r id; do
        if [[ $(activity_name "$id") == "$name" ]]; then
            set_activity_info "$id" "$name" "$description" "$icon"
            printf '%s\n' "$id"
            return
        fi
    done < <(activity_ids)

    if [[ $name == Normal ]]; then
        while IFS= read -r id; do
            if [[ $(activity_name "$id") == Default ]]; then
                set_activity_info "$id" "$name" "$description" "$icon"
                printf '%s\n' "$id"
                return
            fi
        done < <(activity_ids)
    fi

    id=$(busctl --user call "$activity_service" "$activity_path" "$activity_interface" AddActivity s "$name" | sed -n 's/^s "\(.*\)"$/\1/p')
    set_activity_info "$id" "$name" "$description" "$icon"
    printf '%s\n' "$id"
}

set_wallpaper() {
    local activity_id=$1 image=$2 script

    [[ -f $image ]] || {
        printf 'Missing wallpaper: %s\n' "$image" >&2
        exit 1
    }

    script="var desktopsForThisActivity = desktopsForActivity(\"$activity_id\"); for (var i = 0; i < desktopsForThisActivity.length; i++) { var desktop = desktopsForThisActivity[i]; desktop.wallpaperPlugin = \"org.kde.image\"; desktop.currentConfigGroup = Array(\"Wallpaper\", \"org.kde.image\", \"General\"); desktop.writeConfig(\"Image\", \"file://$image\"); desktop.writeConfig(\"FillMode\", 2); desktop.reloadConfig(); }"
    qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$script" >/dev/null
}

normal_id=$(ensure_activity Normal 'My normal desktop' user-home)
coding_id=$(ensure_activity Coding 'Coding and development' applications-development)
gaming_id=$(ensure_activity Gaming 'Gaming and media' applications-games)

set_wallpaper "$normal_id" "$wallpapers_dir/midpoint.png"
set_wallpaper "$coding_id" "$wallpapers_dir/thick-forest-3840x2160-14776.jpg"
set_wallpaper "$gaming_id" "$wallpapers_dir/Firewatch/0.jpg"

busctl --user call "$activity_service" "$activity_path" "$activity_interface" SetCurrentActivity s "$normal_id" >/dev/null
busctl --user call "$activity_service" "$activity_path" "$activity_interface" ListActivitiesWithInformation
