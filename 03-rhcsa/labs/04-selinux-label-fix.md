# Lab: Fix a SELinux Label Issue

**Track:** RHCSA
**Estimated time:** 30 minutes
**Topology:** Single VM

---
<a name="toc"></a>

## Table of contents

- [Steps](#steps)
  - [1 — Start httpd and confirm SELinux is enforcing](#1-start-httpd-and-confirm-selinux-is-enforcing)
  - [2 — Create content in the standard location (should work)](#2-create-content-in-the-standard-location-should-work)
  - [3 — Create a custom web root with wrong context](#3-create-a-custom-web-root-with-wrong-context)
  - [4 — Configure httpd to serve from the custom path](#4-configure-httpd-to-serve-from-the-custom-path)
  - [5 — Test — observe the failure](#5-test-observe-the-failure)
  - [6 — Apply the correct SELinux fix](#6-apply-the-correct-selinux-fix)
  - [7 — Test again — confirm fix works](#7-test-again-confirm-fix-works)


## Prerequisites

- Completed [SELinux Fundamentals](../13-selinux-fundamentals.md) and [SELinux Troubleshooting](../14-selinux-avc-basics.md)
- httpd installed: `sudo dnf install -y httpd`
- SELinux tools: `sudo dnf install -y policycoreutils-python-utils`
- VM snapshot taken

---

## Success criteria

- httpd serves content from `/var/www/html/` correctly
- httpd serves content from a custom path `/srv/webroot/` after correct SELinux fix
- The fix uses `semanage fcontext` + `restorecon` (not `setenforce 0`, not `chmod 777`)
- AVC denials are visible in audit log before the fix and absent after

---

## Steps

### 1 — Start httpd and confirm SELinux is enforcing

```bash
sudo systemctl enable --now httpd
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
getenforce
```

Expected: `Enforcing`


[↑ Back to TOC](#toc)

---

### 2 — Create content in the standard location (should work)

```bash
echo "<h1>Standard location works</h1>" | sudo tee /var/www/html/index.html
curl http://localhost/
```

> **✅ Verify**
> Output contains: `Standard location works`
>

Check the context:

```bash
ls -Z /var/www/html/index.html
```

Look for: `httpd_sys_content_t`


[↑ Back to TOC](#toc)

---

### 3 — Create a custom web root with wrong context

```bash
sudo mkdir -p /srv/webroot
echo "<h1>Custom location</h1>" | sudo tee /srv/webroot/index.html
ls -Z /srv/webroot/index.html
```

Note the context — it will be something like `default_t` or `var_t`, **not** `httpd_sys_content_t`.


[↑ Back to TOC](#toc)

---

### 4 — Configure httpd to serve from the custom path

```bash
sudo vim /etc/httpd/conf.d/custom.conf
```

```apache
<VirtualHost *:8080>
    DocumentRoot /srv/webroot
    <Directory /srv/webroot>
        Require all granted
    </Directory>
</VirtualHost>
```

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
sudo semanage port -a -t http_port_t -p tcp 8080 2>/dev/null || \
  sudo semanage port -m -t http_port_t -p tcp 8080
sudo systemctl restart httpd
```


[↑ Back to TOC](#toc)

---

### 5 — Test — observe the failure

```bash
curl http://localhost:8080/
```

Expected: `403 Forbidden` or connection refused.

Check the audit log:

```bash
sudo ausearch -m avc -ts recent
```

You should see an AVC denial showing httpd was denied access to `/srv/webroot/index.html`.


[↑ Back to TOC](#toc)

---

### 6 — Apply the correct SELinux fix

```bash
# Define the correct context for the custom path
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/webroot(/.*)?"

# Apply the context to existing files
sudo restorecon -Rv /srv/webroot/
```

> **✅ Verify context**
> ```bash
> ls -Z /srv/webroot/index.html
> ```
> Look for: `httpd_sys_content_t`
>


[↑ Back to TOC](#toc)

---

### 7 — Test again — confirm fix works

```bash
curl http://localhost:8080/
```

Expected: `<h1>Custom location</h1>`

Check audit log again:

```bash
sudo ausearch -m avc -ts recent
```

No new AVC denials for this request.


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
sudo systemctl disable --now httpd
sudo firewall-cmd --permanent --remove-service=http
sudo firewall-cmd --permanent --remove-port=8080/tcp
sudo firewall-cmd --reload
sudo semanage port -d -t http_port_t -p tcp 8080 2>/dev/null || true
sudo semanage fcontext -d "/srv/webroot(/.*)?" 2>/dev/null || true
sudo rm -rf /srv/webroot
sudo rm -f /etc/httpd/conf.d/custom.conf
sudo systemctl daemon-reload
```

---

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| httpd won't start | Port 8080 not in SELinux policy | `semanage port -a -t http_port_t -p tcp 8080` |
| Still 403 after restorecon | semanage fcontext not applied first | Delete fcontext entry, re-run semanage then restorecon |
| AVC denials still showing | Cached denials in audit log | Wait 60 seconds or check timestamps — only look at denials after your fix |
| `semanage: command not found` | Package missing | `sudo dnf install -y policycoreutils-python-utils` |

---

## Why this matters in production

SELinux label problems are the single most common SELinux issue admins
encounter. Whenever content is placed in a non-default path (custom app dirs,
mounted volumes, symlinks), the context must be explicitly defined. The correct
workflow is always: `semanage fcontext -a` → `restorecon -Rv` — never
`setenforce 0`.

---

## Next step

→ [RHCE: Automation Mindset](../../04-rhce/01-automation-mindset.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
