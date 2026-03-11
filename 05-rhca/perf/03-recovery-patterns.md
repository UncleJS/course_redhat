
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Recovery Patterns
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

## Overview

This chapter covers the systematic recovery procedures an RHCA-level administrator must execute under pressure: boot failures, corrupted filesystems, forgotten root passwords, broken SELinux contexts, and unresponsive systemd services. Each pattern follows a Diagnose → Recover → Verify → Prevent structure.


[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [Overview](#overview)
- [Pattern 1 — Root Password Reset (RHEL 10)](#pattern-1-root-password-reset-rhel-10)
  - [Procedure](#procedure)
- [Pattern 2 — Emergency and Rescue Targets](#pattern-2-emergency-and-rescue-targets)
  - [Emergency target](#emergency-target)
  - [Rescue target](#rescue-target)
  - [Recovery decision tree](#recovery-decision-tree)
- [Pattern 3 — Filesystem Corruption Recovery](#pattern-3-filesystem-corruption-recovery)
  - [Detecting corruption](#detecting-corruption)
  - [XFS recovery](#xfs-recovery)
  - [ext4 recovery](#ext4-recovery)
  - [LVM volume not appearing](#lvm-volume-not-appearing)
- [Pattern 4 — Broken SELinux Context Recovery](#pattern-4-broken-selinux-context-recovery)
  - [Relabel a specific file or directory](#relabel-a-specific-file-or-directory)
  - [Relabel a non-standard path](#relabel-a-non-standard-path)
  - [Full system relabel](#full-system-relabel)
  - [SELinux in permissive mode left over from troubleshooting](#selinux-in-permissive-mode-left-over-from-troubleshooting)
- [Pattern 5 — Unresponsive systemd Service](#pattern-5-unresponsive-systemd-service)
  - [Diagnose](#diagnose)
  - [Clear a start-limit and restart](#clear-a-start-limit-and-restart)
  - [Force-kill a stuck service](#force-kill-a-stuck-service)
  - [Service hangs on stop (taking too long)](#service-hangs-on-stop-taking-too-long)
  - [Broken unit file — system won't boot past a target](#broken-unit-file-system-wont-boot-past-a-target)
- [Pattern 6 — Boot to Last Known Good Kernel](#pattern-6-boot-to-last-known-good-kernel)
- [Pattern 7 — Network Unreachable After Config Change](#pattern-7-network-unreachable-after-config-change)
- [Pattern 8 — Disk Full Recovery](#pattern-8-disk-full-recovery)
- [Recovery Runbook Template](#recovery-runbook-template)
- [Recovery - <Scenario Name>](#recovery-scenario-name)
  - [Steps](#steps)
  - [Post-recovery](#post-recovery)
  - [Escalation](#escalation)
- [Recap](#recap)


## Pattern 1 — Root Password Reset (RHEL 10)

Use when: locked out of root account, no sudo access from any other user.

### Procedure

**1. Interrupt the boot at GRUB**

At the GRUB menu, press `e` to edit the default boot entry.

**2. Edit the kernel command line**

Find the line beginning with `linux` and add `rd.break` at the end:

```
linux /vmlinuz-... root=/dev/vda3 ro ... rd.break
```

Press `Ctrl+X` to boot with this parameter.

**3. In the initramfs emergency shell**

```bash
# Remount the real root filesystem read-write
switch_root:/# mount -o remount,rw /sysroot

# Chroot into the real filesystem
switch_root:/# chroot /sysroot

# Reset the root password
sh-5.1# passwd root
New password:
Retype new password:
passwd: all authentication tokens updated successfully.

# CRITICAL: tell SELinux to relabel all files on next boot
sh-5.1# touch /.autorelabel

# Exit chroot and the shell
sh-5.1# exit
switch_root:/# exit
```

The system will perform an SELinux relabel (takes 2–5 minutes on a full disk), then reboot normally.

> **Why `/.autorelabel`?** The `passwd` command was run outside of a running SELinux context. Without relabeling, the `/etc/shadow` file may have the wrong label and logins will fail with a PAM SELinux error.


[↑ Back to TOC](#toc)

---

## Pattern 2 — Emergency and Rescue Targets

### Emergency target

The most minimal boot — mounts only the root filesystem read-only, no services.

```bash
# Boot into emergency target from GRUB:
# Append to kernel line:
systemd.unit=emergency.target

# In the emergency shell, remount root rw to make changes:
# mount -o remount,rw /
```

### Rescue target

Starts a minimal set of services (filesystems mounted, no network). Good for diagnosing service failures that prevent normal boot.

```bash
# Boot into rescue target:
systemd.unit=rescue.target

# Or from a running system:
$ sudo systemctl isolate rescue.target
```

### Recovery decision tree

```
System won't boot normally
  ├── Reaches GRUB? → Yes → use rd.break or systemd.unit=emergency.target
  │                   No  → boot from RHEL install media → Troubleshoot mode
  ├── Mounts root?  → No  → filesystem corruption → see Pattern 3
  └── Fails in service start → journalctl -b -1 -p err → disable failing unit
```


[↑ Back to TOC](#toc)

---

## Pattern 3 — Filesystem Corruption Recovery

### Detecting corruption

```bash
# XFS metadata errors in the kernel journal
$ journalctl -k | grep -i "XFS\|filesystem error\|I/O error"

# Mount failure on boot
$ journalctl -b | grep "mount\|fsck\|EXT4\|XFS" | grep -i "err\|fail"
```

### XFS recovery

XFS is self-healing via its journal (log). Manual `fsck` is rarely needed. The tool is `xfs_repair`.

```bash
# UNMOUNT the filesystem first (or use rescue target if it's the root fs)
$ sudo umount /dev/vda3

# Replay the journal (attempt #1 — usually sufficient)
$ sudo xfs_repair /dev/vda3

# If xfs_repair says "Dirty log — use -L to force log zeroing"
# This LOSES in-flight transactions but gets the FS mountable
$ sudo xfs_repair -L /dev/vda3

# Remount and verify
$ sudo mount /dev/vda3 /mountpoint
$ df -h /mountpoint
```

> **XFS cannot be repaired while mounted.** If it is the root filesystem, boot from `emergency.target` (root is mounted read-only) or use RHEL install media.

### ext4 recovery

```bash
$ sudo umount /dev/vdb1
$ sudo fsck.ext4 -y /dev/vdb1   # -y = answer yes to all questions
$ sudo mount /dev/vdb1 /mountpoint
```

### LVM volume not appearing

```bash
# Scan for volume groups
$ sudo vgscan --mknodes
$ sudo vgchange -ay   # activate all VGs

# If PV is missing (degraded mirror or failed disk)
$ sudo pvs
  WARNING: Couldn't find device with uuid ...
  /dev/vdb: open failed: No such file or directory
$ sudo vgreduce --removemissing <vgname>
```


[↑ Back to TOC](#toc)

---

## Pattern 4 — Broken SELinux Context Recovery

When files have wrong or missing SELinux labels, services fail with AVC denials.

### Relabel a specific file or directory

```bash
# Restore default context based on fcontext database
$ sudo restorecon -Rv /var/www/html/

# Verify
$ ls -Z /var/www/html/
system_u:object_r:httpd_sys_content_t:s0  index.html
```

### Relabel a non-standard path

```bash
# Add a permanent fcontext rule first
$ sudo semanage fcontext -a -t httpd_sys_content_t '/srv/web(/.*)?'

# Then relabel (semanage alone does NOT relabel existing files)
$ sudo restorecon -Rv /srv/web/
```

### Full system relabel

For situations where large swaths of the filesystem have wrong labels:

```bash
# Option 1: Trigger relabel on next boot
$ sudo touch /.autorelabel
$ sudo reboot
# System relabels all files, then reboots — allow 5–15 minutes

# Option 2: Relabel interactively without reboot (very slow on large filesystems)
$ sudo restorecon -Rv /
```

### SELinux in permissive mode left over from troubleshooting

```bash
# Check current mode
$ getenforce
Permissive   ← this should not persist in production

# Return to enforcing
$ sudo setenforce 1

# Verify it will be enforcing after reboot
$ grep SELINUX= /etc/selinux/config
SELINUX=enforcing
```

> **Never leave `SELINUX=permissive` in `/etc/selinux/config` as a fix.** It disables MAC for the entire system permanently.


[↑ Back to TOC](#toc)

---

## Pattern 5 — Unresponsive systemd Service

### Diagnose

```bash
# What is the service's current state?
$ systemctl status myapp.service

# Full journal for the service (last 50 lines)
$ journalctl -u myapp.service -n 50

# Is it stuck in a start loop?
$ systemctl show myapp.service | grep -E "ActiveState|SubState|Result|NRestarts"
ActiveState=activating
NRestarts=15
Result=start-limit-hit
```

### Clear a start-limit and restart

```bash
# If Result=start-limit-hit, reset the rate limit counter
$ sudo systemctl reset-failed myapp.service
$ sudo systemctl start myapp.service
```

### Force-kill a stuck service

```bash
# Send SIGTERM first
$ sudo systemctl kill --signal=SIGTERM myapp.service

# If still stuck after a few seconds, SIGKILL
$ sudo systemctl kill --signal=SIGKILL myapp.service

# Confirm it stopped
$ systemctl is-active myapp.service
inactive
```

### Service hangs on stop (taking too long)

```bash
# Check timeout settings
$ systemctl show myapp.service | grep TimeoutStop
TimeoutStopUSec=1min 30s

# Override timeout for a specific unit
$ sudo systemctl edit myapp.service
# Add:
[Service]
TimeoutStopSec=10
```

### Broken unit file — system won't boot past a target

```bash
# From emergency.target or rescue.target:
# Mask the problematic unit temporarily
$ sudo systemctl mask myapp.service

# Reboot into normal target, then investigate
$ sudo reboot
```


[↑ Back to TOC](#toc)

---

## Pattern 6 — Boot to Last Known Good Kernel

When a kernel update breaks boot (driver issue, panic on boot):

```bash
# At GRUB, select the previous kernel entry, OR:
# Boot with kernel argument to skip the newest kernel (temporarily):
# In GRUB editor, select the older kernel entry manually.

# After booting into the older kernel, check installed kernels:
$ rpm -qa kernel | sort
kernel-6.12.0-1.el10.x86_64
kernel-6.12.0-2.el10.x86_64   ← broken

# Set the default kernel (grubby)
$ sudo grubby --set-default /boot/vmlinuz-6.12.0-1.el10.x86_64

# Verify
$ sudo grubby --default-kernel
/boot/vmlinuz-6.12.0-1.el10.x86_64

# Optionally remove the broken kernel
$ sudo dnf remove kernel-6.12.0-2.el10.x86_64
```


[↑ Back to TOC](#toc)

---

## Pattern 7 — Network Unreachable After Config Change

```bash
# Check connection state
$ nmcli connection show
$ nmcli device status

# Reload connection without losing SSH session
$ sudo nmcli connection reload

# Bring connection down and up
$ sudo nmcli connection down ens3 && sudo nmcli connection up ens3

# If interface has no IP
$ sudo nmcli device connect ens3

# Verify routing
$ ip route show
$ ip addr show ens3

# Check for conflicting static route
$ ip route show table all | grep -v "proto kernel"
```

**If you lost SSH access entirely:** use the VM console (virsh console, IPMI, cloud serial console) to fix the network configuration.


[↑ Back to TOC](#toc)

---

## Pattern 8 — Disk Full Recovery

```bash
# Identify the full filesystem
$ df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda3        20G   20G     0 100% /

# Step 1: Find large files
$ sudo find / -xdev -type f -size +100M 2>/dev/null | sort -k5 -rn

# Step 2: Find directories using the most space
$ sudo du -xh / --max-depth=3 | sort -rh | head -20

# Step 3: Rotated logs taking up space?
$ sudo journalctl --disk-usage
$ sudo journalctl --vacuum-size=500M

# Step 4: Old kernels
$ rpm -qa kernel | sort
$ sudo dnf remove <old-kernel-nvr>

# Step 5: DNF cache
$ sudo dnf clean all

# Step 6: Abandoned container images (if Podman in use)
$ podman image prune -a

# Step 7: Extend the LVM volume (if LVM is in use)
$ sudo lvextend -r -L +5G /dev/rhel/root   # -r resizes the filesystem too
```

> **`-r` flag on `lvextend`** resizes the filesystem atomically with the LV expansion — always use it.


[↑ Back to TOC](#toc)

---

## Recovery Runbook Template

Copy this into your runbook for any new recovery scenario:

```markdown

[↑ Back to TOC](#toc)

## Recovery - <Scenario Name>

**Trigger:** What condition makes this runbook active  
**Impact:** What is broken / what users see  
**RTO target:** Expected time to recover  

### Prerequisites
- Access method: (SSH / console / IPMI)
- Required privileges: (root / sudo)
- Tools needed:

### Steps
1. Diagnose: confirm this is the right runbook
2. Isolate: stop the bleeding
3. Fix: apply the recovery
4. Verify: success criteria
5. Communicate: notify stakeholders

### Post-recovery
- Root cause investigation
- Prevent recurrence
- Update monitoring

### Escalation
- If not resolved in X minutes → contact ...
```


[↑ Back to TOC](#toc)

---

## Why This Matters in Production

Recovery procedures that are documented, practiced, and version-controlled reduce MTTR (Mean Time to Recover) dramatically. The difference between a 15-minute recovery and a 4-hour outage is usually:

1. Knowing the exact commands before you're under pressure
2. Having a tested runbook rather than reasoning from first principles during an incident
3. Practicing in a non-production environment (use the lab VMs!)

RHCA candidates are expected to execute these procedures quickly and correctly under exam conditions. More importantly, production systems depend on administrators who can.

---


[↑ Back to TOC](#toc)

## Recap

| Scenario | Entry Point | Key Command |
|---|---|---|
| Root password lost | GRUB `rd.break` | `chroot /sysroot; passwd root; touch /.autorelabel` |
| Boot failure | GRUB `emergency.target` | `systemctl list-units --failed` |
| XFS corruption | Unmount → repair | `xfs_repair /dev/vdX` |
| SELinux label broken | Running system | `restorecon -Rv <path>` |
| Stuck service | systemctl | `systemctl reset-failed; systemctl kill` |
| Bad kernel | GRUB + grubby | `grubby --set-default <vmlinuz>` |
| Network down | nmcli | `nmcli connection reload; nmcli device connect` |
| Disk full | df + find + du | `journalctl --vacuum-size=`; `dnf clean`; `lvextend -r` |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Configuring the boot process](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_monitoring_and_updating_the_kernel/index) | GRUB2, kernel parameters, and boot troubleshooting |
| [`xfs_repair` man page](https://man7.org/linux/man-pages/man8/xfs_repair.8.html) | XFS filesystem recovery reference |
| [`grubby` man page](https://man7.org/linux/man-pages/man8/grubby.8.html) | Managing GRUB2 default kernel entries |
| [RHEL 10 — Rescuing and recovering a system](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/interactively_installing_rhel_from_installation_media/index) | Official rescue mode and root password reset guide |

---


[↑ Back to TOC](#toc)

## Next step

→ [Objective Map](../../98-reference/01-objective-map.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
