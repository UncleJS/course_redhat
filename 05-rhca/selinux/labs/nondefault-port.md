# Lab: Non-Default Port — Correct SELinux Fix

**Track:** RHCA
**Estimated time:** 40 minutes
**Topology:** Single VM

---

## Prerequisites

- Completed [Fix Taxonomy](../fix-taxonomy.md), [semanage](../semanage.md), and [Audit Workflow](../audit-workflow.md)
- httpd installed: `sudo dnf install -y httpd`
- SELinux tools: `sudo dnf install -y policycoreutils-python-utils`
- VM snapshot taken

---

## Success criteria

- httpd serves content on port 9090
- The fix uses `semanage port` (not `setenforce 0`, not disabling firewalld)
- AVC denials are visible before the fix and absent after
- firewalld is correctly configured for port 9090

---

## Steps

### 1 — Configure httpd to listen on port 9090

```bash
sudo vim /etc/httpd/conf/httpd.conf
```

Find the `Listen 80` line and change it to:

```
Listen 9090
```

### 2 — Try to start httpd (expect failure)

```bash
sudo systemctl restart httpd
sudo systemctl status httpd
```

Expected: httpd fails to start.

### 3 — Read the audit log

```bash
sudo ausearch -m avc -ts recent
```

You should see a denial like:

```
denied { name_bind } for pid=... comm="httpd" src=9090
scontext=system_u:system_r:httpd_t:s0
tcontext=system_u:object_r:unreserved_port_t:s0
```

The key: `name_bind` denied, port 9090, context `unreserved_port_t`.
httpd is allowed to bind `http_port_t` ports — but 9090 is `unreserved_port_t`.

### 4 — Confirm with audit2why

```bash
sudo ausearch -m avc -ts recent | sudo audit2why
```

Look for: "SELinux is preventing httpd from name_bind access on the tcp_socket port 9090."

It should suggest a boolean (`httpd_can_network_relabelfrom`) or a `semanage port` fix.
The correct fix is `semanage port`.

### 5 — Apply the correct fix

```bash
# Check what's currently assigned to http_port_t
sudo semanage port -l | grep http_port

# Add port 9090 to http_port_t
sudo semanage port -a -t http_port_t -p tcp 9090
```

> **✅ Verify policy**
> ```bash
> sudo semanage port -l | grep 9090
> ```
> Look for: `http_port_t  tcp  9090, ...`
>

### 6 — Open port 9090 in firewalld

```bash
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --reload
```

### 7 — Start httpd and verify

```bash
sudo systemctl restart httpd
sudo systemctl status httpd
```

Expected: `Active: active (running)`

```bash
curl http://localhost:9090/
```

Expected: the RHEL test page or 403 (content root is empty) — but NOT a connection refused.

> **✅ Verify — No new AVC denials**
> ```bash
> sudo ausearch -m avc -ts recent
> ```
> No new denials related to httpd and port 9090.
>

### 8 — Confirm with ss

```bash
ss -tlnp | grep :9090
```

Look for: httpd/httpd worker listening on `:9090`.

---

## Cleanup

```bash
sudo systemctl disable --now httpd
sudo firewall-cmd --permanent --remove-port=9090/tcp
sudo firewall-cmd --reload
sudo semanage port -d -t http_port_t -p tcp 9090
# Restore httpd.conf
sudo vim /etc/httpd/conf/httpd.conf   # change Listen 9090 back to Listen 80
```

---

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| httpd still fails after semanage | firewalld not opened | `firewall-cmd --permanent --add-port=9090/tcp` |
| `semanage port -a` fails with "already defined" | Port has a conflicting existing label | Use `-m` (modify) instead of `-a` |
| No AVC in audit log | auditd not running | `sudo systemctl start auditd` |
| curl returns "connection refused" | SELinux fix applied but service not restarted | `sudo systemctl restart httpd` |

---

## Why this matters in production

Microservices, custom applications, and legacy software commonly run on
non-standard ports. The correct RHEL workflow is always: identify the port's
SELinux type requirement → `semanage port -a` → `firewall-cmd --permanent`.
Skipping either step creates either a security gap or a broken service.
