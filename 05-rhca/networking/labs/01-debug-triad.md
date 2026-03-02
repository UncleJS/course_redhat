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
- [Setup — install a simple web service](#setup-install-a-simple-web-service)
- [Fault 1 — DNS broken](#fault-1-dns-broken)
  - [Introduce the fault](#introduce-the-fault)
  - [Observe the symptom](#observe-the-symptom)
  - [Troubleshoot it](#troubleshoot-it)
  - [Fix it](#fix-it)
- [Fault 2 — Firewall blocking HTTP](#fault-2-firewall-blocking-http)
  - [Introduce the fault](#introduce-the-fault)
  - [Observe the symptom](#observe-the-symptom)
  - [Troubleshoot it](#troubleshoot-it)
  - [Fix it](#fix-it)
- [Fault 3 — SELinux context broken on web content](#fault-3-selinux-context-broken-on-web-content)
  - [Introduce the fault](#introduce-the-fault)
  - [Observe the symptom](#observe-the-symptom)
  - [Troubleshoot it](#troubleshoot-it)
  - [Fix it](#fix-it)


## Prerequisites

- Completed [Routing + Troubleshooting Method](../02-routing-method.md) and [tcpdump Guided Debugging](../03-tcpdump.md)
- `tcpdump` installed: `sudo dnf install -y tcpdump`
- VM snapshot taken

---

## Overview

This lab introduces three deliberate network faults. For each fault:
1. You observe the symptom
2. You apply the troubleshooting method to identify the cause
3. You apply the fix and verify

No solutions are given upfront — work through each fault yourself.


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

### Fix it

Restore the correct DNS server using `nmcli`.

> **✅ Verify**
> ```bash
> ping -c 2 access.redhat.com
> ```
> Name resolves successfully.
>


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

### Fix it

Open the correct port/service in firewalld.

> **✅ Verify**
> ```bash
> curl http://localhost/
> ```
> Returns the web page.
>


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

### Fix it

Apply the correct SELinux label using `restorecon`.

> **✅ Verify**
> ```bash
> curl http://localhost/
> ausearch -m avc -ts recent
> ```
> Page loads. No new AVC denials.
>


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

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `curl: (6)` name not resolved | DNS fault not cleared | Re-run DNS fix steps |
| 403 persists after restorecon | Wrong context after chcon | `restorecon -v /var/www/html/index.html` |
| http still blocked | Permanent firewall rule but no reload | `sudo firewall-cmd --reload` |

---

## Why this matters in production

The single most time-consuming class of incidents in RHEL environments
is misidentifying the layer of a network problem: "it must be SELinux" when
it's actually firewalld, or "restart the service" when DNS is broken. This
lab builds the muscle memory for the diagnostic order: routing → DNS →
firewall → SELinux → application.

---

## Next step

→ [Performance Resource Triage](../../perf/01-resource-triage.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
