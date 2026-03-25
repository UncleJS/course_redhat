
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab: Debug DNS vs Routing vs Firewall
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCA
**Estimated time:** 45 minutes
**Topology:** Single VM

---
<a name="toc"></a>

## Table of contents

- [Overview](#overview)
- [Background](#background)
- [Prerequisites](#prerequisites)
- [Setup — install a simple web service](#setup-install-a-simple-web-service)
- [Fault 1 — DNS broken](#fault-1-dns-broken)
  - [Introduce the fault](#introduce-the-fault)
  - [Observe the symptom](#observe-the-symptom)
  - [Troubleshoot it](#troubleshoot-it)
  - [Fix it](#fix-it)
- [Fault 2 — Firewall blocking HTTP](#fault-2-firewall-blocking-http)
  - [Introduce the fault](#introduce-the-fault-1)
  - [Observe the symptom](#observe-the-symptom-1)
  - [Troubleshoot it](#troubleshoot-it-1)
  - [Fix it](#fix-it-1)
- [Fault 3 — SELinux context broken on web content](#fault-3-selinux-context-broken-on-web-content)
  - [Introduce the fault](#introduce-the-fault-2)
  - [Observe the symptom](#observe-the-symptom-2)
  - [Troubleshoot it](#troubleshoot-it-2)
  - [Fix it](#fix-it-2)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)
- [Cleanup](#cleanup)
- [Why this matters in production](#why-this-matters-in-production)


## Prerequisites

- Completed [Routing + Troubleshooting Method](../02-routing-method.md) and [tcpdump Guided Debugging](../03-tcpdump.md)
- `tcpdump` installed: `sudo dnf install -y tcpdump`
- VM snapshot taken

---


[↑ Back to TOC](#toc)

## Overview

This lab introduces three deliberate network faults. For each fault:
1. You observe the symptom
2. You apply the troubleshooting method to identify the cause
3. You apply the fix and verify

No solutions are given upfront — work through each fault yourself.


[↑ Back to TOC](#toc)

---

## Background

The single most time-consuming class of incidents in RHEL environments is
misidentifying the layer of a connectivity problem. A "can't reach the web
server" complaint may be caused by any of five distinct root causes — each
requiring a different fix and each producing similar surface symptoms.

The five-layer diagnostic stack (from lowest to highest) is:

1. **Physical/link** — cable, NIC, interface state (`ip link show`)
2. **Routing** — wrong gateway, missing route, wrong IP (`ip route`, `ip addr`)
3. **Firewall** — firewalld, nftables, iptables blocking the port (`firewall-cmd --list-all`)
4. **SELinux** — mandatory access control denying file or network access (`ausearch -m avc`)
5. **Application** — service not running, wrong port, misconfiguration (`ss -tlnp`, logs)

This lab exercises faults at layers 3, 3.5 (DNS), and 4 — the three most
common causes in a running RHEL system where the physical layer is correct.
The key skill is **not jumping to layer 5** (restart the service) before
verifying layer 3 and 4.

Each fault in this lab is designed to produce symptoms that could be
mistaken for another fault. Fault 1 (DNS) will look like the network is down
to anyone who jumps to `ping hostname` without trying `ping IP-address`. Fault 2
(firewall) will look like the service is broken to anyone who does not check
port state. Fault 3 (SELinux) will look like a permissions bug in the web
server configuration.


[↑ Back to TOC](#toc)

---

## Setup — install a simple web service

```bash
sudo dnf install -y httpd
sudo systemctl enable --now httpd
echo "<h1>Lab web server</h1>" | sudo tee /var/www/html/index.html
sudo restorecon -v /var/www/html/index.html
```

Verify the baseline works:

```bash
curl http://localhost/
```

Expected: `Lab web server`

Take a VM snapshot here so you can reset between fault exercises:

```bash
# On RHEL with virsh (if this is a VM):
# sudo virsh snapshot-create-as <vmname> pre-fault-lab "clean baseline"
```


[↑ Back to TOC](#toc)

---

## Fault 1 — DNS broken

### Introduce the fault

```bash
sudo nmcli connection modify "$(nmcli -g NAME connection show --active | head -1)" \
  ipv4.dns "192.168.255.254"
sudo nmcli connection up "$(nmcli -g NAME connection show --active | head -1)"
```

### Observe the symptom

```bash
ping -c 2 access.redhat.com
```

Expected: name resolution fails.

### Troubleshoot it

Use the tools from [Routing + Troubleshooting Method](../02-routing-method.md).
Work out:
- Can you ping `8.8.8.8` (IP, no DNS)?
- What does `resolvectl status` show?
- What does `dig @8.8.8.8 access.redhat.com` return?
- What DNS server is being used?

```bash
# Guided diagnostic sequence:
ping -c 2 8.8.8.8               # step 4: IP connectivity works
resolvectl status               # step 5: check configured DNS servers
dig access.redhat.com           # sends query to configured DNS
dig @8.8.8.8 access.redhat.com  # bypasses configured DNS — works?
nmcli connection show "$(nmcli -g NAME connection show --active | head -1)" \
  | grep ipv4.dns               # confirm the bad DNS value
```

### Fix it

Restore the correct DNS server using `nmcli`.

> **✅ Verify**
> ```bash
> ping -c 2 access.redhat.com
> ```
> Name resolves successfully.


[↑ Back to TOC](#toc)

---

## Fault 2 — Firewall blocking HTTP

### Introduce the fault

```bash
sudo firewall-cmd --permanent --remove-service=http
sudo firewall-cmd --reload
```

### Observe the symptom

From a second terminal (or using `curl` with a timeout):

```bash
curl --max-time 5 http://127.0.0.1/
```

Or test from another host if available.

### Troubleshoot it

Work out:
- Is httpd running? (`systemctl status httpd`)
- Is it listening? (`ss -tlnp | grep :80`)
- What does `firewall-cmd --list-all` show?
- Is it SELinux? (`ausearch -m avc -ts recent`)

```bash
# Guided diagnostic sequence:
systemctl status httpd           # is the service up?
ss -tlnp | grep :80              # is it listening?
sudo firewall-cmd --list-all     # is port 80 or service http listed?
sudo ausearch -m avc -ts recent  # any SELinux denials?
# If no AVC denials and port is listening → firewall is the culprit
```

### Fix it

Open the correct port/service in firewalld.

> **✅ Verify**
> ```bash
> curl http://localhost/
> ```
> Returns the web page.


[↑ Back to TOC](#toc)

---

## Fault 3 — SELinux context broken on web content

### Introduce the fault

```bash
sudo chcon -t var_t /var/www/html/index.html
```

This changes the file's SELinux context to the wrong type.

### Observe the symptom

```bash
curl http://localhost/
```

Expected: `403 Forbidden` (httpd can't read the file).

### Troubleshoot it

Work out:
- Is httpd running?
- Is port 80 open in firewalld?
- What does `ls -Z /var/www/html/index.html` show?
- Are there AVC denials? (`ausearch -m avc -ts recent`)

```bash
# Guided diagnostic sequence:
systemctl status httpd                        # service running? ✓
sudo firewall-cmd --list-services            # http present? ✓
ls -Z /var/www/html/index.html               # check SELinux type
# Expected: httpd_sys_content_t
# Actual:   var_t  ← wrong type
sudo ausearch -m avc -ts recent             # confirm AVC denial
# type=AVC ... denied { read } ... tcontext=var_t
```

### Fix it

Apply the correct SELinux label using `restorecon`.

> **✅ Verify**
> ```bash
> curl http://localhost/
> ausearch -m avc -ts recent
> ```
> Page loads. No new AVC denials.


[↑ Back to TOC](#toc)

---

## Troubleshooting guide

| Symptom | Likely layer | Key diagnostic command | Fix |
|---|---|---|---|
| `curl: (6)` name not resolved | DNS (layer 3.5) | `resolvectl status`; `dig @8.8.8.8 hostname` | Restore correct DNS server via `nmcli` |
| `curl: (7)` connection refused | Application/firewall | `ss -tlnp \| grep :80`; `firewall-cmd --list-all` | Start the service or open the firewall port |
| `curl: (7)` connection timed out | Firewall DROP rule | `firewall-cmd --list-all`; `tcpdump -i lo port 80` | Add the `http` service or port to firewalld |
| HTTP 403 Forbidden | SELinux (layer 4) | `ls -Z /var/www/html/`; `ausearch -m avc -ts recent` | `restorecon -Rv /var/www/html/` |
| HTTP 500 Internal Server Error | Application | `journalctl -u httpd -n 50`; check error_log | Application-specific; check config |
| `ping` works but `curl` fails | Firewall or application | `nc -zv host 80`; `ss -tlnp` | Open firewall port; start service |
| `dig` returns SERVFAIL | DNS server unreachable or misconfigured | `dig @<dns-server> <name>`; `ping <dns-server>` | Fix DNS server address in nmcli |
| `403` on restart after `restorecon` | Wrong default context in policy | `semanage fcontext -l \| grep /var/www` | `semanage fcontext -a -t httpd_sys_content_t '/var/www/html(/.*)?'` |


[↑ Back to TOC](#toc)

---

## Extension tasks

### Extension 1 — Add a fourth fault: routing

After completing the three main faults, add a routing fault:

```bash
# Fault 4: remove the default gateway
sudo ip route del default

# Observe: local curl still works (localhost, no routing needed)
curl http://localhost/       # still works

# But external traffic fails:
ping -c 2 8.8.8.8           # fails
curl http://192.168.1.50/   # fails (if that's an external host)

# Diagnose:
ip route show | grep default  # no default route
ip route get 8.8.8.8          # RTNETLINK answers: Network is unreachable

# Fix: restore the default route (temporary)
sudo ip route add default via 192.168.122.1

# Fix permanently via nmcli:
sudo nmcli connection modify "$(nmcli -g NAME connection show --active | head -1)" \
  ipv4.gateway "192.168.122.1"
sudo nmcli connection up "$(nmcli -g NAME connection show --active | head -1)"
```

---

### Extension 2 — Introduce all three faults simultaneously

A harder variant: introduce faults 1, 2, and 3 simultaneously, then
diagnose which layer is broken first. The correct diagnostic order is:

1. Routing check (`ip route`, `ping 8.8.8.8`)
2. DNS check (`dig @8.8.8.8 hostname`, `resolvectl status`)
3. Service listening check (`ss -tlnp`)
4. Firewall check (`firewall-cmd --list-all`)
5. SELinux check (`ausearch -m avc`, `ls -Z`)

Work from lowest layer to highest — fixing the firewall before confirming
DNS is pointless if DNS is also broken.

```bash
# Introduce all three faults at once
sudo nmcli connection modify "$(nmcli -g NAME connection show --active | head -1)" \
  ipv4.dns "192.168.255.254"
sudo nmcli connection up "$(nmcli -g NAME connection show --active | head -1)"

sudo firewall-cmd --permanent --remove-service=http
sudo firewall-cmd --reload

sudo chcon -t var_t /var/www/html/index.html

# Now diagnose and fix all three in the correct order
```

---

### Extension 3 — Use tcpdump to confirm each fault

For each fault, use `tcpdump` to provide evidence of the failure mechanism:

**DNS fault evidence:**
```bash
sudo tcpdump -n -i ens3 port 53 &
dig access.redhat.com
# Observe: DNS query sent to 192.168.255.254, no response (timeout)
kill %1
```

**Firewall fault evidence:**
```bash
sudo tcpdump -n -i lo port 80 &
curl --max-time 3 http://localhost/
# Observe: SYN packet sent but no SYN-ACK (firewall drops it)
# OR: no packets at all (firewall drops before reaching loopback)
kill %1
```

**SELinux fault evidence:**
```bash
curl http://localhost/   # 403
sudo ausearch -m avc -ts recent | grep httpd
# AVC denial shows:
# scontext=httpd_t tcontext=var_t tclass=file permissive=0
```


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
sudo systemctl disable --now httpd
sudo firewall-cmd --permanent --add-service=http 2>/dev/null || true
sudo firewall-cmd --reload
sudo restorecon -Rv /var/www/html/
```

Restore correct DNS:

```bash
sudo nmcli connection modify "$(nmcli -g NAME connection show --active | head -1)" \
  ipv4.dns "192.168.122.1 8.8.8.8"
sudo nmcli connection up "$(nmcli -g NAME connection show --active | head -1)"
```

---


[↑ Back to TOC](#toc)

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `curl: (6)` name not resolved | DNS fault not cleared | Re-run DNS fix steps |
| 403 persists after restorecon | Wrong context after chcon | `restorecon -v /var/www/html/index.html` |
| http still blocked | Permanent firewall rule but no reload | `sudo firewall-cmd --reload` |

---


[↑ Back to TOC](#toc)

## Why this matters in production

The single most time-consuming class of incidents in RHEL environments
is misidentifying the layer of a network problem: "it must be SELinux" when
it's actually firewalld, or "restart the service" when DNS is broken. This
lab builds the muscle memory for the diagnostic order: routing → DNS →
firewall → SELinux → application.

The pattern holds for container environments too: a container that cannot
reach an external service may have a routing issue (no default gateway in
the container network), a DNS issue (wrong nameserver in the container's
`/etc/resolv.conf`), a firewall issue (firewalld on the host blocking
outbound), or an SELinux issue (container_t denied network access). The
diagnostic order is the same.

---


[↑ Back to TOC](#toc)

## Next step

→ [Performance Resource Triage](../../perf/01-resource-triage.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
