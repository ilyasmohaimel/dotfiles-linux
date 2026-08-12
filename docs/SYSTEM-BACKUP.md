# Backing up and restoring my whole system

This repository is for safe, readable configuration. It is not a full backup: it intentionally leaves out keys, logins, personal files, databases, browser profiles, and app sessions.

For a real recovery plan, I keep three separate backups:

1. This Git repository for configs, package lists, and setup notes.
2. An encrypted system backup for `/`, `/home`, and `/boot`.
3. A separate copy of personal files and projects, including anything too private or too large for Git.

## My disk layout

At the time this was written, the system uses separate ext4 partitions for `/` and `/home`, plus a FAT EFI partition mounted at `/boot`:

```text
/dev/nvme0n1p1  vfat  /boot
/dev/nvme0n1p2  ext4  /
/dev/nvme0n1p3  ext4  /home
```

That means I back up all three. Backing up only `/` will not save my home directory, and backing up only `/home` will not save the operating system or boot files.

## Backup destination

For a restorable Linux system backup, I use a Linux filesystem such as ext4 on an external disk, or an encrypted Borg repository on a server that preserves Unix ownership, ACLs, xattrs, and hard links.

My mounted Toshiba disk is NTFS, so I do not use it as the only full-system backup. NTFS cannot reliably preserve the Linux metadata needed for an exact restore. It is fine for an extra copy of personal media or archives.

## Borg backup setup

Borg is the tool I would use for the full backup because it is encrypted, deduplicated, and keeps history. Install it once:

```sh
sudo pacman -S --needed borg
```

Choose an external ext4 disk mounted at a stable path, then create an encrypted repository. Replace the example path with the actual backup disk path:

```sh
export BACKUP_REPO=/mnt/backup-disk/borg/arch-kde
sudo borg init --encryption=repokey-blake2 "$BACKUP_REPO"
```

I keep the Borg passphrase and exported key outside this repository, in my password manager and another safe place:

```sh
sudo borg key export "$BACKUP_REPO" ~/Documents/borg-arch-kde-key.txt
```

The exported key is sensitive. I do not commit it, upload it publicly, or leave the only copy on the same disk as the backup.

## Creating a backup

I close apps that write important databases first. Then I run separate archives for the system, home, and EFI partition:

```sh
export BACKUP_REPO=/mnt/backup-disk/borg/arch-kde

sudo borg create --stats --compression zstd,6 --one-file-system \
  "$BACKUP_REPO"::'{hostname}-{now:%Y-%m-%dT%H:%M}-root' / \
  --exclude /dev --exclude /proc --exclude /sys --exclude /run \
  --exclude /tmp --exclude /mnt --exclude /media --exclude /lost+found

sudo borg create --stats --compression zstd,6 \
  "$BACKUP_REPO"::'{hostname}-{now:%Y-%m-%dT%H:%M}-home' /home

sudo borg create --stats --compression zstd,6 \
  "$BACKUP_REPO"::'{hostname}-{now:%Y-%m-%dT%H:%M}-boot' /boot
```

Afterwards, I verify the repository and inspect the new archives:

```sh
sudo borg check --verify-data "$BACKUP_REPO"
sudo borg list "$BACKUP_REPO"
```

For retention, I keep recent daily backups, several weekly backups, and a few monthly backups:

```sh
sudo borg prune --keep-daily 7 --keep-weekly 4 --keep-monthly 6 "$BACKUP_REPO"
sudo borg compact "$BACKUP_REPO"
```

I do not automate deletion until I have successfully restored or mounted an archive at least once.

## Restoring after a disk failure

1. Boot an Arch ISO and connect the backup disk.
2. Recreate or mount the EFI, root, and home partitions.
3. Mount root at `/mnt`, home at `/mnt/home`, and EFI at `/mnt/boot`.
4. Extract the matching root, home, and boot archives into those mounts.
5. `arch-chroot /mnt`, regenerate initramfs, reinstall/configure the bootloader if needed, and verify `/etc/fstab`.
6. Reboot, then restore only the app settings I want from this Git repository.

The important part is restoring root, home, and boot from the same backup run. Mixing different dates can leave packages, kernel modules, and home-state databases out of sync.

## Fast rebuild instead of full restore

If the disk is healthy and I only want a clean reinstall, I can install Arch normally, use the package manifests in `kde/manifests/`, restore selected configs from this repo, and follow the GPU guide. I still sign back into browsers, password managers, Discord, Steam, Codex, and MCP servers instead of restoring their session data.
