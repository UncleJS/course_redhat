# NFS Client Mounts and automount
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Network File System (NFS) lets a RHEL client mount a remote export as a local
directory. For boot-time mounts use fstab with `_netdev`. For on-demand home
or project shares, **autofs** mounts only when accessed. This chapter covers
the **client** side (exporting from a server is a separate role).

Install client tools:

```bash
sudo dnf install -y nfs-utils autofs
```

---
<a name="toc"></a>

## Table of contents

- [Manual NFS mount](#manual-nfs-mount)
- [Persistent mounts in fstab](#persistent-mounts-in-fstab)
- [autofs indirect maps](#autofs-indirect-maps)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)
- [Further reading](#further-reading)
- [Next step](#next-step)


## Manual NFS mount

```bash
# Discover exports (if allowed by server)
showmount -e nfs.lab.example

sudo mkdir -p /mnt/nfsdata
sudo mount -t nfs nfs.lab.example:/export/data /mnt/nfsdata

# Verify
mount | grep nfs
df -h /mnt/nfsdata
```

Use NFSv4 by default on modern RHEL when talking to a RHEL NFS server.
Options like `rw`, `ro`, and `vers=4.2` can be passed with `-o`.


[↑ Back to TOC](#toc)

---

## Persistent mounts in fstab

```bash
sudo vim /etc/fstab
```

```text
nfs.lab.example:/export/data  /mnt/nfsdata  nfs  defaults,_netdev  0  0
```

`_netdev` tells systemd to wait for the network before mounting — required
for reliable boot. Then:

```bash
sudo systemctl daemon-reload
sudo mount -a
```


[↑ Back to TOC](#toc)

---

## autofs indirect maps

```bash
sudo dnf install -y autofs
sudo systemctl enable --now autofs
```

Master map includes the default `auto.master`. Add an indirect map, for
example under `/misc`:

```bash
# /etc/auto.master.d/misc.autofs
/misc   /etc/auto.misc
```

```bash
# /etc/auto.misc  (example entry)
data   -rw,soft,intr  nfs.lab.example:/export/data
```

```bash
sudo systemctl reload autofs
ls /misc/data          # triggers mount
mount | grep /misc/data
```

When the directory is idle, autofs unmounts after a timeout.


[↑ Back to TOC](#toc)

---

## Worked example

Assume a lab NFS server exports `/exports/shared` as `192.168.122.50:/exports/shared`:

```bash
sudo mkdir -p /mnt/shared
echo "192.168.122.50:/exports/shared  /mnt/shared  nfs  defaults,_netdev  0  0" \
  | sudo tee -a /etc/fstab
sudo systemctl daemon-reload
sudo mount /mnt/shared
touch /mnt/shared/hello-from-$(hostname)
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| Missing `_netdev` | Boot hangs waiting for NFS | Add `_netdev`; use `x-systemd.automount` if needed |
| Firewall blocks NFS | `mount.nfs: Connection timed out` | Open NFS ports on **server**; check `firewall-cmd` |
| Wrong export path | Access denied / no such file | `showmount -e` and compare export |
| SELinux on home dirs | AVC on NFS home | See NFS SELinux booleans; label carefully |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Managing file systems: NFS](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_file_systems/index) | Client and server NFS |
| [`autofs` man page](https://man7.org/linux/man-pages/man8/automount.8.html) | automount daemon |
| [`fstab` `_netdev`](https://man7.org/linux/man-pages/man5/fstab.5.html) | Network mount option |


[↑ Back to TOC](#toc)

---

## Next step

→ [Time sync with chrony](17-time-chrony.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
