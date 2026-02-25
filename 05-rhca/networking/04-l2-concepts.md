# VLAN, Bridge, Bond Concepts (Optional)

This chapter covers the concepts behind three advanced NIC configurations
used in RHEL infrastructure: VLANs, bridges, and bonds. Labs are optional
because they require specific network environments.

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


[↑ Back to TOC](#toc)

---

## VLANs — logical network segmentation

VLANs let one physical interface carry traffic for multiple networks by
tagging frames with an 802.1Q VLAN ID. The switch must be configured to
allow these tags (trunk port).

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


[↑ Back to TOC](#toc)

---

## Combining: bond + VLAN + bridge

A production stack for a hypervisor host:

```
Physical NIC (ens3, ens4)
    └── Bond (bond0, mode=LACP)
          ├── VLAN 10 (ens3.10) → Bridge br-mgmt (management traffic)
          ├── VLAN 20 (ens3.20) → Bridge br-vm   (VM traffic)
          └── VLAN 30 (ens3.30) → Bridge br-stor  (storage traffic)
```

Each bridge is then the network backend for KVM virtual machines.


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

## Next step

→ [Lab: Debug DNS vs Routing vs Firewall](labs/01-debug-triad.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
