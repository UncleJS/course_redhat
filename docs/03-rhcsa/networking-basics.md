# Networking Basics — ip, ss

Before configuring networking, you need to understand the current state of
the network stack. These read-only commands are your first tools.

---

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

---

## Network interface states

| State | Meaning |
|---|---|
| `UP` | Administratively enabled |
| `LOWER_UP` | Physical link is up (cable connected or WiFi associated) |
| `DOWN` | Interface disabled |
| `NO-CARRIER` | Interface up but no physical link |

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

---

## Network namespace quick view

```bash
# All network namespaces (relevant when using containers)
ip netns list
```

---

## Next step

→ [NetworkManager (nmcli)](networkmanager-nmcli.md)
