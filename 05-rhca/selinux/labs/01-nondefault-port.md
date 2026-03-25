
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab: Non-Default Port — Correct SELinux Fix
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCA
**Estimated time:** 40 minutes
**Topology:** Single VM

---
<a name="toc"></a>

## Table of contents

- [Background](#background)
- [Prerequisites](#prerequisites)
- [Success criteria](#success-criteria)
- [Steps](#steps)
  - [1 — Configure httpd to listen on port 9090](#1-configure-httpd-to-listen-on-port-9090)
  - [2 — Try to start httpd (expect failure)](#2-try-to-start-httpd-expect-failure)
  - [3 — Read the audit log](#3-read-the-audit-log)
  - [4 — Confirm with audit2why](#4-confirm-with-audit2why)
  - [5 — Apply the correct fix](#5-apply-the-correct-fix)
  - [6 — Open port 9090 in firewalld](#6-open-port-9090-in-firewalld)
  - [7 — Start httpd and verify](#7-start-httpd-and-verify)
  - [8 — Confirm with ss](#8-confirm-with-ss)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)
- [Cleanup](#cleanup)


## Background

Non-standard port bindings are one of the most common SELinux issues
encountered when deploying or migrating services on RHEL. When a service
binds a port that SELinux has not labelled for that service's domain, the
kernel denies the `name_bind` operation before the network stack even sees
the request. The result — a service that fails to start with no obvious
error message in the application logs — is a classic RHCA-level diagnostic
challenge.

This lab exercises the complete SELinux port fix workflow: observe the
failure, read the AVC denial, understand what `audit2why` is telling you,
and apply the targeted fix using `semanage port`. The anti-pattern — setting
`setenforce 0` or disabling the firewall — is explicitly excluded from the
success criteria to build the correct reflex.

This scenario applies directly to production situations: microservices on
non-standard ports, legacy applications migrated to RHEL, or internal
tooling that was written before SELinux port policy was a consideration.
Every RHCA-level engineer should be able to resolve this class of problem
in under 10 minutes.

---

## Prerequisites

- Completed [Fix Taxonomy](../01-fix-taxonomy.md), [semanage](../02-semanage.md), and [Audit Workflow](../03-audit-workflow.md)
- httpd installed: `sudo dnf install -y httpd`
- SELinux tools: `sudo dnf install -y policycoreutils-python-utils`
- VM snapshot taken


[↑ Back to TOC](#toc)

## Success criteria

- httpd serves content on port 9090
- The fix uses `semanage port` (not `setenforce 0`, not disabling firewalld)
- AVC denials are visible before the fix and absent after
- firewalld is correctly configured for port 9090

---


[↑ Back to TOC](#toc)

## Steps

### 1 — Configure httpd to listen on port 9090

```bash
sudo vim /etc/httpd/conf/httpd.conf
```

Find the `Listen 80` line and change it to:

```text
Listen 9090
```

> **Hint:** The `Listen` directive is near the top of the file. Use `/Listen`
> in vim to jump directly to it.

### 2 — Try to start httpd (expect failure)

```bash
sudo systemctl restart httpd
sudo systemctl status httpd
```

Expected: httpd fails to start.

```bash
journalctl -u httpd -n 20
```

Note: The journal may show a generic "Failed to start" without a specific
error about SELinux. This is normal — the AVC denial is in the audit log,
not the service journal.

> **Hint:** If you see `(13)Permission denied: AH00072: make_sock: could not
> bind to address` in the journal, that confirms the bind is being blocked.
> The audit log will show the SELinux denial causing it.

### 3 — Read the audit log

```bash
sudo ausearch -m avc -ts recent
```

You should see a denial like:

```text
denied { name_bind } for pid=... comm="httpd" src=9090
scontext=system_u:system_r:httpd_t:s0
tcontext=system_u:object_r:unreserved_port_t:s0
```

The key: `name_bind` denied, port 9090, context `unreserved_port_t`.
httpd is allowed to bind `http_port_t` ports — but 9090 is `unreserved_port_t`.

> **Hint:** If `ausearch -m avc -ts recent` returns nothing, try
> `ausearch -m avc -ts boot` — the denial may have been logged earlier in
> the session. Also verify `auditd` is running:
> `sudo systemctl status auditd`.

### 4 — Confirm with audit2why

```bash
sudo ausearch -m avc -ts recent | sudo audit2why
```

Look for: "SELinux is preventing httpd from name_bind access on the tcp_socket port 9090."

It should suggest a boolean (`httpd_can_network_relabelfrom`) or a `semanage port` fix.
The correct fix is `semanage port`.

> **Hint:** `audit2why` output includes the exact `semanage port` command
> with placeholder `PORT_TYPE`. Choose `http_port_t` as the type since
> httpd is an HTTP server.

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

> **Hint:** If `semanage port -a` returns "ValueError: Port tcp/9090 already
> defined", the port already has a label. Use `semanage port -m` instead of
> `-a` to modify the existing entry.

### 6 — Open port 9090 in firewalld

```bash
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --reload
```

> **Hint:** `--permanent` writes the rule to disk. `--reload` activates it.
> Without `--reload`, the permanent rule is not yet active in the running
> configuration. Verify with `sudo firewall-cmd --list-ports`.

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

> **Hint:** If httpd starts but `curl` returns "Connection refused", the
> SELinux fix is correct but the firewall rule may not have taken effect.
> Run `sudo firewall-cmd --list-ports` to confirm 9090/tcp appears.

### 8 — Confirm with ss

```bash
ss -tlnp | grep :9090
```

Look for: httpd/httpd worker listening on `:9090`.


[↑ Back to TOC](#toc)

---

## Troubleshooting guide

**httpd fails to start even after `semanage port -a`**

Check: Did you actually restart httpd *after* applying the semanage fix?
`semanage port` takes effect immediately, but the service must retry the
bind operation.
```bash
sudo systemctl restart httpd
```

**`ausearch -m avc -ts recent` returns nothing**

Check: Is `auditd` running?
```bash
sudo systemctl status auditd
sudo systemctl start auditd   # if stopped
```
Then re-trigger the failure: `sudo systemctl restart httpd`.
Then re-run: `sudo ausearch -m avc -ts recent`.

**`semanage port -a` fails with "already defined"**

The port has an existing SELinux label (possibly `unreserved_port_t` set
explicitly, or another type). Use `-m` to modify:
```bash
sudo semanage port -m -t http_port_t -p tcp 9090
```

**curl returns "Connection refused" after httpd starts**

httpd is listening but something is blocking the connection.
Step 1: Confirm httpd is actually listening:
```bash
ss -tlnp | grep :9090
```
Step 2: Confirm firewalld allows the port:
```bash
sudo firewall-cmd --list-ports
# Should show: 9090/tcp
```
Step 3: Confirm no new AVC denials:
```bash
sudo ausearch -m avc -ts recent
```

**curl returns 403 Forbidden**

This is expected if `/var/www/html/` is empty — httpd is running correctly.
403 means httpd received the request and processed it; the web root has no
`index.html`. This is a success condition for this lab.

**`semanage` command not found**

```bash
sudo dnf install -y policycoreutils-python-utils
```

**AVC denial shows `comm="systemd"` instead of `comm="httpd"`**

systemd itself may be generating a denial when trying to manage the httpd
socket. Check the `scontext` field — if it shows `init_t` or `systemd_t`,
this is a secondary denial. Focus on the `httpd_t` denial first.

**httpd journal shows no SELinux-specific error**

httpd reports a generic bind failure. The SELinux denial is always in
`/var/log/audit/audit.log`, not the systemd journal. Always use `ausearch`
for SELinux diagnosis, not `journalctl`.

**Port 9090 conflicts with Cockpit (if installed)**

Cockpit uses port 9090 by default. If Cockpit is installed and running,
httpd cannot bind 9090 regardless of SELinux settings.
Check: `ss -tlnp | grep :9090` before starting the lab.
Alternative: Use port 9091 for this lab.


[↑ Back to TOC](#toc)

---

## Extension tasks

**Extension 1 — SSH on a non-standard port**

Reconfigure `sshd` to listen on port 2222 instead of 22. Apply the correct
SELinux port label (`ssh_port_t`), update firewalld, and verify you can SSH
to port 2222. Then revert to port 22.

Expected commands:
```bash
sudo semanage port -a -t ssh_port_t -p tcp 2222
sudo firewall-cmd --permanent --add-port=2222/tcp
sudo firewall-cmd --reload
# Edit /etc/ssh/sshd_config: Port 2222
sudo systemctl restart sshd
ssh -p 2222 user@localhost
```

**Extension 2 — Multiple services on non-default ports**

Deploy two instances of a simple HTTP service using template units:
- Instance A on port 8081
- Instance B on port 8082

Apply the correct `semanage port` label for both ports. Verify both services
start and respond. Use `semanage port -l -C` to confirm only your custom
entries are shown.

> **Hint:** Port 8080 is already labelled as `http_port_t` in the default
> policy. Ports 8081 and 8082 are `unreserved_port_t` — they need `semanage
> port -a`.

**Extension 3 — Verify using per-domain permissive mode**

Instead of using `semanage port` to fix the lab scenario, use per-domain
permissive mode to confirm the denial, then apply the real fix:

```bash
# Set httpd_t to permissive (rest of system stays enforcing)
sudo semanage permissive -a httpd_t

# Start httpd — it should now start despite the unlabelled port
sudo systemctl start httpd

# Verify httpd is running despite the denial
sudo ausearch -m avc -ts recent
# Shows permissive=1 denials — would be denied in enforcing mode

# Now apply the real fix
sudo semanage port -a -t http_port_t -p tcp 9090

# Remove the per-domain permissive entry
sudo semanage permissive -d httpd_t

# Restart and confirm httpd still runs (now with the real fix)
sudo systemctl restart httpd
```

This extension demonstrates the per-domain permissive pattern — safer than
`setenforce 0` because only `httpd_t` is relaxed during testing.


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

## Why this matters in production

Microservices, custom applications, and legacy software commonly run on
non-standard ports. The correct RHEL workflow is always: identify the port's
SELinux type requirement → `semanage port -a` → `firewall-cmd --permanent`.
Skipping either step creates either a security gap or a broken service.

---


[↑ Back to TOC](#toc)

## Next step

→ [RHCA Containers: Podman Fundamentals](../../containers/01-podman-fundamentals.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
