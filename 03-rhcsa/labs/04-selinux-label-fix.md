
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab: Fix a SELinux Label Issue
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCSA
**Estimated time:** 30 minutes
**Topology:** Single VM

---
<a name="toc"></a>

## Table of contents

- [Background](#background)
- [Steps](#steps)
  - [1 — Start httpd and confirm SELinux is enforcing](#1-start-httpd-and-confirm-selinux-is-enforcing)
  - [2 — Create content in the standard location (should work)](#2-create-content-in-the-standard-location-should-work)
  - [3 — Create a custom web root with wrong context](#3-create-a-custom-web-root-with-wrong-context)
  - [4 — Configure httpd to serve from the custom path](#4-configure-httpd-to-serve-from-the-custom-path)
  - [5 — Test — observe the failure](#5-test-observe-the-failure)
  - [6 — Apply the correct SELinux fix](#6-apply-the-correct-selinux-fix)
  - [7 — Test again — confirm fix works](#7-test-again-confirm-fix-works)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)


## Prerequisites

- Completed [SELinux Fundamentals](../13-selinux-fundamentals.md) and [SELinux Troubleshooting](../14-selinux-avc-basics.md)
- httpd installed: `sudo dnf install -y httpd`
- SELinux tools: `sudo dnf install -y policycoreutils-python-utils`
- VM snapshot taken

---


[↑ Back to TOC](#toc)

## Background

SELinux label mismatches are the single most common SELinux problem in
production. The scenario is always the same: content placed in a non-default
path inherits the context of that path rather than the context required by
the service that will access it. The service fails with a 403 or permission
error, the admin suspects a Unix permission problem, `chmod 777` makes no
difference, and frustration sets in.

The correct mental model: SELinux contexts are not inherited from the parent
directory at access time — they are assigned at file creation time based on
the file context policy database. A file created in `/srv/` gets `srv_t` or
a related context, not `httpd_sys_content_t`. The policy database (managed by
`semanage fcontext`) is what tells `restorecon` what the correct context
should be for any given path. If the path is not in the database, `restorecon`
has no information and leaves the context unchanged.

This pattern — non-standard path, wrong inherited context, service denial —
appears routinely in real deployments. Application teams deploy to `/opt/`,
`/srv/`, `/data/`, or custom paths. Every time, the SELinux context must be
explicitly configured. The correct two-step workflow is: `semanage fcontext -a`
to register the path in the policy database, then `restorecon -Rv` to apply
the registered context to existing files. Any other approach (chcon, setenforce 0)
is either temporary or wrong.

### Why chcon is not enough

Many guides show `chcon -R -t httpd_sys_content_t /srv/webroot/` as a fix.
This works until the next filesystem relabel. A relabel (`restorecon -R /` or
`touch /.autorelabel` on boot) resets every file to the context the policy
database says it should have. If the database has no entry for `/srv/webroot/`,
it reverts to a generic type. The `semanage fcontext` → `restorecon` workflow
persists through relabels because the policy database is updated.

---


[↑ Back to TOC](#toc)

## Success criteria

- httpd serves content from `/var/www/html/` correctly
- httpd serves content from a custom path `/srv/webroot/` after correct SELinux fix
- The fix uses `semanage fcontext` + `restorecon` (not `setenforce 0`, not `chmod 777`)
- AVC denials are visible in audit log before the fix and absent after

---


[↑ Back to TOC](#toc)

## Steps

### 1 — Start httpd and confirm SELinux is enforcing

```bash
sudo systemctl enable --now httpd
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
getenforce
```

Expected: `Enforcing`

> **Hint:** If `getenforce` returns `Permissive` or `Disabled`, this lab
> will not work as designed — you will not see the 403 failure in step 5.
> Set to enforcing with `sudo setenforce 1` if needed. Ensure
> `/etc/selinux/config` has `SELINUX=enforcing` to survive a reboot.


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

> **Hint:** The standard `/var/www/html/` path is already in the SELinux
> policy database. Any file created or copied here automatically gets the
> correct `httpd_sys_content_t` context — that is why this step works without
> any SELinux configuration. The custom path in step 3 is not in the database.


[↑ Back to TOC](#toc)

---

### 3 — Create a custom web root with wrong context

```bash
sudo mkdir -p /srv/webroot
echo "<h1>Custom location</h1>" | sudo tee /srv/webroot/index.html
ls -Z /srv/webroot/index.html
```

Note the context — it will be something like `default_t` or `var_t`, **not** `httpd_sys_content_t`.

> **Hint:** The exact context will depend on what `/srv/` maps to in the
> SELinux policy on your system. Run `ls -Z /srv/` to see the directory
> context and note that the file inherits it. This is the wrong context
> for httpd to access.


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

> **Hint:** The `semanage port` step is necessary because httpd by default
> is only allowed to bind to standard HTTP ports (80, 443, 8443, etc.).
> Port 8080 must be explicitly added to the `http_port_t` SELinux port type
> or httpd will fail to start with an `AVC name_bind denied` error.


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

> **Hint:** Read the AVC carefully. The key fields are:
> - `comm="httpd"` — which process was denied
> - `name="index.html"` — which file was accessed
> - `tcontext=...var_t...` (or similar) — the current wrong context on the file
>
> The fix is to change `tcontext` to `httpd_sys_content_t`. The path
> `/srv/webroot` is what needs the `semanage fcontext` entry.


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

> **Hint:** The regex `/srv/webroot(/.*)?` matches the directory itself AND
> all files and subdirectories within it. Without the `(/.*)?` suffix, only
> the `/srv/webroot` directory gets the new context — not the files inside.
> Always use this regex pattern when applying a context to a directory tree.


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

> **Hint:** If the 403 persists after fixing the context, check whether
> there is also a standard Unix permission problem. `ls -l /srv/webroot/`
> should show the files as world-readable (644) or at least readable by
> the `apache` user. SELinux and DAC are independent checks — both must pass.


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


[↑ Back to TOC](#toc)

## Troubleshooting guide

| Symptom | Likely cause | Fix |
|---|---|---|
| httpd won't start | Port 8080 not in SELinux port policy | `semanage port -a -t http_port_t -p tcp 8080` |
| Still 403 after restorecon | `semanage fcontext` not run first | Delete entry, re-run `semanage fcontext -a`, then `restorecon` |
| AVC denials still showing | Looking at old denials (before fix timestamp) | Use `ausearch -m avc -ts <time-after-fix>` to filter to only new denials |
| `semanage: command not found` | Package missing | `sudo dnf install -y policycoreutils-python-utils` |
| `restorecon` changes context but `ls -Z` still shows wrong type | Ran `restorecon` before `semanage fcontext` | Re-run `semanage fcontext -a -t httpd_sys_content_t "/srv/webroot(/.*)?"` then `restorecon -Rv /srv/webroot/` |
| 403 persists despite correct SELinux context | Unix permission problem (DAC) | `ls -l /srv/webroot/` — ensure files are world-readable or readable by `apache` |
| httpd shows AVC for directory, not file | Directory itself has wrong context | `ls -Z /srv/webroot/` — apply `semanage` and `restorecon` to the directory too |
| `curl` returns `connection refused` instead of 403 | httpd not listening on 8080 | Check `systemctl status httpd` and `ss -tlnp | grep 8080` |

---


[↑ Back to TOC](#toc)

## Why this matters in production

SELinux label problems are the single most common SELinux issue admins
encounter. Whenever content is placed in a non-default path (custom app dirs,
mounted volumes, symlinks), the context must be explicitly defined. The correct
workflow is always: `semanage fcontext -a` → `restorecon -Rv` — never
`setenforce 0`.

### Production deployment checklist for new application paths

When deploying an application to a non-standard path, work through this
checklist before starting the service:

```bash
# 1. Identify which service will access the files
# (e.g., httpd, nginx, named, vsftpd)

# 2. Find the correct SELinux type for that service's content
sudo semanage fcontext -l | grep httpd_sys_content_t | head -5
# Note the pattern used for standard paths like /var/www/html

# 3. Register your custom path
sudo semanage fcontext -a -t httpd_sys_content_t "/opt/myapp(/.*)?"

# 4. Apply the context
sudo restorecon -Rv /opt/myapp/

# 5. Verify
ls -Z /opt/myapp/
# Expected: httpd_sys_content_t on files

# 6. Check for boolean requirements
sudo getsebool -a | grep httpd
# If the service needs to connect to a database: httpd_can_network_connect_db

# 7. Check for port registration (if non-standard port)
sudo semanage port -l | grep http_port_t

# 8. Start service and check for AVCs
sudo systemctl start httpd
sudo ausearch -m avc -ts recent
```

Steps 3 and 4 (`semanage fcontext` + `restorecon`) must always be done in
that order. Reversing them — running `restorecon` before `semanage fcontext`
— has no effect because `restorecon` cannot apply a context that is not yet
in the database.

### SELinux context types for common services

Knowing the correct type for each service avoids having to guess or search:

| Service | Content type | Executable type | Port type |
|---|---|---|---|
| httpd / nginx | `httpd_sys_content_t` | `httpd_exec_t` | `http_port_t` |
| sshd | `sshd_key_t` (keys) | `sshd_exec_t` | `ssh_port_t` |
| vsftpd | `public_content_t` / `public_content_rw_t` | `ftpd_exec_t` | `ftp_port_t` |
| named (DNS) | `named_zone_t` | `named_exec_t` | `dns_port_t` |
| postfix / smtp | `mail_spool_t` | `postfix_exec_t` | `smtp_port_t` |
| postgresql | `postgresql_db_t` | `postgresql_exec_t` | `postgresql_port_t` |
| samba | `samba_share_t` | `smbd_exec_t` | `smb_port_t` |

When unsure of the correct type for a service, query the existing policy for
standard paths:

```bash
# See what context is used for standard httpd content paths
sudo semanage fcontext -l | grep '/var/www'
# Output shows: /var/www(/.*)? all files  system_u:object_r:httpd_sys_content_t:s0
```

### Common exam mistakes on SELinux tasks

| Mistake | Consequence | Prevention |
|---|---|---|
| Running `restorecon` before `semanage fcontext` | Context not changed; 403 persists | Always register with `semanage` first |
| Using `chcon` instead of `semanage` + `restorecon` | Survives until relabel, then reverts | Only `semanage` + `restorecon` is persistent |
| Using `setenforce 0` to "fix" the issue | Security completely disabled; hides root cause | Never disable SELinux to work around a label problem |
| Forgetting `(/.*)?` regex suffix in `semanage fcontext` | Only directory context updated; files inside keep wrong context | Always use `"/path(/.*)?"` to cover the full tree |
| Applying `semanage fcontext` to wrong path | Target files keep wrong context | Double-check the path matches where files actually are |
| Not checking for DAC issues after fixing SELinux | 403 persists because Unix permissions also deny access | After SELinux fix, check `ls -l` too |
| Missing port registration for non-standard ports | httpd refuses to bind, fails to start | `semanage port -a -t http_port_t -p tcp <port>` |

### Quick SELinux diagnosis workflow

When a service fails and SELinux may be involved:

```bash
# 1. Is SELinux enforcing?
getenforce

# 2. Are there recent AVC denials?
sudo ausearch -m avc -ts recent | tail -20

# 3. What context does the file have vs. what should it have?
ls -Z /path/to/file
sudo semanage fcontext -l | grep '/path/to'

# 4. Are there boolean requirements?
sudo getsebool -a | grep <service>

# 5. Quick sealert summary
sudo sealert -a /var/log/audit/audit.log 2>/dev/null | grep -A5 "SELinux is preventing"
```

### Booleans: when to use them

SELinux booleans toggle predefined policy behaviours without writing custom
policy. Use booleans when the service needs a capability, not just access to
a specific path:

```bash
# List all booleans with current state and description
sudo semanage boolean -l

# Common httpd booleans
sudo getsebool -a | grep httpd
```

| Boolean | Effect |
|---|---|
| `httpd_can_network_connect` | Allow httpd to make outbound TCP connections |
| `httpd_can_network_connect_db` | Allow httpd to connect to database ports |
| `httpd_can_sendmail` | Allow httpd to send email |
| `httpd_enable_homedirs` | Allow httpd to read user home directories |
| `httpd_use_nfs` | Allow httpd to read NFS-mounted content |
| `httpd_execmem` | Allow httpd to execute memory (needed by some PHP extensions) |

Set a boolean persistently (survives reboot):

```bash
sudo setsebool -P httpd_can_network_connect on
# -P writes to policy database; without -P change is lost on reboot
```

Booleans are coarser than `semanage fcontext`: a boolean affects all paths
accessible via that policy rule, not just one directory. For a specific
non-standard document root, `semanage fcontext` is the right tool because it
grants only what is needed.

---


[↑ Back to TOC](#toc)

## Extension tasks

**Extension 1 — Diagnose with sealert**

Instead of reading the AVC directly from `ausearch`, use `sealert` to analyse
the same denial. Compare the output. Confirm that `sealert` recommends the
same `semanage fcontext` fix. Note the confidence percentage it assigns.

```bash
sudo sealert -a /var/log/audit/audit.log
# Read the suggested fix section
# Compare to what you applied manually
```

**Extension 2 — Fix using a boolean instead of fcontext**

Research whether a boolean exists that would allow httpd to access content
in `/srv/`. Test it. Understand why `semanage fcontext` is generally
preferable to a permissive boolean — it grants the minimum necessary access.

```bash
sudo getsebool -a | grep httpd
# Look for relevant booleans

# Try: httpd_read_user_content or similar
sudo setsebool httpd_read_user_content on
curl http://localhost:8080/

# Compare: which approach is more targeted?
# semanage fcontext applies only to that path
# A broad boolean may allow access to many other paths too
sudo setsebool httpd_read_user_content off   # revert
```

**Extension 3 — Persist context across file replacements**

Deploy an application update by deleting and recreating files in
`/srv/webroot/`. Verify the context is correctly applied to the new files
(it should be, because the directory is now in the policy database). Then
try using `mv` from a home directory file and observe that the context
reverts to the source context — and that `restorecon` fixes it.

```bash
# Simulate update: replace index.html
sudo rm /srv/webroot/index.html
echo "<h1>Version 2</h1>" | sudo tee /srv/webroot/index.html
ls -Z /srv/webroot/index.html   # should still be httpd_sys_content_t (created in-place)

# Simulate mv from home dir
echo "<h1>Moved in</h1>" > ~/moved.html
sudo mv ~/moved.html /srv/webroot/index.html
ls -Z /srv/webroot/index.html   # context reverted to user_home_t
curl http://localhost:8080/     # 403 again

sudo restorecon -v /srv/webroot/index.html   # fix
curl http://localhost:8080/     # 200 OK
```

---


[↑ Back to TOC](#toc)

## Next step

→ [RHCE: Automation Mindset](../../04-rhce/01-automation-mindset.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
