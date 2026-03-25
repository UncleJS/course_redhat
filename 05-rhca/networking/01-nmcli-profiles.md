
[↑ Back to TOC](#toc)

# nmcli Profiles at Scale
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

At RHCA level, you need to understand NetworkManager's connection model deeply
enough to manage it at scale — via Ansible, templates, or automation.

NetworkManager models network configuration as **connection profiles** — named
objects that associate a set of network settings with a device or device type.
A single physical interface can have multiple profiles (e.g., a static profile
and a DHCP fallback profile), though only one is active at a time. Profiles
are stored as keyfiles in `/etc/NetworkManager/system-connections/` on RHEL 10,
having replaced the older `ifcfg` format in RHEL 9.

The distinction between a *device* and a *connection* is important. A device
is a kernel-level network interface (`ens3`, `eth0`). A connection is a
configuration set that can be applied to a device. When you run
`nmcli connection up "eth-static"`, NetworkManager applies that connection's
settings to the associated device. Multiple connections can exist for the same
device; `autoconnect-priority` determines which one NetworkManager applies
at boot when multiple are configured.

At RHCA scale, manual `nmcli` commands are replaced by automation. The RHEL
System Roles `network` role is the idiomatic way to configure networking
across a fleet via Ansible. It generates and applies the same keyfile
configurations that `nmcli` would produce, making it easy to verify manually
what automation would create.

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
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## Connection profile deep-dive

A connection profile is a configuration file in
`/etc/NetworkManager/system-connections/`. Modern RHEL 10 uses **keyfile** format.

```bash
# List all connection files
sudo ls -la /etc/NetworkManager/system-connections/

# View a profile
sudo cat "/etc/NetworkManager/system-connections/Wired connection 1.nmconnection"
```

A keyfile groups settings into sections:

```ini
[connection]
id=eth-static
uuid=12345678-1234-1234-1234-123456789abc
type=ethernet
interface-name=ens3
autoconnect=true

[ethernet]
mac-address-blacklist=

[ipv4]
method=manual
address1=192.168.1.100/24,192.168.1.1
dns=192.168.1.53;8.8.8.8;
dns-search=lab.local;
ignore-auto-dns=true

[ipv6]
method=disabled

[proxy]
```

The `address1=IP/prefix,gateway` format combines address and gateway in one
field. Additional addresses use `address2=`, `address3=`, etc.


[↑ Back to TOC](#toc)

---

## All important nmcli properties

```bash
# Full list of properties for a connection
nmcli connection show "Wired connection 1"

# Specific property
nmcli -f ipv4.addresses connection show "Wired connection 1"

# Show only fields matching a pattern
nmcli -f ipv4,ipv6 connection show "Wired connection 1"
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

After modifying, activate the changes:

```bash
sudo nmcli connection up "eth-static"
```

Changes take effect when the connection is activated. `nmcli connection
modify` only writes to the keyfile — it does not apply changes to the
running interface until `connection up` is called.


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

The `+` prefix appends to a list property. Use `-` to remove:

```bash
sudo nmcli connection modify "eth-static" -ipv4.addresses "192.168.1.103/24"
```

After modifying, reactivate:

```bash
sudo nmcli connection up "eth-static"
ip addr show ens3   # verify all addresses are applied
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

Routes can include a metric to control preference:

```bash
# Add route with metric 200 (higher metric = lower preference)
sudo nmcli connection modify "eth-static" \
  +ipv4.routes "10.10.0.0/16 192.168.1.254 200"
```

Verify routes after activation:

```bash
ip route show | grep 10.10.0.0
# 10.10.0.0/16 via 192.168.1.254 dev ens3 proto static metric 200
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

For scripting across multiple interfaces, drive the loop from an array or
configuration file:

```bash
#!/usr/bin/env bash
# Configure multiple interfaces from a data structure
declare -A INTERFACES=(
  ["server-eth0"]="ens3:192.168.1.100/24:192.168.1.1"
  ["server-eth1"]="ens4:10.0.0.100/24:10.0.0.1"
)

for CON_NAME in "${!INTERFACES[@]}"; do
  IFS=: read -r IFACE IP GW <<< "${INTERFACES[$CON_NAME]}"
  nmcli connection delete "${CON_NAME}" 2>/dev/null || true
  nmcli connection add type ethernet con-name "${CON_NAME}" \
    ifname "${IFACE}" ipv4.method manual \
    ipv4.addresses "${IP}" ipv4.gateway "${GW}" \
    ipv6.method disabled connection.autoconnect yes
  nmcli connection up "${CON_NAME}"
done
```


[↑ Back to TOC](#toc)

---

## Manage profiles with Ansible (RHEL System Roles)

```bash
sudo dnf install -y rhel-system-roles
```

```yaml
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

The `network` role is idempotent — running it multiple times produces the
same result. It uses `nmcli` internally and writes keyfiles to the standard
location.

To verify what the role would generate without applying it:

```bash
ansible-playbook --check network.yml
```

> **Exam tip:** On RHCA exams, know both the `nmcli` command-line approach
> and that the RHEL System Roles `network` role exists. The role is the
> scalable approach; `nmcli` is used for one-off or interactive configuration.

---

## Reload profiles after manual keyfile edits

```bash
# If you edit /etc/NetworkManager/system-connections/ directly
sudo nmcli connection reload

# Activate the updated connection
sudo nmcli connection up "<connection-name>"
```

After `reload`, NetworkManager re-reads all keyfiles. Connections that were
modified will show their updated properties in `nmcli connection show`.
The connection must be brought up again for the changes to take effect on
the interface.

```bash
# Full round-trip test after manual edit
sudo vim "/etc/NetworkManager/system-connections/eth-static.nmconnection"
sudo nmcli connection reload
sudo nmcli connection up "eth-static"
ip addr show ens3
ip route show
```


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** A server has two NICs (`ens3` and `ens4`). Create a bonded
interface (`bond0`) for redundancy using `active-backup` mode, configure
a static IP on it, and verify failover.

```bash
# 1. Create the bond master interface
sudo nmcli connection add \
  type bond \
  con-name bond0 \
  ifname bond0 \
  bond.options "mode=active-backup,miimon=100,fail_over_mac=1"

# 2. Add ens3 as the first slave
sudo nmcli connection add \
  type ethernet \
  con-name bond0-slave1 \
  ifname ens3 \
  master bond0 \
  slave-type bond

# 3. Add ens4 as the second slave (standby)
sudo nmcli connection add \
  type ethernet \
  con-name bond0-slave2 \
  ifname ens4 \
  master bond0 \
  slave-type bond

# 4. Assign a static IP to the bond
sudo nmcli connection modify bond0 \
  ipv4.method manual \
  ipv4.addresses "192.168.1.200/24" \
  ipv4.gateway "192.168.1.1" \
  ipv4.dns "192.168.1.53 8.8.8.8" \
  ipv6.method disabled \
  connection.autoconnect yes

# 5. Bring up the bond and its slaves
sudo nmcli connection up bond0
sudo nmcli connection up bond0-slave1
sudo nmcli connection up bond0-slave2

# 6. Verify bond status
cat /proc/net/bonding/bond0
# Should show: Currently Active Slave: ens3
# Bond Mode: fault-tolerance (active-backup)

# 7. Verify the IP is applied
ip addr show bond0

# 8. Test failover (simulate ens3 failure)
sudo ip link set ens3 down
sleep 3
cat /proc/net/bonding/bond0
# Currently Active Slave: ens4

# 9. Restore
sudo ip link set ens3 up

# 10. Verify persistent configuration
sudo nmcli connection show bond0 | grep ipv4.addresses
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

**1. Connection modified but not applied — changes not visible**

Symptom: `nmcli connection modify` succeeds but `ip addr show` still shows
the old IP.

Fix:
```bash
# Must explicitly activate the connection after modifying
sudo nmcli connection up "eth-static"
```

---

**2. Two connections auto-connect on the same interface — wrong one activates**

Symptom: wrong IP address applied at boot.

Fix:
```bash
nmcli connection show | grep ens3   # find all connections for ens3
# Set autoconnect-priority: higher number = preferred
sudo nmcli connection modify "eth-static" connection.autoconnect-priority 100
sudo nmcli connection modify "eth-dhcp" connection.autoconnect-priority 10
```

---

**3. DNS not applying from nmcli — resolved still uses old DNS**

Symptom: `nmcli connection show` shows correct DNS but `resolvectl status`
shows different servers.

Fix:
```bash
resolvectl status   # check which interface's DNS is active
# If NM's DNS is not being used:
sudo nmcli connection modify "eth-static" ipv4.ignore-auto-dns yes
sudo nmcli connection up "eth-static"
```

---

**4. Static route not persisting across reboots**

Symptom: `ip route add` adds the route but it disappears after reboot.

Fix:
```bash
# ip route add is temporary — use nmcli for persistence
sudo nmcli connection modify "eth-static" \
  +ipv4.routes "10.10.0.0/16 192.168.1.254"
sudo nmcli connection up "eth-static"
```

---

**5. Manual keyfile edit not picked up by NetworkManager**

Symptom: edited `/etc/NetworkManager/system-connections/...nmconnection`
but `nmcli connection show` still shows old values.

Fix:
```bash
sudo nmcli connection reload   # re-read all keyfiles
# Then reactivate:
sudo nmcli connection up "<name>"
```

---

**6. Bond not forming — slaves not joining**

Symptom: `cat /proc/net/bonding/bond0` shows no slaves.

Fix:
```bash
# Check that slave connections reference the correct master
nmcli connection show bond0-slave1 | grep master
# Should show: connection.master: bond0
# Also ensure the slave connections are activated:
sudo nmcli connection up bond0-slave1
sudo nmcli connection up bond0-slave2
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


[↑ Back to TOC](#toc)

## Next step

→ [Routing + Troubleshooting Method](02-routing-method.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
