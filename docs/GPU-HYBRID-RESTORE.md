# My Intel + NVIDIA hybrid GPU setup

This is how I set up graphics on my HP Pavilion 15-cs0xxx. The Intel UHD 620 runs the desktop to keep power use and heat down. The NVIDIA MX150 is there for games and heavier apps through PRIME offload. I do not run the whole desktop on NVIDIA.

Before installing anything, I check that the machine really has the same GPUs:

```sh
lspci -nnk | rg -A3 'VGA|3D|Display'
```

I should see Intel UHD 620 (`8086:5917`) and NVIDIA MX150 (`10de:1d10`).

## Packages

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

I start with a full update, then install the repository packages:

```sh
sudo pacman -Syu --needed linux linux-headers nvidia-prime switcheroo-control mesa mesa-utils vulkan-tools vulkan-intel lib32-vulkan-intel
```

Then I install the matching AUR driver packages:

```sh
yay -S --needed nvidia-580xx-dkms nvidia-580xx-utils lib32-nvidia-580xx-utils
```

The kernel, kernel headers, DKMS module, and NVIDIA user-space packages need to match. If the 580xx packages no longer build on the current kernel, I check the package maintainers' compatibility notes instead of swapping in the normal `nvidia` package or an NVIDIA `.run` installer.

## Boot configuration

My [`mkinitcpio.conf`](../kde/etc/mkinitcpio.conf) uses this module order:

```sh
MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)
```

The `kms` hook is intentionally absent. After putting that setting in `/etc/mkinitcpio.conf`, I rebuild the initramfs and enable the hybrid-GPU service:

```sh
sudo mkinitcpio -P
sudo systemctl enable --now switcheroo-control.service
sudo reboot
```

## Running an app on NVIDIA

The normal desktop stays on Intel. These commands run an app on the MX150:

```sh
prime-run steam
prime-run mangohud steam
prime-run obs
prime-run brave
```

The KDE profile includes NVIDIA launchers for Steam, Brave, Discord, OBS, VS Code, and Zen Browser. [`steam.desktop`](../kde/home/.local/share/applications/steam.desktop) also sends normal Steam launches through `prime-run`.

For a new desktop entry, I keep the normal command and add `prime-run` in front of `Exec=`:

```ini
Exec=prime-run app-name %U
X-KDE-RunOnDiscreteGpu=true
```

## Checking that it worked

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

What I expect to see:

- `nvidia`, `nvidia_modeset`, `nvidia_uvm`, and `nvidia_drm` are loaded.
- `nouveau` is not loaded.
- `nvidia-smi` identifies the MX150 and the installed NVIDIA driver version.
- Normal `glxinfo -B` says Intel UHD 620 / Mesa.
- `prime-run glxinfo -B` says NVIDIA MX150 / NVIDIA driver.
- Normal Vulkan prefers Intel; `prime-run vulkaninfo --summary` puts NVIDIA first.
- `switcheroo-control.service` is active and `switcherooctl list` identifies Intel as default and NVIDIA as discrete.

## If an update breaks it

- If DKMS fails, I check that `linux-headers` matches `uname -r`, then rebuild with `sudo dkms autoinstall -k "$(uname -r)"` and regenerate initramfs.
- If the desktop starts using NVIDIA by default, I look for a global PRIME/offload environment variable or desktop entry override and remove it. This setup is meant to be selective.
- If `nvidia-smi` works but OpenGL or Vulkan does not, I run fresh `prime-run glxinfo -B` and `prime-run vulkaninfo --summary` checks before changing the package stack.
- If a new kernel breaks the driver, I boot the last working kernel from the boot menu, then fix the DKMS/package mismatch before trying the newer kernel again.
