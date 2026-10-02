# Archives and Compression — tar, gzip, xz
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Packaging files into a single archive and compressing them is an everyday
admin skill: backups, log bundles, software drops, and exam tasks all use
`tar` with `gzip` or `xz`. On RHEL, GNU tar is always available on a minimal
install; compression helpers come from `gzip` and `xz` packages.

An **archive** concatenates many files (and directory trees) into one stream
or file. **Compression** shrinks that stream. You can combine both in one
step (`tar czf`, `tar cJf`) or keep them separate. Prefer preserving
ownership and permissions when moving system trees between hosts.

---
<a name="toc"></a>

## Table of contents

- [Create and list archives](#create-and-list-archives)
- [Extract archives](#extract-archives)
- [gzip and xz alone](#gzip-and-xz-alone)
- [Preserve ownership and SELinux contexts](#preserve-ownership-and-selinux-contexts)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)
- [Further reading](#further-reading)
- [Next step](#next-step)


## Create and list archives

```bash
# Create a gzip-compressed tarball (most common)
tar czf /tmp/etc-backup.tar.gz -C / etc

# Create an xz-compressed tarball (smaller, slower)
tar cJf /tmp/var-log.tar.xz -C /var log

# Uncompressed tar
tar cf /tmp/home-student.tar -C /home student

# List contents without extracting
tar tzf /tmp/etc-backup.tar.gz | head
tar tJf /tmp/var-log.tar.xz | head
```

Flags: `c` create, `t` list, `x` extract, `f` file, `z` gzip, `J` xz,
`v` verbose. Order of short flags is flexible; keep `f` immediately before
the archive path.


[↑ Back to TOC](#toc)

---

## Extract archives

```bash
# Extract into the current directory
mkdir -p ~/restore && cd ~/restore
tar xzf /tmp/etc-backup.tar.gz

# Extract to an explicit directory
tar xzf /tmp/etc-backup.tar.gz -C /tmp/restore-etc

# Extract one path from the archive
tar xzf /tmp/etc-backup.tar.gz -C /tmp etc/hosts
```

> **Exam tip:** Always inspect with `tar t` before extracting as root into
> `/`. Malicious or misplaced archives can overwrite system files.


[↑ Back to TOC](#toc)

---

## gzip and xz alone

```bash
# Compress a single file (replaces original with .gz / .xz)
gzip large.log
xz large.csv

# Keep the original (-k / --keep)
gzip -k large.log
xz -k large.csv

# Decompress
gunzip large.log.gz
unxz large.csv.xz

# Stream compress (pipeline)
journalctl -u sshd --since today | gzip > sshd-today.log.gz
```


[↑ Back to TOC](#toc)

---

## Preserve ownership and SELinux contexts

```bash
# As root: preserve numeric UID/GID when extracting on another host
sudo tar xzf backup.tar.gz --numeric-owner -C /

# Include SELinux contexts in the archive (GNU tar)
sudo tar czf selinux-etc.tar.gz --selinux -C / etc

# Restore contexts after extract if needed
sudo restorecon -RFv /etc
```


[↑ Back to TOC](#toc)

---

## Worked example

Bundle `/var/log` for offsite analysis, verify, and extract a single file:

```bash
sudo tar czf /tmp/varlog-$(date +%F).tar.gz -C /var log
tar tzf /tmp/varlog-$(date +%F).tar.gz | grep messages | head
mkdir -p /tmp/log-peek
tar xzf /tmp/varlog-$(date +%F).tar.gz -C /tmp/log-peek log/messages
ls -l /tmp/log-peek/log/messages
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| Forgot compression flag | Huge `.tar` or "not in gzip format" | Match `z`/`J` on create and extract |
| Extracted in the wrong cwd | Files land in unexpected places | Use `-C /target` or `cd` first |
| Tar as non-root loses owners | Extracted files owned by you | Extract as root; use `--numeric-owner` when needed |
| Absolute paths in archive | Surprise overwrite under `/` | Prefer `-C` + relative paths when creating |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`tar` man page](https://man7.org/linux/man-pages/man1/tar.1.html) | GNU tar options including `--selinux` |
| [`gzip` man page](https://man7.org/linux/man-pages/man1/gzip.1.html) | gzip / gunzip |
| [`xz` man page](https://man7.org/linux/man-pages/man1/xz.1.html) | xz / unxz |


[↑ Back to TOC](#toc)

---

## Next step

→ [Pipes and Redirection](03-pipes-redirection.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
