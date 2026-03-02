# First Boot Checklist
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Run through this checklist immediately after installing RHEL 10.
Each step takes under a minute.

---
<a name="toc"></a>

## Table of contents

- [1 — Confirm you are NOT logged in as root](#1-confirm-you-are-not-logged-in-as-root)
- [2 — Check network connectivity](#2-check-network-connectivity)
- [3 — Check DNS resolution](#3-check-dns-resolution)
- [4 — Register the system (if not done during install)](#4-register-the-system-if-not-done-during-install)
- [5 — Apply all available updates](#5-apply-all-available-updates)
- [6 — Confirm SELinux is enforcing](#6-confirm-selinux-is-enforcing)
- [7 — Confirm firewalld is running](#7-confirm-firewalld-is-running)
- [8 — Check system time](#8-check-system-time)
- [9 — Set a hostname (if not done during install)](#9-set-a-hostname-if-not-done-during-install)
- [10 — Take a VM snapshot](#10-take-a-vm-snapshot)


## 1 — Confirm you are NOT logged in as root

```bash
$ whoami
```

Expected: your regular username. If it says `root`, log out and log in as your
regular user.


[↑ Back to TOC](#toc)

---

## 2 — Check network connectivity

```bash
$ ping -c 3 8.8.8.8
```

Look for: `3 packets transmitted, 3 received`

If this fails, see [NetworkManager (nmcli)](../03-rhcsa/09-networkmanager-nmcli.md).


[↑ Back to TOC](#toc)

---

## 3 — Check DNS resolution

```bash
$ ping -c 2 access.redhat.com
```

Look for: IP address resolved and packets received.


[↑ Back to TOC](#toc)

---

## 4 — Register the system (if not done during install)

```bash
sudo subscription-manager register --username <your-redhat-username>
sudo subscription-manager attach --auto
```


[↑ Back to TOC](#toc)

---

## 5 — Apply all available updates

```bash
sudo dnf upgrade -y
```

This may take a few minutes on first run. Reboot if the kernel was updated.

```bash
sudo reboot
```


[↑ Back to TOC](#toc)

---

## 6 — Confirm SELinux is enforcing

```bash
$ getenforce
```

Expected: `Enforcing`

> **⚠️ Do NOT change this**
> Do not set SELinux to `Permissive` or `Disabled`. If something breaks, learn
> to fix it correctly. See [SELinux Fundamentals](../03-rhcsa/13-selinux-fundamentals.md).
>


[↑ Back to TOC](#toc)

---

## 7 — Confirm firewalld is running

```bash
$ sudo firewall-cmd --state
```

Expected: `running`


[↑ Back to TOC](#toc)

---

## 8 — Check system time

```bash
$ timedatectl
```

Look for: `System clock synchronized: yes` and `NTP service: active`

If NTP is not active:

```bash
sudo timedatectl set-ntp true
```


[↑ Back to TOC](#toc)

---

## 9 — Set a hostname (if not done during install)

```bash
sudo hostnamectl set-hostname rhel10-lab
```


[↑ Back to TOC](#toc)

---

## 10 — Take a VM snapshot

Now is the perfect time to take a clean snapshot before you start making changes.
See [Lab Workflow](../00-preface/02-labs.md) for instructions.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Configuring basic system settings](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_basic_system_settings/index) | Hostnames, time zones, locales, and initial configuration |
| [systemd-hostnamed](https://www.freedesktop.org/software/systemd/man/latest/hostnamed.html) | Upstream docs for `hostnamectl` |
| [chrony documentation](https://chrony-project.org/documentation.html) | NTP configuration reference |

---

## Next step

→ [Accounts, sudo, and Updates](03-sudo-updates.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
