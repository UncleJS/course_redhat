# nmcli Profiles at Scale

At RHCA level, you need to understand NetworkManager's connection model deeply
enough to manage it at scale — via Ansible, templates, or automation.

---
<a name="toc"></a>

## Table of contents

- [Connection profile deep-dive](#connection-profile-deep-dive)
- [All important nmcli properties](#all-important-nmcli-properties)
  - [Key properties for static configuration](#key-properties-for-static-configuration)
- [Multiple IP addresses on one interface](#multiple-ip-addresses-on-one-interface)
- [Multiple routes (policy routing intro)](#multiple-routes-policy-routing-intro)
- [Create profiles via nmcli batch (scripting)](#create-profiles-via-nmcli-batch-scripting)
- [Manage profiles with Ansible (RHEL System Roles)](#manage-profiles-with-ansible-rhel-system-roles)
- [Reload profiles after manual keyfile edits](#reload-profiles-after-manual-keyfile-edits)


## Connection profile deep-dive

A connection profile is a configuration file in
`/etc/NetworkManager/system-connections/`. Modern RHEL 10 uses **keyfile** format.

```bash
# List all connection files
sudo ls -la /etc/NetworkManager/system-connections/

# View a profile
sudo cat "/etc/NetworkManager/system-connections/Wired connection 1.nmconnection"
```


[↑ Back to TOC](#toc)

---

## All important nmcli properties

```bash
# Full list of properties for a connection
nmcli connection show "Wired connection 1"

# Specific property
nmcli -f ipv4.addresses connection show "Wired connection 1"
```

### Key properties for static configuration

```bash
sudo nmcli connection modify "eth-static" \
  connection.autoconnect yes \
  connection.autoconnect-priority 10 \
  ipv4.method manual \
  ipv4.addresses "192.168.1.100/24" \
  ipv4.gateway "192.168.1.1" \
  ipv4.dns "192.168.1.53 8.8.8.8" \
  ipv4.dns-search "lab.local example.com" \
  ipv4.ignore-auto-dns yes \
  ipv6.method disabled
```


[↑ Back to TOC](#toc)

---

## Multiple IP addresses on one interface

```bash
sudo nmcli connection modify "eth-static" \
  ipv4.addresses "192.168.1.100/24,192.168.1.101/24,192.168.1.102/24"
```

Or add one at a time:

```bash
sudo nmcli connection modify "eth-static" +ipv4.addresses "192.168.1.103/24"
```


[↑ Back to TOC](#toc)

---

## Multiple routes (policy routing intro)

```bash
# Add a static route via a specific gateway
sudo nmcli connection modify "eth-static" \
  +ipv4.routes "10.10.0.0/16 192.168.1.254"

# Remove a route
sudo nmcli connection modify "eth-static" \
  -ipv4.routes "10.10.0.0/16 192.168.1.254"
```


[↑ Back to TOC](#toc)

---

## Create profiles via nmcli batch (scripting)

```bash
#!/usr/bin/env bash
set -euo pipefail

CONNECTION_NAME="server-eth0"
INTERFACE="ens3"
IP="192.168.1.100/24"
GW="192.168.1.1"
DNS="192.168.1.53"

# Delete existing (idempotent)
nmcli connection delete "${CONNECTION_NAME}" 2>/dev/null || true

# Create new
nmcli connection add \
  type ethernet \
  con-name "${CONNECTION_NAME}" \
  ifname "${INTERFACE}" \
  ipv4.method manual \
  ipv4.addresses "${IP}" \
  ipv4.gateway "${GW}" \
  ipv4.dns "${DNS}" \
  ipv6.method disabled \
  connection.autoconnect yes

nmcli connection up "${CONNECTION_NAME}"
```


[↑ Back to TOC](#toc)

---

## Manage profiles with Ansible (RHEL System Roles)

```bash
sudo dnf install -y rhel-system-roles
```

```yaml

[↑ Back to TOC](#toc)

---
- name: Configure network
  hosts: all
  become: true
  vars:
    network_connections:
      - name: eth-static
        type: ethernet
        interface_name: ens3
        state: up
        autoconnect: true
        ip:
          address:
            - 192.168.1.100/24
          gateway4: 192.168.1.1
          dns:
            - 192.168.1.53
            - 8.8.8.8
          dns_search:
            - lab.local

  roles:
    - redhat.rhel_system_roles.network
```

---

## Reload profiles after manual keyfile edits

```bash
# If you edit /etc/NetworkManager/system-connections/ directly
sudo nmcli connection reload

# Activate the updated connection
sudo nmcli connection up "<connection-name>"
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [NetworkManager keyfile format](https://networkmanager.dev/docs/api/latest/nm-settings-keyfile.html) | Connection file format for `/etc/NetworkManager/system-connections/` |
| [`nmcli` man page](https://man7.org/linux/man-pages/man1/nmcli.1.html) | Full option reference including `--offline` mode |
| [RHEL 10 — NetworkManager at scale](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_networking/index) | Automating and templating network configuration |

---

## Next step

→ [Routing + Troubleshooting Method](02-routing-method.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
