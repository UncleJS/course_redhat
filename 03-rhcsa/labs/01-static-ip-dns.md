
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab: Static IP + DNS Validation
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCSA
**Estimated time:** 25 minutes
**Topology:** Single VM

---
<a name="toc"></a>

## Table of contents

- [Steps](#steps)
  - [1 — Identify your interface and current connection](#1-identify-your-interface-and-current-connection)
  - [2 — Choose a static IP](#2-choose-a-static-ip)
  - [3 — Configure static addressing](#3-configure-static-addressing)
  - [4 — Activate the new config](#4-activate-the-new-config)
  - [5 — Test connectivity](#5-test-connectivity)
  - [6 — Test persistence across reboot](#6-test-persistence-across-reboot)
- [Cleanup (restore DHCP)](#cleanup-restore-dhcp)


## Prerequisites

- Completed [NetworkManager (nmcli)](../09-networkmanager-nmcli.md) and [DNS and Name Resolution](../10-dns-resolution.md)
- Know your VM's current interface name (`ip link show`)
- VM snapshot taken

---


[↑ Back to TOC](#toc)

## Success criteria

- VM has a manually configured static IP address
- Default gateway is set correctly
- DNS resolves external names
- `ping access.redhat.com` succeeds
- Configuration survives a reboot

---


[↑ Back to TOC](#toc)

## Steps

### 1 — Identify your interface and current connection

```bash
nmcli device status
nmcli connection show
```

Note your interface name (e.g., `ens3`) and active connection name.

### 2 — Choose a static IP

Pick an IP in your VM's subnet. If your VM is using `192.168.122.x` (NAT),
use something like `192.168.122.200/24`. Check for conflicts:

```bash
ping -c 2 192.168.122.200   # should show no response (IP is free)
```

### 3 — Configure static addressing

Replace `<CONNECTION-NAME>` with your actual connection name:

```bash
sudo nmcli connection modify "<CONNECTION-NAME>" \
  ipv4.method manual \
  ipv4.addresses 192.168.122.200/24 \
  ipv4.gateway 192.168.122.1 \
  ipv4.dns "192.168.122.1 8.8.8.8"
```

### 4 — Activate the new config

```bash
sudo nmcli connection up "<CONNECTION-NAME>"
```

> **✅ Verify — IP address**
> ```bash
> ip addr show
> ```
> Look for: `192.168.122.200/24` on your interface.
>

> **✅ Verify — Default gateway**
> ```bash
> ip route show
> ```
> Look for: `default via 192.168.122.1`
>

> **✅ Verify — DNS**
> ```bash
> resolvectl status | grep "DNS Server"
> ```
> Look for: `192.168.122.1` and `8.8.8.8`
>

### 5 — Test connectivity

```bash
ping -c 3 192.168.122.1         # gateway reachable
ping -c 3 8.8.8.8               # internet reachable (IP)
ping -c 3 access.redhat.com     # DNS + internet working
```

All three should succeed.

### 6 — Test persistence across reboot

```bash
sudo reboot
```

After boot, log back in and repeat the verify steps.


[↑ Back to TOC](#toc)

---

## Cleanup (restore DHCP)

```bash
sudo nmcli connection modify "<CONNECTION-NAME>" \
  ipv4.method auto \
  ipv4.addresses "" \
  ipv4.gateway "" \
  ipv4.dns ""

sudo nmcli connection up "<CONNECTION-NAME>"
```


[↑ Back to TOC](#toc)

---

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| No IP after `connection up` | Wrong interface or connection name | Re-check with `nmcli device status` |
| `ping 8.8.8.8` fails | Wrong gateway | Verify gateway IP matches your network |
| `ping access.redhat.com` fails but `ping 8.8.8.8` works | Wrong DNS | Check `ipv4.dns` setting |
| Settings lost after reboot | Connection not marked auto-connect | `nmcli connection modify ... connection.autoconnect yes` |

---


[↑ Back to TOC](#toc)

## Why this matters in production

Servers rarely use DHCP. Static addressing ensures predictable access, stable
DNS PTR records, and no surprise IP changes during DHCP lease expiry. Getting
comfortable with `nmcli` is the foundation for all network configuration
work that follows.

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab — Create a systemd Service](02-systemd-service.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
