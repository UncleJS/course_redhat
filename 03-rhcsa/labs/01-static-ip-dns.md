
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

- [Background](#background)
- [Steps](#steps)
  - [1 — Identify your interface and current connection](#1-identify-your-interface-and-current-connection)
  - [2 — Choose a static IP](#2-choose-a-static-ip)
  - [3 — Configure static addressing](#3-configure-static-addressing)
  - [4 — Activate the new config](#4-activate-the-new-config)
  - [5 — Test connectivity](#5-test-connectivity)
  - [6 — Test persistence across reboot](#6-test-persistence-across-reboot)
- [Cleanup (restore DHCP)](#cleanup-restore-dhcp)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)


## Prerequisites

- Completed [NetworkManager (nmcli)](../09-networkmanager-nmcli.md) and [DNS and Name Resolution](../10-dns-resolution.md)
- Know your VM's current interface name (`ip link show`)
- VM snapshot taken

---


[↑ Back to TOC](#toc)

## Background

Servers in production almost never use DHCP. A web server, database node, or
load balancer that gets its IP from DHCP is a liability: IP changes on lease
renewal break DNS PTR records, firewall rules, Kerberos keytabs, and any other
configuration that references that IP by address. Static addressing is the
default expectation for any host running a persistent service.

Beyond stability, static IP assignment is a prerequisite for many automation
and identity management workflows. Ansible inventories, IdM host objects, and
TLS certificate subject names all depend on the host having a predictable
address. Changing the IP of a registered host typically requires updating all
of these references — a significant maintenance burden avoided by getting the
addressing right at provision time.

This lab exercises the full `nmcli` static addressing workflow: identify the
connection profile, apply address, gateway, and DNS settings, activate, verify,
and confirm persistence across reboot. These steps are a precise match for
the networking tasks that appear on the RHCSA exam.

### What you will learn

- How to inspect the current NetworkManager connection state
- The difference between `ipv4.method auto` (DHCP) and `ipv4.method manual` (static)
- Why activating a modified connection (`nmcli connection up`) is required to apply changes
- How to verify each layer of the network stack independently
- Why `connection.autoconnect yes` is essential for persistence

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

> **Hint:** The connection name shown by `nmcli connection show` is often
> something like `"Wired connection 1"` or `"ens3"`. It may contain spaces.
> When using it in subsequent commands, always wrap it in quotes.

### 2 — Choose a static IP

Pick an IP in your VM's subnet. If your VM is using `192.168.122.x` (NAT),
use something like `192.168.122.200/24`. Check for conflicts:

```bash
ping -c 2 192.168.122.200   # should show no response (IP is free)
```

> **Hint:** Your gateway is typically the `.1` address of the subnet. If
> `ip route show` currently shows `default via 192.168.122.1`, that is your
> gateway. Do not use the gateway address as your static IP.

### 3 — Configure static addressing

Replace `<CONNECTION-NAME>` with your actual connection name:

```bash
sudo nmcli connection modify "<CONNECTION-NAME>" \
  ipv4.method manual \
  ipv4.addresses 192.168.122.200/24 \
  ipv4.gateway 192.168.122.1 \
  ipv4.dns "192.168.122.1 8.8.8.8"
```

> **Hint:** `ipv4.method manual` is mandatory. Without it, NetworkManager
> will still run DHCP even after you set a static address — DHCP may
> then overwrite your static settings with a lease response.

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

> **Hint:** If the first ping fails, the gateway is unreachable — check
> that your static IP is in the correct subnet and the gateway IP is right.
> If the second fails, routing beyond the gateway is broken (hypervisor
> issue). If the third fails but the second succeeds, DNS is misconfigured —
> check `ipv4.dns` in your profile.

### 6 — Test persistence across reboot

```bash
sudo reboot
```

After boot, log back in and repeat the verify steps.

> **Hint:** If the static IP is gone after reboot, the connection profile
> may not have `connection.autoconnect yes`. Check with:
> `nmcli connection show "<CONNECTION-NAME>" | grep autoconnect`
> and fix with:
> `sudo nmcli connection modify "<CONNECTION-NAME>" connection.autoconnect yes`


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

## Troubleshooting guide

| Symptom | Likely cause | Fix |
|---|---|---|
| No IP after `connection up` | Wrong interface or connection name | Re-check with `nmcli device status` — note exact name |
| `ping 8.8.8.8` fails | Wrong gateway IP | `ip route show` — verify `default via` points to correct gateway |
| `ping access.redhat.com` fails but `ping 8.8.8.8` works | Wrong DNS servers | `resolvectl status` — check DNS servers; update `ipv4.dns` |
| Settings lost after reboot | Connection not set to autoconnect | `nmcli connection modify ... connection.autoconnect yes` |
| Two IPs shown on interface | Old DHCP lease not cleared | Bring connection down and up: `nmcli connection down` then `nmcli connection up` |
| `nmcli connection up` fails with "device unavailable" | Interface name mismatch in profile | `nmcli connection show "<name>" | grep interface-name` — must match actual device name |
| DNS shows only one server despite setting two | Space-separated format not accepted | Use quotes: `ipv4.dns "8.8.8.8 8.8.4.4"` and verify with `resolvectl status` |
| Static IP chosen conflicts with another host | ARP conflict on network | `ping -c 1 <chosen-ip>` before setting — if it replies, choose a different IP |

---


[↑ Back to TOC](#toc)

## Why this matters in production

Servers rarely use DHCP. Static addressing ensures predictable access, stable
DNS PTR records, and no surprise IP changes during DHCP lease expiry. Getting
comfortable with `nmcli` is the foundation for all network configuration
work that follows.

Static IP configuration is one of the most reliably tested topics on the RHCSA
exam. The exam environment typically provides a VM with a running DHCP address
and instructs you to configure a specific static address, gateway, and DNS
server — then verify the configuration survives a reboot. Students who have
not practiced this exact workflow under time pressure often lose marks on an
otherwise simple task.

The key points the exam tests:
1. Correct use of `ipv4.method manual` (forgetting this is the most common error)
2. Setting gateway via `ipv4.gateway` (not as part of the address)
3. Using `nmcli connection up` after modification (changes are not applied automatically)
4. Verifying all three layers: IP (`ip addr`), gateway (`ip route`), DNS (`resolvectl status`)
5. Persistence after reboot (requires `connection.autoconnect yes`, which is the default)

### Verification checklist

Use this checklist after configuring static addressing:

```bash
# 1. IP address present
ip addr show ens3 | grep "inet "
# Expected: inet <your-static-ip>/24

# 2. Default route present
ip route show | grep "^default"
# Expected: default via <gateway-ip> dev ens3

# 3. DNS configured
resolvectl status | grep -A2 "Link.*ens3"
# Expected: DNS Servers: <your-dns-ip>

# 4. Gateway reachable
ping -c 1 <gateway-ip>

# 5. Internet reachable by IP
ping -c 1 8.8.8.8

# 6. DNS resolution works
ping -c 1 access.redhat.com

# 7. Config marked autoconnect
nmcli -f connection.autoconnect connection show "<CONNECTION-NAME>"
# Expected: connection.autoconnect: yes
```

All seven checks must pass before calling the lab complete.

### Common exam mistakes on static IP tasks

The RHCSA exam networking task is high-value and frequently failed for these reasons:

| Mistake | Consequence | Prevention |
|---|---|---|
| Omitting `ipv4.method manual` | DHCP still active; static address may be ignored | Always set `method manual` explicitly |
| Setting gateway inside `ipv4.addresses` (e.g., `192.168.1.10/24 192.168.1.1`) | Gateway silently ignored or parsing error | Use separate `ipv4.gateway` parameter |
| Forgetting `nmcli connection up` after `modify` | Changes are written to disk but not applied | Always follow `modify` with `connection up` |
| Wrong connection name (contains spaces, copied incorrectly) | `nmcli connection up "..."` fails with "unknown connection" | Copy exact name from `nmcli connection show` output |
| Not rebooting to verify persistence | Lab passes on the exam console but fails evaluator's reboot check | Always reboot and re-verify |
| Verifying IP only, not gateway and DNS | Partial credit at best | Complete all three verification commands |

### Interface naming on RHEL 10

RHEL 10 uses predictable network interface names by default. The name encodes
the device type and location:

| Prefix | Meaning | Example |
|---|---|---|
| `ens` | Ethernet, on-board, slot number | `ens3`, `ens192` |
| `enp` | Ethernet, PCI bus location | `enp0s3`, `enp2s0` |
| `eth` | Legacy naming (older kernels / cloud VMs) | `eth0` |
| `eno` | Ethernet, on-board index | `eno1` |

The name is assigned at first boot based on firmware, topology, and kernel
driver. It will not change between reboots on the same hardware. On exam VMs
you will typically see `ens3` or `enp1s0`.

---


[↑ Back to TOC](#toc)

## Extension tasks

**Extension 1 — Create a secondary connection profile**

Without modifying the existing profile, create a new named profile
`"lab-static-alt"` on the same interface with the address `192.168.122.201/24`.
Activate it, verify, then switch back to the original profile. Understand how
`connection.autoconnect-priority` controls which profile activates at boot.

```bash
sudo nmcli connection add type ethernet con-name "lab-static-alt" \
  ifname ens3 ipv4.method manual \
  ipv4.addresses 192.168.122.201/24 \
  ipv4.gateway 192.168.122.1 \
  ipv4.dns "8.8.8.8"
sudo nmcli connection up "lab-static-alt"
# Verify, then switch back:
sudo nmcli connection up "<ORIGINAL-CONNECTION-NAME>"
sudo nmcli connection delete "lab-static-alt"
```

**Extension 2 — Add a search domain**

Extend the static configuration to include `lab.local` as a DNS search
domain. Add an entry to `/etc/hosts` for `testhost.lab.local`. Verify that
`ping testhost` (without the domain suffix) resolves correctly.

```bash
sudo nmcli connection modify "<CONNECTION-NAME>" ipv4.dns-search "lab.local"
sudo nmcli connection up "<CONNECTION-NAME>"
echo "192.168.122.50  testhost.lab.local testhost" | sudo tee -a /etc/hosts
ping -c 2 testhost
```

**Extension 3 — Configure via keyfile**

Locate the connection keyfile in `/etc/NetworkManager/system-connections/`.
Edit it directly to change the DNS server to `1.1.1.1`, reload NetworkManager,
and verify the change is active. Then revert via `nmcli`.

```bash
ls /etc/NetworkManager/system-connections/
sudo vim /etc/NetworkManager/system-connections/<profile>.nmconnection
# Change dns= line to dns=1.1.1.1;
sudo nmcli connection reload
sudo nmcli connection up "<CONNECTION-NAME>"
resolvectl status | grep "DNS Server"
```

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab — Create a systemd Service](02-systemd-service.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
