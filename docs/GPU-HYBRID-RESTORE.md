# Restoring my Intel + NVIDIA hybrid GPU setup

This is the setup for my HP Pavilion 15-cs0xxx laptop: Intel UHD 620 is the normal desktop GPU, and the NVIDIA MX150 is used only when I launch an app with PRIME offload. The goal is not to force NVIDIA for the whole desktop.

## What a future agent should do

1. Read this file and inspect the current system before changing anything.
2. Confirm the machine has Intel UHD 620 (`8086:5917`) and NVIDIA MX150 (`10de:1d10`) with `lspci -nnk`.
3. Fully update Arch first, then install the matching driver stack. Never mix kernel headers, DKMS modules, and NVIDIA user-space packages from different driver versions.
4. Preserve the Intel desktop path. Use `prime-run` only for games and heavier apps.
5. Rebuild initramfs, reboot, then run every verification command below. Do not call the job done based only on package installation.

## Package stack

I used this working stack on 2026-08-12:

```text
linux                         7.1.6.arch1-1
linux-headers                 7.1.6.arch1-1
nvidia-580xx-dkms             580.173.02-1
nvidia-580xx-utils            580.173.02-1
lib32-nvidia-580xx-utils      580.173.02-1
nvidia-prime                  1.0-6
switcheroo-control            3.0-1
mesa                          1:26.1.6-1
mesa-utils                    9.0.0-7
vulkan-tools                  1.4.357.0-1
vulkan-intel                  1:26.1.6-1
lib32-vulkan-intel            1:26.1.6-1
```

`nvidia-580xx-dkms`, `nvidia-580xx-utils`, and `lib32-nvidia-580xx-utils` are AUR packages. The remaining packages come from Arch repositories.

Install the repository packages first:

```sh
sudo pacman -Syu --needed linux linux-headers nvidia-prime switcheroo-control mesa mesa-utils vulkan-tools vulkan-intel lib32-vulkan-intel
```

Then use the AUR helper already installed on the system:

```sh
yay -S --needed nvidia-580xx-dkms nvidia-580xx-utils lib32-nvidia-580xx-utils
```

If the 580xx packages no longer build on the current kernel, stop there and check the package maintainers' current compatibility notes. Do not silently replace this setup with the regular `nvidia` packages or install a random `.run` driver.

## Boot setup

The checked-in [`mkinitcpio.conf`](../kde/etc/mkinitcpio.conf) has this exact module order:

```sh
MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)
```

The `kms` hook is intentionally absent. After merging that setting into `/etc/mkinitcpio.conf`:

```sh
sudo mkinitcpio -P
sudo systemctl enable --now switcheroo-control.service
sudo reboot
```

## PRIME offload

The normal desktop should stay on Intel. These commands run one app on the MX150:

```sh
prime-run steam
prime-run mangohud steam
prime-run obs
prime-run brave
```

The current KDE profile includes launchers for Steam, Brave, Discord, OBS, VS Code, and Zen Browser. `kde/home/.local/share/applications/steam.desktop` also makes normal Steam launches use `prime-run`.

For a new desktop entry, keep the app's normal command and prepend `prime-run` to `Exec=`:

```ini
Exec=prime-run app-name %U
X-KDE-RunOnDiscreteGpu=true
```

## Verification after reboot

Run all of this from a terminal:

```sh
uname -r
dkms status
lsmod | rg 'nvidia|nouveau'
lspci -nnk | rg -A3 'VGA|3D|Display'
nvidia-smi
glxinfo -B
prime-run glxinfo -B
vulkaninfo --summary
prime-run vulkaninfo --summary
systemctl is-active switcheroo-control.service
switcherooctl list
```

Expected result:

- `nvidia`, `nvidia_modeset`, `nvidia_uvm`, and `nvidia_drm` are loaded.
- `nouveau` is not loaded.
- `nvidia-smi` identifies the MX150 and the installed NVIDIA driver version.
- Normal `glxinfo -B` says Intel UHD 620 / Mesa.
- `prime-run glxinfo -B` says NVIDIA MX150 / NVIDIA driver.
- Normal Vulkan prefers Intel; `prime-run vulkaninfo --summary` puts NVIDIA first.
- `switcheroo-control.service` is active and `switcherooctl list` identifies Intel as default and NVIDIA as discrete.

## If something breaks

- If DKMS fails, check that `linux-headers` matches `uname -r`, then rebuild with `sudo dkms autoinstall -k "$(uname -r)"` and regenerate initramfs.
- If the desktop runs on NVIDIA by default, inspect the desktop entries and environment for a global PRIME/offload variable. Remove the global override; this setup is intended to be selective.
- If NVIDIA works in `nvidia-smi` but not in OpenGL/Vulkan, test a fresh `prime-run glxinfo -B` and `prime-run vulkaninfo --summary` before changing package stacks.
- If a new kernel breaks the driver, boot the previous working kernel from the bootloader, then fix the DKMS/package mismatch before trying the new one again.
