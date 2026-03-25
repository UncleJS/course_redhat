
[↑ Back to TOC](#toc)

# NetworkManager and nmcli
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**NetworkManager** is the default network management daemon on RHEL 10.
`nmcli` is its command-line interface — the tool you will use for all
network configuration.

NetworkManager owns the lifecycle of all network connections: it starts
connections at boot, monitors link state, applies DHCP responses, integrates
with `systemd-resolved` for DNS, and stores configuration persistently. It is
not optional on RHEL 10 — do not stop or disable it. Other tools like `ip`
can make temporary kernel-level changes, but those changes disappear on reboot
or on the next NetworkManager reconnection.

The central abstraction in NetworkManager is the **connection profile**. A
profile is a named set of configuration parameters (address method, IP, gateway,
DNS, etc.) that can be applied to a device. Multiple profiles can exist for the
same device — useful for laptops that switch between office, home, and lab
networks. Only one profile is active on a device at a time.

`nmcli` is the preferred CLI for all exam and production use. The `nmtui`
text-mode UI is available for interactive edits if preferred, but `nmcli` is
faster to script and is what exam questions expect.

---
<a name="toc"></a>

## Table of contents

- [Key concepts](#key-concepts)
- [View current state](#view-current-state)
- [Configure a static IP address](#configure-a-static-ip-address)
- [Switch back to DHCP](#switch-back-to-dhcp)
- [Create a new connection profile](#create-a-new-connection-profile)
- [Bring connections up and down](#bring-connections-up-and-down)
- [Delete a connection profile](#delete-a-connection-profile)
- [Set hostname via nmcli](#set-hostname-via-nmcli)
- [DNS configuration](#dns-configuration)
- [Connection file location](#connection-file-location)
- [Useful nmcli shortcuts](#useful-nmcli-shortcuts)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)
- [nmcli field reference](#nmcli-field-reference)
- [Bonding and teaming (overview)](#bonding-and-teaming-overview)


## Key concepts

| Term | Meaning |
|---|---|
| **device** | A physical or virtual network interface (e.g., `ens3`) |
| **connection** | A configuration profile tied to a device |
| **active connection** | A connection currently applied to a device |

A device can have multiple connections defined (e.g., home, work, static),
but only one active at a time.

Connection profiles store all network configuration in keyfiles under
`/etc/NetworkManager/system-connections/`. When you run `nmcli connection up`,
NetworkManager reads the profile, applies settings to the kernel, and (where
applicable) initiates DHCP or configures the static address.


[↑ Back to TOC](#toc)

---

## View current state

```bash
# Short overview of devices and their status
nmcli

# Device status
nmcli device status

# Connection profiles (all defined)
nmcli connection show

# Active connections only
nmcli connection show --active

# Details of a specific connection
nmcli connection show "Wired connection 1"
```


[↑ Back to TOC](#toc)

---

## Configure a static IP address

```bash
# Step 1 — identify your connection name
nmcli connection show

# Step 2 — modify the connection
sudo nmcli connection modify "Wired connection 1" \
  ipv4.method manual \
  ipv4.addresses 192.168.1.100/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "192.168.1.1 8.8.8.8"

# Step 3 — apply changes
sudo nmcli connection up "Wired connection 1"
```

> **✅ Verify**
> ```bash
> ip addr show
> ip route show
> ```
> Look for your new IP and the default gateway route.
>

> **Exam tip:** `ipv4.method manual` is required when specifying a static
> address. If you set an address but leave the method as `auto`, NetworkManager
> will still run DHCP and may overwrite your static address.


[↑ Back to TOC](#toc)

---

## Switch back to DHCP

```bash
sudo nmcli connection modify "Wired connection 1" \
  ipv4.method auto \
  ipv4.addresses "" \
  ipv4.gateway "" \
  ipv4.dns ""

sudo nmcli connection up "Wired connection 1"
```

The empty-string values clear the static settings. When `ipv4.method` is `auto`,
NetworkManager runs DHCP and populates the address, gateway, and DNS
automatically from the server response.


[↑ Back to TOC](#toc)

---

## Create a new connection profile

```bash
sudo nmcli connection add \
  type ethernet \
  con-name "static-lab" \
  ifname ens3 \
  ipv4.method manual \
  ipv4.addresses 192.168.1.200/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "192.168.1.1"
```

This creates a new profile named `static-lab` bound to device `ens3`.
The existing profile for `ens3` is not deleted — bring this new one up
explicitly with `nmcli connection up static-lab`.

By default, new connections have `connection.autoconnect yes`, meaning
NetworkManager will attempt to activate them on boot. If two profiles share
the same device and both have autoconnect enabled, NetworkManager activates
the one with the highest `connection.autoconnect-priority` (default 0).


[↑ Back to TOC](#toc)

---

## Bring connections up and down

```bash
sudo nmcli connection up "static-lab"
sudo nmcli connection down "static-lab"

# Bring up default (auto-connect)
sudo nmcli device connect ens3
sudo nmcli device disconnect ens3
```

`nmcli connection up` activates a named profile (and disconnects any other
profile on the same device). `nmcli device connect` tells NetworkManager to
pick the best available profile for that device and activate it.


[↑ Back to TOC](#toc)

---

## Delete a connection profile

```bash
sudo nmcli connection delete "static-lab"
```

Deleting a profile removes the keyfile from
`/etc/NetworkManager/system-connections/`. This is permanent. The device
is not automatically reconfigured — bring up another profile if needed.


[↑ Back to TOC](#toc)

---

## Set hostname via nmcli

```bash
sudo nmcli general hostname rhel10-lab
sudo hostnamectl set-hostname rhel10-lab   # equivalent
```

Both commands write to `/etc/hostname` and are persistent. The hostname
affects `/etc/hosts` resolution for `localhost` variants, Kerberos principal
names, and reverse DNS records. Set it correctly before registering with
an identity system like SSSD or IdM.


[↑ Back to TOC](#toc)

---

## DNS configuration

DNS servers are set per connection. After modifying DNS:

```bash
sudo nmcli connection modify "Wired connection 1" ipv4.dns "192.168.1.1 8.8.8.8"
sudo nmcli connection up "Wired connection 1"
```

Check the resolved DNS:

```bash
resolvectl status
cat /etc/resolv.conf
```

NetworkManager passes DNS server information to `systemd-resolved`, which
manages the actual stub resolver at `127.0.0.53`. On RHEL 10, do not edit
`/etc/resolv.conf` directly — it is a symlink managed by `systemd-resolved`
and will be overwritten.

To set DNS search domains alongside servers:

```bash
sudo nmcli connection modify "Wired connection 1" \
  ipv4.dns "192.168.1.1 8.8.8.8" \
  ipv4.dns-search "lab.local example.com"
sudo nmcli connection up "Wired connection 1"
```


[↑ Back to TOC](#toc)

---

## Connection file location

NetworkManager stores connection profiles as keyfiles:

```bash
ls /etc/NetworkManager/system-connections/
```

You can edit these directly (then run `sudo nmcli connection reload`), but
nmcli is safer and preferred.

A typical keyfile for a static connection looks like:

```ini
[connection]
id=static-lab
type=ethernet
interface-name=ens3
autoconnect=true

[ipv4]
method=manual
address1=192.168.1.200/24,192.168.1.1
dns=192.168.1.1;8.8.8.8;

[ipv6]
method=ignore
```

Understanding this format is useful when editing is faster than re-creating a
profile from scratch. Always run `nmcli connection reload` after manual edits.


[↑ Back to TOC](#toc)

---

## Useful nmcli shortcuts

```bash
# Quick status table
nmcli

# Which IP do I have?
nmcli -f IP4.ADDRESS device show ens3

# All details about device
nmcli device show ens3

# Tabular view of all connections with their device and state
nmcli -f NAME,DEVICE,STATE connection show
```


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** A new VM has DHCP and you need to assign it the static address
`10.0.0.50/24`, gateway `10.0.0.1`, DNS `10.0.0.1` and `8.8.8.8`.

```bash
# 1. Find the active connection name
nmcli connection show --active
# Output shows: "Wired connection 1" on device ens3

# 2. Apply static configuration
sudo nmcli connection modify "Wired connection 1" \
  ipv4.method manual \
  ipv4.addresses 10.0.0.50/24 \
  ipv4.gateway 10.0.0.1 \
  ipv4.dns "10.0.0.1 8.8.8.8"

# 3. Activate
sudo nmcli connection up "Wired connection 1"

# 4. Verify IP
ip addr show ens3
# Expected: inet 10.0.0.50/24

# 5. Verify route
ip route show
# Expected: default via 10.0.0.1 dev ens3

# 6. Verify DNS
resolvectl status | grep "DNS Server"
# Expected: 10.0.0.1, 8.8.8.8

# 7. Test end-to-end
ping -c 3 10.0.0.1 && ping -c 3 8.8.8.8 && ping -c 3 access.redhat.com
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Symptom | Likely cause | Diagnosis | Fix |
|---|---|---|---|
| Static IP not applied after `connection up` | Wrong connection name used | `nmcli connection show` — check exact name | Use the exact name including spaces and capitalisation |
| IP reverts to DHCP after reboot | `ipv4.method` still `auto` | `nmcli connection show <name> \| grep method` | Set `ipv4.method manual` before setting addresses |
| No default route after static config | Gateway not set | `ip route show` — no `default` entry | `nmcli ... ipv4.gateway <gw-ip>` |
| DNS not working despite correct server | Connection not re-activated | `resolvectl status` — old servers still listed | `sudo nmcli connection up <name>` to reapply |
| Two profiles fight over same device | Both have `autoconnect yes` | `nmcli connection show` — two entries for same device | Set `connection.autoconnect no` on the one not wanted at boot |
| `connection reload` needed warning | Edited keyfile directly | Warnings in `journalctl -u NetworkManager` | `sudo nmcli connection reload` after any manual keyfile edit |


[↑ Back to TOC](#toc)

---

## nmcli field reference

`nmcli connection show <name>` outputs dozens of fields. The most relevant
for RHCSA work:

```bash
nmcli connection show "Wired connection 1" | grep -E \
  "connection\.(id|uuid|type|interface-name|autoconnect)|ipv4\.(method|addresses|gateway|dns|dns-search)|GENERAL"
```

Key fields:

| Field | Set with | Meaning |
|---|---|---|
| `connection.id` | `con-name` in `add` | Human-readable connection name |
| `connection.interface-name` | `ifname` in `add` | Device this profile binds to |
| `connection.autoconnect` | `connection.autoconnect yes/no` | Activate this profile at boot |
| `connection.autoconnect-priority` | `connection.autoconnect-priority <n>` | Higher number wins when multiple profiles compete |
| `ipv4.method` | `ipv4.method manual/auto` | `manual` = static, `auto` = DHCP |
| `ipv4.addresses` | `ipv4.addresses 10.0.0.1/24` | Assigned IP with prefix |
| `ipv4.gateway` | `ipv4.gateway 10.0.0.1` | Default gateway |
| `ipv4.dns` | `ipv4.dns "8.8.8.8 1.1.1.1"` | DNS servers (space-separated) |
| `ipv4.dns-search` | `ipv4.dns-search "lab.local"` | DNS search domains |
| `ipv4.routes` | `+ipv4.routes "10.0.0.0/8 192.168.1.1"` | Static routes |
| `ipv6.method` | `ipv6.method ignore/auto/manual` | IPv6 configuration method |

To see the full list of settable fields:

```bash
nmcli connection show "Wired connection 1"
```

To modify a field that accepts lists (like `ipv4.routes`):

```bash
# Append a route (+ prefix adds to list)
sudo nmcli connection modify "Wired connection 1" \
  +ipv4.routes "10.10.0.0/24 192.168.1.1"

# Remove a specific route (- prefix removes from list)
sudo nmcli connection modify "Wired connection 1" \
  -ipv4.routes "10.10.0.0/24 192.168.1.1"
```


[↑ Back to TOC](#toc)

---

## Bonding and teaming (overview)

NetworkManager manages bonded interfaces and team interfaces as connection
profiles, just like regular Ethernet. Bonding provides link aggregation and
failover without additional software.

To create a bond with two slave interfaces:

```bash
# Create the bond master
sudo nmcli connection add type bond \
  con-name "bond0" \
  ifname bond0 \
  bond.options "mode=active-backup,miimon=100"

# Add slave 1
sudo nmcli connection add type ethernet \
  con-name "bond0-slave1" \
  ifname ens3 \
  master bond0

# Add slave 2
sudo nmcli connection add type ethernet \
  con-name "bond0-slave2" \
  ifname ens4 \
  master bond0

# Configure IP on the bond master
sudo nmcli connection modify bond0 \
  ipv4.method manual \
  ipv4.addresses 192.168.1.10/24 \
  ipv4.gateway 192.168.1.1

# Bring up
sudo nmcli connection up bond0
sudo nmcli connection up bond0-slave1
sudo nmcli connection up bond0-slave2
```

Common bond modes:

| Mode | Name | Use case |
|---|---|---|
| 0 | `balance-rr` | Round-robin load balancing (requires switch support) |
| 1 | `active-backup` | Failover only — one NIC active at a time (no switch config needed) |
| 4 | `802.3ad` | Dynamic link aggregation (LACP) — requires switch config |
| 5 | `balance-tlb` | Adaptive transmit load balancing |
| 6 | `balance-alb` | Adaptive load balancing (both TX and RX) |

For RHCSA, `active-backup` is the most commonly tested mode — it provides
redundancy without any switch configuration.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`nmcli` man page](https://man7.org/linux/man-pages/man1/nmcli.1.html) | Full nmcli option and command reference |
| [NetworkManager documentation](https://networkmanager.dev/docs/) | Connection file formats, dispatcher scripts, keyfile format |
| [RHEL 10 — Configuring and managing networking](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_networking/index) | Official guide covering nmcli, bonding, VLANs |

---


[↑ Back to TOC](#toc)

## Next step

→ [DNS and Name Resolution](10-dns-resolution.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
