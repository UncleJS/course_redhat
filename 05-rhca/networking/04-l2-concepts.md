
[↑ Back to TOC](#toc)

# VLAN, Bridge, Bond Concepts (Optional)
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

This chapter covers the concepts behind three advanced NIC configurations
used in RHEL infrastructure: VLANs, bridges, and bonds. Labs are optional
because they require specific network environments.

At RHCA level, these three technologies frequently appear together in a
single server configuration — particularly on hypervisor hosts running KVM,
and on servers that carry multiple network functions (management, storage,
and VM traffic) over a limited number of physical NICs. Understanding how
they compose lets you design and troubleshoot complex network stacks.

The mental model for each technology:

- **Bonding** operates at Layer 2 and combines multiple physical NICs into
  one logical interface. From the perspective of the rest of the network
  stack, the bond interface looks like a single NIC. The bonding driver in
  the kernel handles balancing, failover, and heartbeat (miimon) across the
  physical slaves.

- **VLANs** also operate at Layer 2 and use 802.1Q frame tagging to carry
  traffic for multiple isolated networks over a single physical or logical
  interface. The switch must be configured to pass 802.1Q tags on trunk ports.
  On the Linux host, each VLAN is a virtual interface (e.g., `bond0.100`)
  that presents tagged frames as untagged to the protocols above it.

- **Bridges** operate at Layer 2 and forward frames between connected
  interfaces based on learned MAC addresses — exactly like a hardware switch,
  but implemented in software. Bridges are used to connect VMs and containers
  to physical networks by making the hypervisor/host act as a switch.

These three compose in a standard hypervisor stack: two physical NICs form
a bond → the bond carries multiple VLANs → each VLAN interface connects to
a bridge → virtual machines connect to the bridges.

---
<a name="toc"></a>

## Table of contents

- [Bonding — link aggregation](#bonding-link-aggregation)
  - [Bonding modes](#bonding-modes)
  - [Create a bond with nmcli](#create-a-bond-with-nmcli)
- [VLANs — logical network segmentation](#vlans-logical-network-segmentation)
  - [Create a VLAN interface](#create-a-vlan-interface)
- [Bridges — software layer 2 switch](#bridges-software-layer-2-switch)
  - [Create a bridge](#create-a-bridge)
- [Combining: bond + VLAN + bridge](#combining-bond-vlan-bridge)
- [Verify layer 2 config](#verify-layer-2-config)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## Bonding — link aggregation

Bonding combines multiple physical interfaces into one logical interface
for **redundancy**, **throughput**, or both.

### Bonding modes

| Mode | Name | Use case |
|---|---|---|
| 0 | `balance-rr` | Round-robin; throughput, no switch config needed |
| 1 | `active-backup` | One active, one standby; simple failover |
| 2 | `balance-xor` | XOR hash; switch must support |
| 4 | `802.3ad` (LACP) | Dynamic link aggregation; most common in production |
| 5 | `balance-tlb` | Adaptive transmit load balancing |
| 6 | `balance-alb` | Adaptive load balancing (both directions) |

**Production guidance:** Use `802.3ad` (LACP) when the switch supports it —
this is the most reliable and performant mode. Use `active-backup` for simple
failover when the switch does not support LACP or as a fallback.

`miimon=100` sets the link monitoring interval to 100ms — the bond driver
checks slave link state every 100ms and fails over within 100ms of a
physical link failure.

### Create a bond with nmcli

```bash
# Create bond interface
sudo nmcli connection add type bond \
  con-name bond0 \
  ifname bond0 \
  bond.options "mode=active-backup,miimon=100"

# Add slave interfaces
sudo nmcli connection add type ethernet \
  con-name bond0-slave1 \
  ifname ens3 \
  master bond0

sudo nmcli connection add type ethernet \
  con-name bond0-slave2 \
  ifname ens4 \
  master bond0

# Configure IP on the bond
sudo nmcli connection modify bond0 \
  ipv4.method manual \
  ipv4.addresses 192.168.1.100/24 \
  ipv4.gateway 192.168.1.1

# Bring it up
sudo nmcli connection up bond0
sudo nmcli connection up bond0-slave1
sudo nmcli connection up bond0-slave2
```

```bash
# Check bond status
cat /proc/net/bonding/bond0
```

Verify output includes:
- `Bonding Mode: fault-tolerance (active-backup)` (or your chosen mode)
- `Currently Active Slave: ens3`
- `MII Status: up` for each slave
- `Link Failure Count: 0`


[↑ Back to TOC](#toc)

---

## VLANs — logical network segmentation

VLANs let one physical interface carry traffic for multiple networks by
tagging frames with an 802.1Q VLAN ID. The switch must be configured to
allow these tags (trunk port).

Key VLAN concepts:
- **Access port**: switch port that strips tags — one VLAN, untagged frames
- **Trunk port**: switch port that passes tagged frames — multiple VLANs
- **Native VLAN**: the untagged VLAN on a trunk port (often VLAN 1)
- **802.1Q tag**: 4-byte header inserted into the Ethernet frame containing
  the VLAN ID (12 bits → VIDs 1–4094)

### Create a VLAN interface

```bash
# VLAN 100 on interface ens3
sudo nmcli connection add type vlan \
  con-name vlan100 \
  ifname ens3.100 \
  dev ens3 \
  id 100 \
  ipv4.method manual \
  ipv4.addresses 10.100.0.10/24 \
  ipv4.gateway 10.100.0.1

sudo nmcli connection up vlan100
```

```bash
# Verify
ip addr show ens3.100
ip -d link show ens3.100   # -d flag shows VLAN details
# Should show: vlan id 100 ...
```

Multiple VLANs on the same parent interface:

```bash
sudo nmcli connection add type vlan \
  con-name vlan200 ifname ens3.200 dev ens3 id 200 \
  ipv4.method manual ipv4.addresses 10.200.0.10/24

sudo nmcli connection up vlan200
```


[↑ Back to TOC](#toc)

---

## Bridges — software layer 2 switch

A bridge connects multiple interfaces at layer 2. On RHEL, bridges are
used for:

- KVM/libvirt virtual machine networking
- Container networking
- Connecting VLANs

### Create a bridge

```bash
# Create bridge
sudo nmcli connection add type bridge \
  con-name br0 \
  ifname br0 \
  ipv4.method manual \
  ipv4.addresses 192.168.1.100/24 \
  ipv4.gateway 192.168.1.1

# Add ens3 as a bridge slave
sudo nmcli connection add type ethernet \
  con-name br0-slave \
  ifname ens3 \
  master br0

sudo nmcli connection up br0
sudo nmcli connection up br0-slave
```

After bringing up the bridge, the physical interface (`ens3`) no longer has
its own IP — it acts as a bridge port. The bridge interface (`br0`) takes
the IP. Machines connected to the same switch as `ens3` can communicate
with VMs attached to `br0` at Layer 2.

```bash
# Verify bridge members
bridge link show br0
# ens3: state forwarding  <- slave port is active
```


[↑ Back to TOC](#toc)

---

## Combining: bond + VLAN + bridge

A production stack for a hypervisor host:

```text
Physical NIC (ens3, ens4)
    └── Bond (bond0, mode=LACP)
          ├── VLAN 10 (ens3.10) → Bridge br-mgmt (management traffic)
          ├── VLAN 20 (ens3.20) → Bridge br-vm   (VM traffic)
          └── VLAN 30 (ens3.30) → Bridge br-stor  (storage traffic)
```

Each bridge is then the network backend for KVM virtual machines.

Building this stack with nmcli:

```bash
# 1. Bond
sudo nmcli connection add type bond con-name bond0 ifname bond0 \
  bond.options "mode=802.3ad,miimon=100,lacp_rate=1"
sudo nmcli connection add type ethernet con-name bond0-s1 ifname ens3 master bond0
sudo nmcli connection add type ethernet con-name bond0-s2 ifname ens4 master bond0

# 2. VLAN interfaces on the bond (NOT on ens3/ens4 directly)
sudo nmcli connection add type vlan con-name vlan10 ifname bond0.10 dev bond0 id 10
sudo nmcli connection add type vlan con-name vlan20 ifname bond0.20 dev bond0 id 20

# 3. Bridges for each VLAN
sudo nmcli connection add type bridge con-name br-mgmt ifname br-mgmt \
  ipv4.method manual ipv4.addresses 10.10.0.1/24
sudo nmcli connection add type bridge con-name br-vm ifname br-vm \
  ipv4.method disabled ipv6.method disabled

# 4. Add VLAN interfaces as bridge slaves
sudo nmcli connection add type vlan con-name vlan10-br ifname bond0.10 \
  dev bond0 id 10 master br-mgmt
sudo nmcli connection add type vlan con-name vlan20-br ifname bond0.20 \
  dev bond0 id 20 master br-vm

# 5. Bring everything up in dependency order
sudo nmcli connection up bond0
sudo nmcli connection up bond0-s1
sudo nmcli connection up bond0-s2
sudo nmcli connection up vlan10-br
sudo nmcli connection up vlan20-br
sudo nmcli connection up br-mgmt
sudo nmcli connection up br-vm
```


[↑ Back to TOC](#toc)

---

## Verify layer 2 config

```bash
# Show all bridge information
bridge link show
bridge vlan show

# Check bond slaves
cat /proc/net/bonding/bond0

# Check VLAN interfaces
ip -d link show ens3.100

# Show all interfaces in brief
ip -brief link

# Bridge forwarding table (learned MACs)
bridge fdb show br0

# Check bridge spanning tree state
bridge stp state br0
```


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** A server with two NICs (`ens3` and `ens4`) needs a bonded
interface for redundancy. The bond must carry two VLANs: VLAN 100 for
management traffic and VLAN 200 for application traffic.

```bash
# 1. Delete any existing connections on ens3/ens4
sudo nmcli connection delete "Wired connection 1" 2>/dev/null || true
sudo nmcli connection delete "Wired connection 2" 2>/dev/null || true

# 2. Create bond (active-backup for simplicity)
sudo nmcli connection add type bond \
  con-name bond0 \
  ifname bond0 \
  bond.options "mode=active-backup,miimon=100"

# 3. Add slaves
sudo nmcli connection add type ethernet \
  con-name bond0-slave1 ifname ens3 master bond0
sudo nmcli connection add type ethernet \
  con-name bond0-slave2 ifname ens4 master bond0

# 4. Disable IP on the bond itself (IPs go on the VLAN interfaces)
sudo nmcli connection modify bond0 \
  ipv4.method disabled \
  ipv6.method disabled

# 5. Create VLAN 100 (management) on the bond
sudo nmcli connection add type vlan \
  con-name vlan100 ifname bond0.100 dev bond0 id 100 \
  ipv4.method manual \
  ipv4.addresses "10.100.0.10/24" \
  ipv4.gateway "10.100.0.1" \
  ipv4.dns "10.100.0.53"

# 6. Create VLAN 200 (application) on the bond
sudo nmcli connection add type vlan \
  con-name vlan200 ifname bond0.200 dev bond0 id 200 \
  ipv4.method manual \
  ipv4.addresses "10.200.0.10/24"

# 7. Bring everything up
sudo nmcli connection up bond0
sudo nmcli connection up bond0-slave1
sudo nmcli connection up bond0-slave2
sudo nmcli connection up vlan100
sudo nmcli connection up vlan200

# 8. Verify bond status
cat /proc/net/bonding/bond0

# 9. Verify VLAN interfaces have IPs
ip addr show bond0.100
ip addr show bond0.200

# 10. Verify VLAN tagging
ip -d link show bond0.100 | grep vlan
# vlan id 100 ...

# 11. Test management connectivity
ping -c 2 -I bond0.100 10.100.0.1

# 12. Simulate failover — bring down the active slave
sudo ip link set ens3 down
sleep 2
cat /proc/net/bonding/bond0   # ens4 should now be active
ping -c 2 10.100.0.1          # should still work
sudo ip link set ens3 up
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

**1. IP configured on physical interface instead of bond — loses IP on failover**

Symptom: IP is on `ens3` directly; when `ens3` fails, the IP is lost even
though the bond should keep connectivity.

Fix:
```bash
# Remove IP from physical interface, assign to bond
sudo nmcli connection modify "Wired connection 1" ipv4.method disabled
sudo nmcli connection modify bond0 \
  ipv4.method manual ipv4.addresses 192.168.1.100/24 ipv4.gateway 192.168.1.1
```

---

**2. VLAN interface created on physical NIC instead of bond**

Symptom: VLANs on `ens3.100` instead of `bond0.100` — VLAN fails over when
`ens3` goes down even though the bond should absorb the failure.

Fix:
```bash
# Delete incorrect VLAN connection
sudo nmcli connection delete vlan100
# Recreate with bond0 as parent
sudo nmcli connection add type vlan con-name vlan100 \
  ifname bond0.100 dev bond0 id 100 ...
```

---

**3. Bond not forming — switch not configured for LACP**

Symptom: `mode=802.3ad` bond shows slaves as "down" or not bonding.

Fix:
```bash
cat /proc/net/bonding/bond0   # check slave status
# If slaves show "MII Status: down" even though links are up:
# Switch port is not configured for LACP
# Either configure the switch for LACP, or switch bond mode to active-backup
sudo nmcli connection modify bond0 \
  bond.options "mode=active-backup,miimon=100"
sudo nmcli connection up bond0
```

---

**4. Bridge causes network loop — STP not enabled**

Symptom: network becomes unreachable after adding a second NIC to a bridge.

Fix:
```bash
# Enable STP on the bridge
sudo nmcli connection modify br0 bridge.stp yes
sudo nmcli connection up br0
bridge stp state br0   # verify STP is running
```

---

**5. VM has no network — bridge slave not activated**

Symptom: bridge is up but VMs cannot reach the network.

Fix:
```bash
bridge link show   # check if the slave interface is listed
# If ens3 is not shown as a member:
sudo nmcli connection up br0-slave   # activate the slave connection
bridge link show   # ens3 should now show state forwarding
```

---

**6. Lost SSH access after creating a bridge**

Symptom: SSH session drops when bringing up the bridge.

Cause: IP moved from `ens3` to `br0`, but the network stack was not ready.

Fix: always perform bridge configuration changes at the console, or use a
script that brings up the bridge atomically:
```bash
# Atomic script to avoid losing connectivity
sudo nmcli connection modify br0 \
  ipv4.method manual ipv4.addresses 192.168.1.100/24 ipv4.gateway 192.168.1.1
sudo nmcli connection modify "Wired connection 1" ipv4.method disabled
sudo nmcli connection up br0 && sudo nmcli connection up br0-slave
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Configuring VLANs, bonds, and bridges](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_networking/index) | Official guide with nmcli and keyfile examples |
| [IEEE 802.1Q (VLAN standard)](https://standards.ieee.org/ieee/802.1Q/10422/) | Authoritative VLAN tagging specification |
| [Linux bonding documentation](https://www.kernel.org/doc/Documentation/networking/bonding.txt) | Kernel bonding modes and configuration |

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab: Debug DNS vs Routing vs Firewall](labs/01-debug-triad.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
