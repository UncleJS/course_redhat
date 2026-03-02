# Networking Basics — ip, ss
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Before configuring networking, you need to understand the current state of
the network stack. These read-only commands are your first tools.

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


[↑ Back to TOC](#toc)

---

## Network namespace quick view

```bash
# All network namespaces (relevant when using containers)
ip netns list
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`ip` man page](https://man7.org/linux/man-pages/man8/ip.8.html) | Full iproute2 command reference |
| [`ss` man page](https://man7.org/linux/man-pages/man8/ss.8.html) | Socket statistics — the modern `netstat` replacement |
| [RHEL 10 — Configuring and managing networking](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_networking/index) | Official networking guide |

---

## Next step

→ [NetworkManager (nmcli)](09-networkmanager-nmcli.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
