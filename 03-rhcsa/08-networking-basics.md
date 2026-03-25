
[↑ Back to TOC](#toc)

# Networking Basics — ip, ss
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Before configuring networking, you need to understand the current state of
the network stack. These read-only commands are your first tools.

Linux networking is built on a layered model: physical interfaces sit at the
bottom, kernel routing tables direct packets between interfaces, and sockets
represent the endpoints applications use to send and receive data. The tools
`ip` and `ss` give you a live view of each layer — interfaces, addresses,
routes, neighbour caches, and open sockets — without modifying anything.

The `ip` command is part of the **iproute2** suite and replaced the legacy
`ifconfig` / `route` / `arp` toolset. The `ss` command (socket statistics)
replaced `netstat`. Both ship by default on RHEL 10. If a legacy tool appears
to work, it is usually a compatibility shim calling the modern equivalent
under the hood — do not rely on it in scripts or exams.

These commands are purely observational. They query the kernel's current
in-memory state. Changes made here without NetworkManager do not persist
across reboots. To make permanent changes, use `nmcli` (covered in the
next chapter).

---
<a name="toc"></a>

## Table of contents

- [The `ip` command](#the-ip-command)
  - [View interfaces](#view-interfaces)
  - [View addresses](#view-addresses)
  - [View routes](#view-routes)
  - [View ARP/neighbour cache](#view-arpneighbour-cache)
- [Network interface states](#network-interface-states)
- [The `ss` command](#the-ss-command)
  - [Output columns (ss -tlnp)](#output-columns-ss-tlnp)
- [Common patterns](#common-patterns)
- [Checking connectivity](#checking-connectivity)
- [Hostname](#hostname)
- [Network namespace quick view](#network-namespace-quick-view)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)
- [Reading `ip link show` output in depth](#reading-ip-link-show-output-in-depth)
- [Reading `ip addr show` output in depth](#reading-ip-addr-show-output-in-depth)
- [Routing table deep dive](#routing-table-deep-dive)


## The `ip` command

`ip` is the modern replacement for `ifconfig`, `route`, and `arp`.

### View interfaces

```bash
# List all interfaces with state
ip link show

# Short form
ip l

# Show one interface
ip link show ens3
```

### View addresses

```bash
# Show all IP addresses
ip addr show

# Short form
ip a

# Show one interface
ip addr show ens3
```

### View routes

```bash
# Show routing table
ip route show

# Short form
ip r

# Show the route used for a specific destination
ip route get 8.8.8.8
```

### View ARP/neighbour cache

```bash
ip neigh show
```


[↑ Back to TOC](#toc)

---

## Network interface states

| State | Meaning |
|---|---|
| `UP` | Administratively enabled |
| `LOWER_UP` | Physical link is up (cable connected or WiFi associated) |
| `DOWN` | Interface disabled |
| `NO-CARRIER` | Interface up but no physical link |

An interface can be `UP` (administratively enabled) but still have `NO-CARRIER`
if nothing is physically connected, or if the virtual NIC's backing network has
no link. In a VM, `NO-CARRIER` usually means the virtual switch or network
adapter is misconfigured.

The flags also appear inside angle brackets in `ip link show` output, for
example: `<BROADCAST,MULTICAST,UP,LOWER_UP>`. `BROADCAST` and `MULTICAST`
tell you the interface supports those addressing modes — expected for all
Ethernet interfaces.


[↑ Back to TOC](#toc)

---

## The `ss` command

`ss` shows socket statistics — what is listening, what is connected.
It replaces `netstat`.

```bash
# All listening TCP ports
ss -tlnp

# All listening UDP ports
ss -ulnp

# All listening (TCP + UDP)
ss -tlnup

# All established connections
ss -tnp

# Show process name and PID
ss -tlnp
```

### Output columns (ss -tlnp)

| Column | Meaning |
|---|---|
| State | LISTEN, ESTABLISHED, etc. |
| Recv-Q | Receive queue size |
| Send-Q | Send queue size |
| Local Address:Port | Listening address |
| Peer Address:Port | Remote address (for established) |
| Process | PID and process name |

A `Local Address` of `0.0.0.0` means the service is listening on all IPv4
interfaces. `[::]` means all IPv6 interfaces (and on dual-stack systems,
often all IPv4 interfaces too). A specific address (e.g., `127.0.0.1`) means
the service is only reachable locally — not from the network.

> **Exam tip:** `ss -tlnp` is the fastest way to confirm whether a service is
> actually listening before blaming the firewall. If the port is not in the
> output, the service is either not running or misconfigured — the firewall is
> not the issue.


[↑ Back to TOC](#toc)

---

## Common patterns

```bash
# Is SSH listening?
ss -tlnp | grep :22

# What process is using port 80?
ss -tlnp | grep :80

# What ports is nginx listening on?
ss -tlnp | grep nginx

# How many established connections to port 443?
ss -tn state established | grep :443 | wc -l
```


[↑ Back to TOC](#toc)

---

## Checking connectivity

```bash
# ICMP reachability
ping -c 4 8.8.8.8
ping -c 4 access.redhat.com

# Traceroute
traceroute 8.8.8.8
tracepath 8.8.8.8   # no root required

# Test TCP port reachability
curl -v telnet://192.168.1.1:22
# or
nc -zv 192.168.1.1 22
```

When diagnosing connectivity problems, work down the stack:

1. `ping <gateway-ip>` — is Layer 3 reachable at all?
2. `ping 8.8.8.8` — can you reach the internet by IP (routing works)?
3. `ping access.redhat.com` — does DNS work?
4. `nc -zv <host> <port>` — is the specific application port open?

Each step isolates a different failure domain.


[↑ Back to TOC](#toc)

---

## Hostname

```bash
# Show all hostname info
hostnamectl

# Set hostname permanently
sudo hostnamectl set-hostname rhel10-lab

# Show only the static hostname
hostname
```

`hostnamectl` distinguishes between three hostname types:

| Type | Description |
|---|---|
| **Static** | The persistent name stored in `/etc/hostname` |
| **Transient** | A dynamic name set by DHCP or mDNS (may differ from static) |
| **Pretty** | A free-form human-readable label (optional, rarely used) |

For servers, static and transient should always match. Use `hostnamectl` to
set the static name — it writes `/etc/hostname` and notifies the running kernel.


[↑ Back to TOC](#toc)

---

## Network namespace quick view

```bash
# All network namespaces (relevant when using containers)
ip netns list
```

Network namespaces give each container or virtual network environment its own
isolated instance of the network stack — its own interfaces, routing table, and
firewall rules. Podman and other container runtimes use namespaces extensively.
On a plain VM with no containers, `ip netns list` returns nothing.


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** A new VM cannot reach its gateway at `192.168.122.1`. Diagnose
the problem using only read-only commands.

```bash
# Step 1 — is the interface up?
ip link show ens3
# Look for UP and LOWER_UP in the flags.
# If missing, the interface is down or has no physical link.

# Step 2 — does the interface have an IP address?
ip addr show ens3
# Look for an inet line like: inet 192.168.122.x/24
# If missing, DHCP failed or no static address is configured.

# Step 3 — is there a default route?
ip route show
# Look for: default via 192.168.122.1 dev ens3
# If missing, no gateway is configured.

# Step 4 — can we reach the gateway at Layer 3?
ping -c 3 192.168.122.1
# If this fails despite having an IP and route, the gateway is
# unreachable — possible VLAN mismatch or hypervisor issue.

# Step 5 — can we reach the internet by IP (bypasses DNS)?
ping -c 3 8.8.8.8

# Step 6 — does DNS work?
ping -c 3 access.redhat.com
resolvectl status
```

If step 2 shows no IP: run `nmcli` to check if a connection is active.
If step 3 shows no default route: the connection profile may have no gateway set.
If steps 4–5 fail: the problem is upstream (hypervisor network, VLAN, physical).
If step 6 fails but step 5 succeeds: DNS is misconfigured (see chapter 10).


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Symptom | Likely cause | Diagnosis | Fix |
|---|---|---|---|
| `ip a` shows no IP on interface | DHCP failed or no profile active | `nmcli connection show --active` | Bring up the connection: `nmcli connection up <name>` |
| Interface shows `NO-CARRIER` | No physical link / bad virtual NIC | `ip link show` flags | Check hypervisor virtual switch config |
| `ping 8.8.8.8` fails, IP present | Missing default route | `ip route show` — no `default` entry | Set gateway in connection profile: `nmcli ... ipv4.gateway` |
| `ping hostname` fails, IP ping works | DNS not configured | `resolvectl status` — no DNS server shown | Set DNS: `nmcli ... ipv4.dns "8.8.8.8"` |
| Service unreachable from network | Service listening only on loopback | `ss -tlnp` — Local Address is `127.0.0.1` | Reconfigure service to listen on `0.0.0.0` or specific interface |
| `ss -tlnp` shows port, but remote connect fails | Firewall blocking | Port visible in `ss` output but not reachable | `firewall-cmd --list-all` and open the port |


[↑ Back to TOC](#toc)

---

## Reading `ip link show` output in depth

A full `ip link show` line looks like:

```text
2: ens3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:ab:cd:ef brd ff:ff:ff:ff:ff:ff
```

Breaking it down:

| Field | Example | Meaning |
|---|---|---|
| Interface index | `2:` | Kernel-assigned number; loopback is always 1 |
| Interface name | `ens3` | Predictable interface name (PCI bus, slot, function) |
| Flags | `<BROADCAST,MULTICAST,UP,LOWER_UP>` | Capability and link-state flags |
| `mtu` | `1500` | Maximum Transmission Unit in bytes |
| `qdisc` | `fq_codel` | Queuing discipline — affects packet scheduling |
| `state` | `UP` | Operational state as seen by the kernel |
| `link/ether` | `52:54:00:ab:cd:ef` | MAC address |

Predictable interface names follow the naming scheme introduced by `udev`:

| Prefix | Type |
|---|---|
| `en` | Ethernet |
| `wl` | Wireless LAN |
| `ww` | Wireless WAN / mobile broadband |

After the prefix: `p<bus>s<slot>` for PCI devices (e.g., `enp1s0`), or `s<slot>` for
embedded/onboard NICs. In VMs, the naming often appears as `ens3`, `ens4` etc.

```bash
# Useful: see all interfaces in one compact view
ip -brief link show
# Output: lo    UNKNOWN  00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>
#         ens3  UP       52:54:00:ab:cd:ef <BROADCAST,MULTICAST,UP,LOWER_UP>
```


[↑ Back to TOC](#toc)

---

## Reading `ip addr show` output in depth

```text
2: ens3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 ...
    link/ether 52:54:00:ab:cd:ef brd ff:ff:ff:ff:ff:ff
    inet 192.168.122.100/24 brd 192.168.122.255 scope global dynamic ens3
       valid_lft 85746sec preferred_lft 85746sec
    inet6 fe80::5054:ff:feab:cdef/64 scope link
       valid_lft forever preferred_lft forever
```

| Field | Meaning |
|---|---|
| `inet` | IPv4 address with prefix length |
| `brd` | Broadcast address |
| `scope global` | Address usable for communication off this machine |
| `scope link` | Address usable only on this link (link-local) |
| `dynamic` | Address assigned by DHCP (not static) |
| `valid_lft` | DHCP lease validity countdown |
| `preferred_lft` | Time remaining at preferred lifetime |
| `inet6 fe80::...` | IPv6 link-local address (auto-assigned) |

A `scope host` address (like `127.0.0.1` on loopback) is only reachable
within the same machine — not even on the local link.

```bash
# Compact single-line view
ip -brief addr show
# ens3  UP  192.168.122.100/24 fe80::5054:ff:feab:cdef/64
```


[↑ Back to TOC](#toc)

---

## Routing table deep dive

```bash
ip route show
```

Example output:

```text
default via 192.168.122.1 dev ens3 proto dhcp src 192.168.122.100 metric 100
192.168.122.0/24 dev ens3 proto kernel scope link src 192.168.122.100
```

| Field | Meaning |
|---|---|
| `default via <ip>` | Default gateway — where packets go when no more-specific route matches |
| `<subnet> dev <iface>` | On-link route — destinations in this subnet are directly reachable |
| `proto dhcp` | Route was installed by DHCP |
| `proto kernel` | Route was auto-created when address was assigned |
| `metric 100` | Route preference — lower metric wins when multiple routes match |
| `src <ip>` | Preferred source address when sending from this route |

To see exactly which route would be used for a specific destination:

```bash
ip route get 10.0.0.1
# Output includes the interface, gateway, and source IP that would be used.
```

Multiple default routes (e.g., after adding a second interface) can cause
asymmetric routing. Check with `ip route show` and remove unneeded defaults.

```bash
# Add a static route
sudo ip route add 10.10.0.0/24 via 192.168.122.254

# Delete a route
sudo ip route del 10.10.0.0/24

# These are temporary — use nmcli for persistent routes:
sudo nmcli connection modify "Wired connection 1" \
  +ipv4.routes "10.10.0.0/24 192.168.122.254"
sudo nmcli connection up "Wired connection 1"
```

> **Exam tip:** Temporary `ip route add` commands vanish on reboot or when
> NetworkManager brings the interface back up. Use `nmcli ... +ipv4.routes`
> for persistent static routes that survive reboots.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`ip` man page](https://man7.org/linux/man-pages/man8/ip.8.html) | Full iproute2 command reference |
| [`ss` man page](https://man7.org/linux/man-pages/man8/ss.8.html) | Socket statistics — the modern `netstat` replacement |
| [RHEL 10 — Configuring and managing networking](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_networking/index) | Official networking guide |

---


[↑ Back to TOC](#toc)

## Next step

→ [NetworkManager (nmcli)](09-networkmanager-nmcli.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
