
[↑ Back to TOC](#toc)

# tcpdump Guided Debugging
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

`tcpdump` captures network packets at the interface level. It is the most
powerful network debugging tool available on RHEL without installing anything.

---
<a name="toc"></a>

## Table of contents

- [Install](#install)
- [Basic usage](#basic-usage)
- [Filters (BPF syntax)](#filters-bpf-syntax)
- [Verbosity levels](#verbosity-levels)
- [Practical debugging scenarios](#practical-debugging-scenarios)
  - ["Is my DNS query leaving the host?"](#is-my-dns-query-leaving-the-host)
  - ["Is my HTTP request reaching the server?"](#is-my-http-request-reaching-the-server)
  - ["Is there a TCP handshake completing?"](#is-there-a-tcp-handshake-completing)
  - ["Capture traffic to a file and inspect later"](#capture-traffic-to-a-file-and-inspect-later)
- [Output format](#output-format)


## Install

```bash
sudo dnf install -y tcpdump
```


[↑ Back to TOC](#toc)

---

## Basic usage

```bash
# Capture on all interfaces, print to screen
sudo tcpdump -n

# Capture on a specific interface
sudo tcpdump -n -i ens3

# Capture and save to file (for later analysis)
sudo tcpdump -n -i ens3 -w /tmp/capture.pcap

# Read from a saved file
sudo tcpdump -n -r /tmp/capture.pcap
```

`-n` disables hostname resolution (much faster output).


[↑ Back to TOC](#toc)

---

## Filters (BPF syntax)

Filters make captures targeted and readable:

```bash
# Only traffic to/from a host
sudo tcpdump -n -i ens3 host 192.168.1.50

# Only traffic on a port
sudo tcpdump -n -i ens3 port 80
sudo tcpdump -n -i ens3 port 53    # DNS

# Only TCP traffic
sudo tcpdump -n -i ens3 tcp

# Only UDP
sudo tcpdump -n -i ens3 udp

# Combine filters
sudo tcpdump -n -i ens3 host 192.168.1.50 and port 443

# Source host
sudo tcpdump -n -i ens3 src host 10.0.0.1

# Destination host
sudo tcpdump -n -i ens3 dst host 8.8.8.8

# ICMP only
sudo tcpdump -n -i ens3 icmp
```


[↑ Back to TOC](#toc)

---

## Verbosity levels

```bash
-v     # verbose (TTL, IP ID, checksum)
-vv    # more verbose (full DNS/NTP decode)
-vvv   # maximum verbosity
-A     # print payload as ASCII
-X     # print payload as hex+ASCII
```


[↑ Back to TOC](#toc)

---

## Practical debugging scenarios

### "Is my DNS query leaving the host?"

```bash
sudo tcpdump -n -i ens3 port 53
```

Then in another terminal:

```bash
dig access.redhat.com
```

Watch for: outbound query on port 53 and the response. If no packets appear,
the query is being intercepted locally (check `/etc/hosts`, `systemd-resolved`).


[↑ Back to TOC](#toc)

---

### "Is my HTTP request reaching the server?"

On the **server**:

```bash
sudo tcpdump -n -i ens3 port 80 -A
```

On the **client**:

```bash
curl http://192.168.1.50/
```

If packets appear on the server: connection is reaching the server. Problem is
in the application (service not running, firewall on server app, SELinux).

If no packets appear: the traffic is being blocked before reaching the server
(routing, firewall on the way, NAT issues).


[↑ Back to TOC](#toc)

---

### "Is there a TCP handshake completing?"

```bash
sudo tcpdump -n -i ens3 "tcp[tcpflags] & (tcp-syn|tcp-ack) != 0"
```

Look for:
- `S` (SYN): client sending connection request
- `S.` (SYN-ACK): server accepting
- `.` (ACK): client acknowledging — handshake complete

If you see SYN but no SYN-ACK: server not listening or firewall dropping.
If you see SYN, SYN-ACK, RST: server resets the connection (port closed or SELinux).


[↑ Back to TOC](#toc)

---

### "Capture traffic to a file and inspect later"

```bash
# Capture 100 packets on port 443
sudo tcpdump -n -i ens3 port 443 -c 100 -w /tmp/https.pcap

# Read back with verbose output
sudo tcpdump -n -r /tmp/https.pcap -v
```


[↑ Back to TOC](#toc)

---

## Output format

```
HH:MM:SS.ffffff IP src > dst: flags seq ack win length
```

Example:

```
10:05:23.456789 IP 192.168.1.100.54321 > 8.8.8.8.53: Flags [S]
  seq 1234567, win 64240, length 0
```

| Part | Meaning |
|---|---|
| `192.168.1.100.54321` | Source IP.port |
| `8.8.8.8.53` | Destination IP.port |
| `Flags [S]` | SYN (connection attempt) |
| `[S.]` | SYN-ACK (server accepted) |
| `[.]` | ACK |
| `[P.]` | PUSH+ACK (data payload) |
| `[F.]` | FIN (connection close) |
| `[R]` | RST (connection reset/rejected) |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [tcpdump filter syntax](https://www.tcpdump.org/manpages/pcap-filter.7.html) | Full Berkeley Packet Filter (BPF) expression reference |
| [Wireshark — Display filters](https://wiki.wireshark.org/DisplayFilters) | GUI-based packet analysis — useful for reading pcap files from `tcpdump -w` |
| [*TCP/IP Illustrated, Vol. 1* by W. Richard Stevens](https://www.oreilly.com/library/view/tcpip-illustrated-volume/9780132808200/) | Definitive guide to understanding what you're capturing |

---


[↑ Back to TOC](#toc)

## Next step

→ [VLAN, Bridge, Bond Concepts](04-l2-concepts.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
