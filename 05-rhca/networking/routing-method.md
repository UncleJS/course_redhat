# Routing + Troubleshooting Method

Routing issues are one of the most common (and most misdiagnosed) network
problems. A systematic method makes them fast to resolve.

---

## The Linux routing table

The kernel consults the routing table to decide where to send each packet.

```bash
# Show all routes
ip route show

# Or
ip r
```

Example output:

```
default via 192.168.1.1 dev ens3 proto dhcp metric 100
192.168.1.0/24 dev ens3 proto kernel scope link src 192.168.1.100
```

| Field | Meaning |
|---|---|
| `default via X` | Default gateway — used for all non-matching destinations |
| `192.168.1.0/24 dev ens3` | Local subnet — reach directly via ens3 |
| `proto kernel` | Added by the kernel when an IP is assigned |
| `metric 100` | Route priority (lower = preferred) |

---

## Route lookup

```bash
# Which route would be used for a specific destination?
ip route get 8.8.8.8

# Which route to reach another host?
ip route get 192.168.2.50
```

---

## Add and remove static routes

```bash
# Temporary (lost on reboot)
sudo ip route add 10.0.0.0/8 via 192.168.1.254
sudo ip route del 10.0.0.0/8 via 192.168.1.254

# Persistent via nmcli
sudo nmcli connection modify "eth-static" +ipv4.routes "10.0.0.0/8 192.168.1.254"
sudo nmcli connection up "eth-static"
```

---

## The routing + connectivity troubleshooting method

Work through this in order. Each step eliminates a layer.

### Step 1 — Is the interface up?

```bash
ip link show ens3
```

Look for: `state UP` and `LOWER_UP` (physical link up).

If `NO-CARRIER`: cable problem, wrong switch port, or VM adapter issue.
If `DOWN`: `sudo nmcli device connect ens3`

---

### Step 2 — Does the interface have an IP?

```bash
ip addr show ens3
```

Look for: a `inet` line with your expected IP.

If missing: check if NetworkManager has an active connection:
`nmcli device status`

---

### Step 3 — Can we reach the default gateway?

```bash
ip route show | grep default   # find gateway IP
ping -c 3 <gateway-IP>
```

If ping fails but interface is UP with an IP:
- Wrong gateway configured?
- Firewall on the gateway?
- Layer 2 problem (ARP)? → `ip neigh show`

---

### Step 4 — Can we reach an external IP (bypass DNS)?

```bash
ping -c 3 8.8.8.8
```

If this fails but gateway works: routing problem between you and the internet.
Check: is there a route to `0.0.0.0/0`? Is NAT configured on the router?

---

### Step 5 — Can we resolve names?

```bash
ping -c 3 access.redhat.com   # if fails but 8.8.8.8 works → DNS problem
resolvectl status
dig access.redhat.com
dig @8.8.8.8 access.redhat.com   # test with a known-good resolver
```

---

### Step 6 — Can we reach the target service?

```bash
# TCP reachability test
curl -v --max-time 5 http://192.168.1.50:80/
nc -zv 192.168.1.50 80

# Is the service listening on the remote?
ssh user@192.168.1.50 "ss -tlnp | grep :80"

# Is a local firewall blocking outbound?
sudo firewall-cmd --list-all
```

---

## Useful tools

```bash
# Show ARP table (layer 2 neighbours)
ip neigh show

# Trace path
traceroute 8.8.8.8
tracepath 8.8.8.8    # no root required

# Packet loss stats
mtr 8.8.8.8

# See what interfaces and IPs exist
ip -brief addr
ip -brief link
```

---

## Further reading

| Resource | Notes |
|---|---|
| [`ip-route` man page](https://man7.org/linux/man-pages/man8/ip-route.8.html) | Full routing table management reference |
| [iproute2 documentation](https://wiki.linuxfoundation.org/networking/iproute2) | Overview of the iproute2 toolset |
| [RHEL 10 — Configuring routing](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_networking/index) | Static routes, policy routing, and multipath |

---

## Next step

→ [tcpdump Guided Debugging](tcpdump.md)
