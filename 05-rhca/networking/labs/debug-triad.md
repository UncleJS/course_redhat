# Lab: Debug DNS vs Routing vs Firewall

**Track:** RHCA
**Estimated time:** 45 minutes
**Topology:** Single VM

---

## Prerequisites

- Completed [Routing + Troubleshooting Method](../routing-method.md) and [tcpdump Guided Debugging](../tcpdump.md)
- `tcpdump` installed: `sudo dnf install -y tcpdump`
- VM snapshot taken

---

## Overview

This lab introduces three deliberate network faults. For each fault:
1. You observe the symptom
2. You apply the troubleshooting method to identify the cause
3. You apply the fix and verify

No solutions are given upfront — work through each fault yourself.

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

Use the tools from [Routing + Troubleshooting Method](../routing-method.md).
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
