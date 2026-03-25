
[↑ Back to TOC](#toc)

# SELinux Troubleshooting — AVCs
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

An **AVC (Access Vector Cache) denial** is what SELinux logs when it blocks
an action. Learning to read and correctly respond to AVCs is the key skill.

The AVC is a kernel-level cache that stores recent access-control decisions.
When a process tries to access a resource, the kernel checks the AVC first.
If no cached decision exists, it queries the SELinux policy engine, caches
the result, and proceeds. A denial is logged to the audit subsystem as an
`AVC` record in `/var/log/audit/audit.log`. These log entries are dense but
highly structured — every field has a specific meaning.

The most important skill is not memorising syntax but understanding the
**diagnostic workflow**: read the AVC, identify the source and target types,
determine whether the fix is a label, a boolean, a port policy, or (rarely)
a custom policy module. Reaching for `setenforce 0` or `audit2allow` as a
first response is always wrong — these hide the problem rather than solving it.

Developing fluency with `ausearch`, `audit2why`, and `sealert` transforms
SELinux from an obstacle into a transparent security layer. Once you can read
an AVC and know which of the four fix types applies, you can resolve almost
any SELinux issue in under five minutes.

---
<a name="toc"></a>

## Table of contents

- [Where AVC denials are logged](#where-avc-denials-are-logged)
- [Reading an AVC denial](#reading-an-avc-denial)
- [`audit2why` — plain-language explanation](#audit2why-plain-language-explanation)
- [`sealert` — richer analysis](#sealert-richer-analysis)
- [The fix taxonomy (choose the right fix)](#the-fix-taxonomy-choose-the-right-fix)
- [Common AVC scenarios and fixes](#common-avc-scenarios-and-fixes)
  - [Web content in wrong location](#web-content-in-wrong-location)
  - [Service on non-default port](#service-on-non-default-port)
- [Confirm SELinux mode before assuming it's a permission problem](#confirm-selinux-mode-before-assuming-its-a-permission-problem)
- [Quick AVC search with `ausearch`](#quick-avc-search-with-ausearch)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)
- [Permissive domains](#permissive-domains)
- [AVC denial patterns quick reference](#avc-denial-patterns-quick-reference)


## Where AVC denials are logged

```bash
# Primary audit log
sudo tail -f /var/log/audit/audit.log | grep AVC

# Journal (syslog copy)
sudo journalctl -f | grep avc
```

The audit daemon (`auditd`) must be running for AVC records to appear in
`/var/log/audit/audit.log`. On RHEL 10, `auditd` is enabled by default.
If it is not running, AVCs still appear in the kernel ring buffer and the
journal, but `ausearch` and `audit2why` cannot process them as effectively.

```bash
# Confirm auditd is running
systemctl status auditd
```


[↑ Back to TOC](#toc)

---

## Reading an AVC denial

Example AVC from `/var/log/audit/audit.log`:

```text
type=AVC msg=audit(1708692000.123:456): avc:  denied  { read } for
pid=1234 comm="httpd" name="index.html"
scontext=system_u:system_r:httpd_t:s0
tcontext=user_u:object_r:user_home_t:s0
tclass=file permissive=0
```

| Field | Meaning |
|---|---|
| `denied { read }` | httpd tried to **read** a file and was blocked |
| `comm="httpd"` | The process was httpd |
| `name="index.html"` | The target file |
| `scontext=...httpd_t...` | Source context (httpd process) |
| `tcontext=...user_home_t...` | Target context (file has wrong type) |
| `tclass=file` | The object class being accessed |

**The fix here:** the file has `user_home_t` context but httpd needs
`httpd_sys_content_t`. Fix = `restorecon`, not `chmod 777`.

Common `tclass` values and what they represent:

| tclass | Object type |
|---|---|
| `file` | Regular file |
| `dir` | Directory |
| `tcp_socket` | TCP socket |
| `udp_socket` | UDP socket |
| `process` | Process (signals, ptrace) |
| `unix_stream_socket` | Unix domain socket |

The `{ }` block (called the **permission vector**) shows what operation was
denied. Common permissions: `read`, `write`, `open`, `execute`, `getattr`,
`name_bind` (binding to a port), `name_connect` (connecting to a port).


[↑ Back to TOC](#toc)

---

## `audit2why` — plain-language explanation

```bash
sudo audit2why < /var/log/audit/audit.log
```

This reads the audit log and explains each denial in plain language,
including a suggested fix.

> **⚠️ audit2why is a diagnostic tool, not a fix generator**
> audit2why may suggest generating a custom policy module with `audit2allow`.
> Only do this as a last resort after ruling out a label fix, boolean, or
> port fix. Custom modules can silently permit unintended access.
>

To process only recent denials:

```bash
sudo ausearch -m avc -ts recent | audit2why
```

`audit2why` output typically includes one of these explanations:
- `Missing type enforcement (TE) allow rule` — needs a context fix or boolean
- `SELinux policy for httpd does not allow ...` — a boolean may cover this
- `Allow this access by ...` — suggests `setsebool` or `semanage fcontext`


[↑ Back to TOC](#toc)

---

## `sealert` — richer analysis

```bash
# Analyse the audit log
sudo sealert -a /var/log/audit/audit.log

# If setroubleshootd is running, check its log
sudo journalctl -u setroubleshootd
```

`sealert` provides:
- A human-readable description of the denial
- Probability-ranked suggested fixes
- The correct `semanage` or `setsebool` command to run

`sealert` output is verbose. Each alert includes a `confidence` score for
each suggested fix — higher confidence means `sealert` is more certain that
fix applies. Always read the description and the suggested commands before
blindly running them. The highest-confidence suggestion is usually correct for
common scenarios.

```bash
# Targeted: only show denials from the last hour
sudo ausearch -m avc -ts recent | sudo sealert -a /dev/stdin
```


[↑ Back to TOC](#toc)

---

## The fix taxonomy (choose the right fix)

When you see an AVC, work through this order:

```text
1. Wrong file label?  → restorecon -Rv <path>
2. Non-default path?  → semanage fcontext + restorecon
3. Boolean covers it? → setsebool -P <boolean> on
4. Non-default port?  → semanage port -a -t <type> -p tcp <port>
5. None of the above? → audit2allow (last resort, with caution)
```

This taxonomy is enough to solve the vast majority of day-to-day AVC denials.
When you reach the RHCA track, the [SELinux Deep Dive](../05-rhca/selinux/01-fix-taxonomy.md)
chapter expands each fix type with edge cases and `semanage` details — but you
don't need it yet.

**Choosing the right fix quickly:**

- If `tcontext` shows a type that doesn't match the directory (e.g., file in
  `/var/www/html/` has `user_home_t`): it's a label problem — use `restorecon`.
- If the path is non-standard (e.g., `/opt/`, `/srv/`): add a `semanage fcontext`
  rule then `restorecon`.
- If the denial involves a network operation (`name_connect`, `name_bind`):
  check booleans first, then `semanage port`.
- If you see `name_bind denied` for a custom port: use `semanage port -a`.

> **Exam tip:** The fix taxonomy above — label → semanage fcontext → boolean →
> port — covers the vast majority of RHCSA exam SELinux questions. Work through
> it in order rather than jumping to `audit2allow`.


[↑ Back to TOC](#toc)

---

## Common AVC scenarios and fixes

### Web content in wrong location

**Symptom:** httpd returns 403, audit log shows `denied { read }` for your content file.

```bash
ls -Z /var/www/html/        # should show httpd_sys_content_t
ls -Z /home/rhel/myapp/     # shows user_home_t — wrong location for web content
```

**Fix — option A:** move content to `/var/www/html/` (preferred):

```bash
sudo cp -r /home/rhel/myapp/* /var/www/html/
sudo restorecon -Rv /var/www/html/
```

**Fix — option B:** if the path must stay non-standard, use `semanage`:

```bash
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/myapp(/.*)?"
sudo restorecon -Rv /srv/myapp/
```

After applying either fix, verify:

```bash
ls -Z /srv/myapp/   # should now show httpd_sys_content_t
curl http://localhost/   # should return 200
```

### Service on non-default port

**Symptom:** httpd fails to start on port 8080, AVC shows `name_bind denied`.

```bash
sudo semanage port -l | grep http
# Add the port
sudo semanage port -a -t http_port_t -p tcp 8080
# Restart service
sudo systemctl restart httpd
```

To list all ports currently defined in the policy:

```bash
sudo semanage port -l
```

If the port is already assigned to a different type (e.g., `unreserved_port_t`),
use `-m` (modify) instead of `-a` (add):

```bash
sudo semanage port -m -t http_port_t -p tcp 8080
```


[↑ Back to TOC](#toc)

---

## Confirm SELinux mode before assuming it's a permission problem

Many admins blame SELinux when the actual problem is a missing firewall rule
or a standard Unix permission. Always check in this order:

1. `systemctl status <service>` — is it even running?
2. Standard file permissions (`ls -l`)
3. SELinux context (`ls -Z`)
4. AVC in audit log (`sudo ausearch -m avc -ts recent`)
5. Firewall (`sudo firewall-cmd --list-all`)

This order matters: a standard permission error (step 2) produces a different
symptom than an SELinux denial (step 4). A 403 from Apache can mean either —
check `ls -l` and `ls -Z` before running `ausearch`.


[↑ Back to TOC](#toc)

---

## Quick AVC search with `ausearch`

```bash
# Recent AVC denials
sudo ausearch -m avc -ts recent

# Today's AVCs
sudo ausearch -m avc -ts today

# AVCs for a specific process
sudo ausearch -m avc -c httpd

# AVCs for a specific file
sudo ausearch -m avc -ts today | grep index.html

# Pipe to audit2why for explanation
sudo ausearch -m avc -ts recent | audit2why
```

`-ts recent` means "in the last 10 minutes". `-ts today` means since midnight.
You can also use `-ts <HH:MM:SS>` for a specific time, or `-ts boot` for since
last boot.


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** An admin places a PHP application in `/var/www/myapp/` (not the
standard `/var/www/html/`). Apache is configured to serve from that path.
The site returns 403.

```bash
# Step 1 — confirm the service is running
systemctl status httpd
# Active: active (running) — service is up

# Step 2 — check standard permissions
ls -l /var/www/myapp/
# -rw-r--r--. 1 apache apache 1234 index.php — permissions OK

# Step 3 — check SELinux context
ls -Z /var/www/myapp/
# system_u:object_r:httpd_sys_script_t:s0 index.php
# Hmm — "httpd_sys_script_t" allows execution but may restrict reads.
# Or it may be showing "var_t" if copied from elsewhere.

# Step 4 — check for AVC denials
sudo ausearch -m avc -ts recent
# type=AVC ... denied { read } for pid=... comm="httpd"
# scontext=...httpd_t... tcontext=...var_t...

# Step 5 — pipe to audit2why
sudo ausearch -m avc -ts recent | audit2why
# Was caused by: Missing type enforcement (TE) allow rule.
# Suggested fix: restorecon -Rv /var/www/myapp/ OR semanage fcontext ...

# Step 6 — try restorecon first (in case policy already covers this path)
sudo restorecon -Rv /var/www/myapp/
ls -Z /var/www/myapp/
# If context is now httpd_sys_content_t, done.

# Step 7 — if path not in policy, add it
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/myapp(/.*)?"
sudo restorecon -Rv /var/www/myapp/

# Step 8 — verify no more AVCs
sudo ausearch -m avc -ts recent
# No output — no denials

# Step 9 — test
curl http://localhost/myapp/
# Expected: 200 OK
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Symptom | Likely cause | Diagnosis | Fix |
|---|---|---|---|
| `restorecon` doesn't fix the context | Path not in the fcontext policy | `matchpathcon <path>` returns `<<none>>` | `semanage fcontext -a` first, then `restorecon` |
| AVC denial persists after fix | Fix applied to wrong path or policy not active | `ausearch -m avc -ts recent` still shows denials | Confirm path matches exactly; check context with `ls -Z` |
| `audit2allow` module applied but problem recurs | Module only covers one path/type combination | New files in path don't inherit the custom rule | Use `semanage fcontext` for a proper persistent fix |
| `sealert` shows no suggestions | `setroubleshoot-server` not installed | `rpm -q setroubleshoot-server` | `sudo dnf install setroubleshoot-server` |
| Boolean set but denial continues | Wrong boolean for this use case | `getsebool -a | grep <service>` — read all available booleans | Try `sealert` to identify the correct boolean |
| AVCs in log but service works | SELinux in permissive mode | `getenforce` returns `Permissive` | These are "would-be" denials — fix them before switching back to Enforcing |


[↑ Back to TOC](#toc)

---

## Permissive domains

Instead of setting the entire system to permissive mode, you can set a
single process domain to permissive. This lets you debug one service without
weakening the entire system's SELinux enforcement:

```bash
# Set httpd_t domain to permissive (for debugging)
sudo semanage permissive -a httpd_t

# Verify
sudo semanage permissive -l

# Remove permissive exception (restore enforcing for that domain)
sudo semanage permissive -d httpd_t
```

With a domain-level permissive setting, all other domains remain enforcing.
AVC denials for `httpd_t` are still logged (as `permissive=1` in the log),
so you can collect them and then apply the fixes before removing the
permissive exception.

This is the correct production-safe approach to debugging a specific service —
not `setenforce 0` which affects all domains.


[↑ Back to TOC](#toc)

---

## AVC denial patterns quick reference

A catalogue of common AVC patterns and their fixes:

### Pattern 1: Wrong file context (most common)

```text
avc: denied { read } for pid=... comm="httpd"
  scontext=...:httpd_t:s0
  tcontext=...:user_home_t:s0
  tclass=file
```

**Fix:** `semanage fcontext -a -t httpd_sys_content_t "<path>(/.*)?"`
then `restorecon -Rv <path>`

### Pattern 2: Service binding to non-default port

```text
avc: denied { name_bind } for pid=... comm="httpd"
  scontext=...:httpd_t:s0
  tcontext=...:unreserved_port_t:s0
  tclass=tcp_socket
```

**Fix:** `semanage port -a -t http_port_t -p tcp <port>`

### Pattern 3: Service connecting to non-default port

```text
avc: denied { name_connect } for pid=... comm="httpd"
  scontext=...:httpd_t:s0
  tcontext=...:mysqld_port_t:s0
  tclass=tcp_socket
```

**Fix:** Check for a boolean first (`httpd_can_network_connect_db`),
then `semanage port` if needed.

### Pattern 4: Boolean needed for network access

```text
avc: denied { name_connect } for pid=... comm="httpd"
  scontext=...:httpd_t:s0
  tcontext=...:http_port_t:s0
  tclass=tcp_socket
```

**Fix:** `setsebool -P httpd_can_network_connect on`

### Pattern 5: Process execution denied

```text
avc: denied { execute } for pid=... comm="httpd"
  scontext=...:httpd_t:s0
  tcontext=...:user_home_t:s0
  tclass=file
```

**Fix:** The file is in the wrong location for execution by this process.
Move it to a location with `httpd_sys_script_exec_t` context, or use
`semanage fcontext` to assign that type to the custom location.

### Pattern 6: Relabeling needed after `mv`

No AVC denial but the file has the wrong context because it was moved
with `mv` from a different location.

**Fix:** `sudo restorecon -v <file>` (if the path is in the policy database)
or `semanage fcontext -a -t <type> <path>` + `restorecon`.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`audit2allow` man page](https://man7.org/linux/man-pages/man1/audit2allow.1.html) | Generate policy modules from AVC denials |
| [`audit2why` man page](https://man7.org/linux/man-pages/man1/audit2why.1.html) | Explain why a denial occurred in human language |
| [`sealert` man page](https://linux.die.net/man/8/sealert) | SELinux alert browser — part of `setroubleshoot-server` |
| [RHEL 10 — Troubleshooting SELinux](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/using_selinux/troubleshooting-problems-related-to-selinux_using-selinux) | Official AVC troubleshooting workflows |

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab: Fix a SELinux Label Issue](labs/04-selinux-label-fix.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
