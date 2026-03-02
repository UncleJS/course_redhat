# NetworkManager and nmcli
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**NetworkManager** is the default network management daemon on RHEL 10.
`nmcli` is its command-line interface — the tool you will use for all
network configuration.

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


## Key concepts

| Term | Meaning |
|---|---|
| **device** | A physical or virtual network interface (e.g., `ens3`) |
| **connection** | A configuration profile tied to a device |
| **active connection** | A connection currently applied to a device |

A device can have multiple connections defined (e.g., home, work, static),
but only one active at a time.


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


[↑ Back to TOC](#toc)

---

## Delete a connection profile

```bash
sudo nmcli connection delete "static-lab"
```


[↑ Back to TOC](#toc)

---

## Set hostname via nmcli

```bash
sudo nmcli general hostname rhel10-lab
sudo hostnamectl set-hostname rhel10-lab   # equivalent
```


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


[↑ Back to TOC](#toc)

---

## Connection file location

NetworkManager stores connection profiles as keyfiles:

```bash
ls /etc/NetworkManager/system-connections/
```

You can edit these directly (then run `sudo nmcli connection reload`), but
nmcli is safer and preferred.


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
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`nmcli` man page](https://man7.org/linux/man-pages/man1/nmcli.1.html) | Full nmcli option and command reference |
| [NetworkManager documentation](https://networkmanager.dev/docs/) | Connection file formats, dispatcher scripts, keyfile format |
| [RHEL 10 — Configuring and managing networking](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_networking/index) | Official guide covering nmcli, bonding, VLANs |

---

## Next step

→ [DNS and Name Resolution](10-dns-resolution.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
