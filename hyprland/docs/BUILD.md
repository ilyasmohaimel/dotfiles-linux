# Source pins and local builds

`manifests/upstream.json` records the exact commits present during the backup. `build/recipes/` preserves the PKGBUILDs used locally. These are historical recipes, not a portable one-command installation: three recipes point at `/home/lookfrost/.local/share/frost-hyprland-setup/sources/`.

To reconstruct the source layout on the original account, clone each URL from the manifest into that sources directory using the corresponding key (`dots`, `shell`, `cli`, `quickshell`, `m3shapes`, `spicetify`) and check out the recorded commit. Verify the commit before applying local changes.

For every matching file under `build/patches/`, run `git apply --check` in the appropriate source checkout, then apply the patch. Copy files from `build/overlays/<source>/` to the same relative paths in that checkout. The shell overlay includes the new ASUS power service. Keep the upstream license files.

Build packages as the normal user with the saved recipes. Review their dependencies and source directories before running `makepkg`; install resulting packages separately with the package manager. Native dependencies must match the Qt/Hyprland versions being used. The source snapshot does not promise future ABI compatibility and does not include package archives or built plugin binaries.

After installing matching packages, the home restore supplies the **complete installed QML tree**, which contains further local changes beyond the build-source patch: the GPU submenu, launcher query/completion and power actions, weather units and the screenshot/wallpaper integration. Keeping only the Git diff of the old build checkout would miss these installed changes.

The CLI and shell were built from compatible October 2026 revisions. Quickshell was pinned to `2b4501a282689792b62e94f3fb30d8f512324fe6`; M3Shapes was pinned to `32ad9ce328bb77ed349b40a3be10ee9ea610b8ab`. See the manifest for all full hashes. The installed Hyprland and dependency versions are in `manifests/package-versions.txt`.

This backup does not install the separate `/opt/frost-gpu` KDE migration stack. The app-route helpers retained in `system/` preserve existing launcher commands and use native routes outside that opt-in session. The Hyprland session selects the primary GPU at login using the laptop's AMD device paths. Review those paths for different hardware.
