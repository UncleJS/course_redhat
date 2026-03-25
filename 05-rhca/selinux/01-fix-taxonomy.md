
[↑ Back to TOC](#toc)

# SELinux Fix Taxonomy — Label vs Boolean vs Port vs Policy
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

The most important SELinux skill is choosing the **correct type of fix** for
a given AVC denial. Applying the wrong fix either doesn't work or creates
a security hole.

At the RHCA level you are expected to diagnose the root cause of an AVC
denial and apply the minimally permissive fix — not the easiest one. The
taxonomy of fixes maps directly to the nature of the problem: a file in the
wrong place needs a label fix; an access pattern the policy designer
anticipated needs a boolean; a non-standard port needs a port label; and a
genuinely novel access need (rare, legitimate) may need a custom policy module.

The mental model: SELinux is a reference monitor. Every access decision is:
subject (process type) + action (read, write, name_bind, ...) + object (file
type, port type, ...). An AVC denial means one of three things — the object
has the wrong type (label fix), the policy was intentionally restricted but
has a switch (boolean fix), or the policy has no rule for this access at all
(port label or policy module). Identifying which case applies before touching
any configuration is the difference between a targeted fix and a policy that
drifts permissive over time.

Getting fix taxonomy wrong in production is a compounding security risk. A
misapplied `audit2allow` module that grants `httpd_t` read access to
`shadow_t` would pass through unnoticed if the engineer didn't review the
generated `.te` file. A `setenforce 0` "temporary" fix that becomes permanent
because the root cause was never addressed disables MAC for the entire host.
The taxonomy forces you to ask the right diagnostic question first.

---
<a name="toc"></a>

## Table of contents

- [The fix decision tree](#the-fix-decision-tree)
- [Fix type 1: File context (most common)](#fix-type-1-file-context-most-common)
- [Fix type 2: Boolean (targeted policy switch)](#fix-type-2-boolean-targeted-policy-switch)
- [Fix type 3: Port label](#fix-type-3-port-label)
- [Fix type 4: audit2allow (last resort)](#fix-type-4-audit2allow-last-resort)
- [Fix type 5: The application is wrong](#fix-type-5-the-application-is-wrong)
- [Worked example — new custom app needing port label and file context](#worked-example-new-custom-app-needing-port-label-and-file-context)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## The fix decision tree

```text
AVC denial observed
        │
        ▼
Is the file/dir in a non-standard location?
  Yes → semanage fcontext + restorecon
  No  → Is there a boolean that covers this use case?
          Yes → setsebool -P
          No  → Is it a non-default port binding?
                  Yes → semanage port
                  No  → Is this a legitimate access that policy doesn't cover?
                          Yes → audit2allow (last resort, with review)
                          No  → Fix the application, not the policy
```


[↑ Back to TOC](#toc)

---

## Fix type 1: File context (most common)

**When to use:** A file or directory has the wrong SELinux type label.
This happens when:
- Files are placed in a non-standard path
- Files are moved with `mv` (context follows source, not destination)
- Freshly created files in a custom directory

**Fix:**

```bash
# Add a persistent fcontext rule
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/myapp(/.*)?"

# Apply it (run every time files change)
sudo restorecon -Rv /srv/myapp/

# Verify
ls -Z /srv/myapp/
```

**View existing rules:**

```bash
sudo semanage fcontext -l | grep /srv
```

**Remove a rule:**

```bash
sudo semanage fcontext -d "/srv/myapp(/.*)?"
```

**Why `cp` preserves context but `mv` does not:**

`cp` creates a new file in the destination directory; the new file inherits
the destination directory's default context from the fcontext database.
`mv` renames the inode in place; the inode retains the source context
regardless of the destination path. Always run `restorecon` after `mv`.

> **Exam tip:** `semanage fcontext -a` adds a rule to the policy database.
> It does **not** change labels on existing files. Always follow with
> `restorecon -Rv <path>` to apply the rule to files on disk.


[↑ Back to TOC](#toc)

---

## Fix type 2: Boolean (targeted policy switch)

**When to use:** The access pattern is known and policy already has a
pre-built switch for it.

**Fix:**

```bash
# Find relevant boolean
sudo getsebool -a | grep httpd

# Enable (persistent)
sudo setsebool -P httpd_can_network_connect on

# Verify
getsebool httpd_can_network_connect
```

**Common booleans (RHEL infra focus):**

| Boolean | Enables |
|---|---|
| `httpd_can_network_connect` | Apache outbound network connections |
| `httpd_can_network_connect_db` | Apache to DB (MySQL/PostgreSQL) |
| `httpd_use_nfs` | Apache to serve NFS content |
| `httpd_use_cifs` | Apache to serve CIFS/SMB content |
| `httpd_enable_homedirs` | Apache to serve from user home dirs |
| `samba_enable_home_dirs` | Samba to share home directories |
| `container_use_devices` | Container to access devices |
| `virt_use_nfs` | Virtualization to use NFS |
| `ssh_use_tcpd` | SSH with TCP wrappers |

**How to discover the right boolean:**

```bash
# Option 1: audit2why — often suggests the boolean directly
sudo ausearch -m avc -ts recent | sudo audit2why

# Option 2: sealert — ranks potential fixes by probability
sudo sealert -a /var/log/audit/audit.log

# Option 3: search boolean descriptions
sudo semanage boolean -l | grep -i "<keyword>"
```

> **Exam tip:** When `audit2why` suggests toggling a boolean, verify
> the boolean name with `getsebool -a | grep <name>` before applying it.
> `setsebool -P` (with `-P`) persists the change across reboots.
> Without `-P`, the boolean resets after reboot.


[↑ Back to TOC](#toc)

---

## Fix type 3: Port label

**When to use:** A service needs to bind to a non-default port.

```bash
# Check what ports are allowed for http
sudo semanage port -l | grep http_port

# Add a new port
sudo semanage port -a -t http_port_t -p tcp 8080

# Modify an existing label
sudo semanage port -m -t http_port_t -p tcp 8080

# Remove
sudo semanage port -d -t http_port_t -p tcp 8080

# Verify
sudo semanage port -l | grep 8080
```

**Choosing between `-a` and `-m`:**

Use `-a` (add) when the port has no existing SELinux label or has
`unreserved_port_t`. Use `-m` (modify) when the port already has a
different label assigned by policy. If you use `-a` on a port that
already has a label, `semanage` returns an error — use `-m` instead.

```bash
# Check if port already has a label
sudo semanage port -l | grep " 8443 "
# If it shows a label → use -m; if not found → use -a
```


[↑ Back to TOC](#toc)

---

## Fix type 4: audit2allow (last resort)

`audit2allow` generates policy modules from audit logs. Use it **only** after
ruling out all other fix types, and **always review** what it generates.

```bash
# Step 1: isolate the specific denial you want to fix
sudo ausearch -m avc -c myapp -ts today > /tmp/myapp-avc.txt

# Step 2: understand what it will allow
sudo audit2allow -i /tmp/myapp-avc.txt

# Step 3: generate a type enforcement file
sudo audit2allow -i /tmp/myapp-avc.txt -M myapp-local

# Step 4: REVIEW myapp-local.te before loading
cat myapp-local.te

# Step 5: load the policy module
sudo semodule -i myapp-local.pp
```

> **⚠️ Review audit2allow output carefully**
> audit2allow generates the minimum policy to allow what was denied,
> but it has no context about whether the access is *intended*. A module
> that allows `httpd_t` to read `shadow_t` (password hashes) would be
> generated if httpd somehow triggered that denial — and it would be wrong.
>

**Reviewing a generated `.te` file:**

```text
# myapp-local.te
module myapp-local 1.0;

require {
    type myapp_t;
    type var_t;
    class file { read open getattr };
}

allow myapp_t var_t:file { read open getattr };
```

Ask: Does `myapp_t` legitimately need to read files of type `var_t`? `var_t`
is the generic type for `/var` — this is suspicious. Investigate why the
application is accessing `/var` without a more specific type. It may indicate
a missing `semanage fcontext` rule rather than a genuine policy gap.

> **Exam tip:** `audit2allow -M <name>` generates both a `.te` (source) and
> `.pp` (compiled policy package) file. Always `cat` the `.te` file before
> running `semodule -i`. The exam may include a scenario where the generated
> policy is overly permissive and you must identify why.


[↑ Back to TOC](#toc)

---

## Fix type 5: The application is wrong

If the AVC shows a service accessing something it should never need
(e.g., a web server reading `/etc/shadow`), the correct fix is to
**fix the application configuration**, not the SELinux policy.

SELinux is revealing a configuration problem or a security issue.
Granting access masks it.

Examples of "the application is wrong":

| AVC denial | What it reveals | Correct fix |
|---|---|---|
| httpd reading `/etc/shadow` | Misconfigured auth module trying to use shadow auth | Fix httpd auth config; use PAM properly |
| sshd writing to `/var/lib/mysql/` | sshd is the wrong process; mysqld is actually broken | Fix mysqld startup, not sshd policy |
| cron reading `/root/.gnupg/` | A root-owned cron job is running as a confined domain | Fix cron job to run as appropriate user |

In all cases, `setenforce 0` would "fix" the symptom while hiding the
underlying misconfiguration or security issue.


[↑ Back to TOC](#toc)

---

## Worked example — new custom app needing port label and file context

**Scenario:** A Python application `inventoryd` is deployed under
`/opt/inventoryd/`. It serves an API on port 8765 and writes its database
to `/var/lib/inventoryd/`. A systemd service unit runs it as the `inventoryd`
user. After installation, the service fails to start.

**Step 1 — observe the denials**

```bash
sudo systemctl start inventoryd.service
# Job failed

sudo ausearch -m avc -ts recent
```

Two AVC records appear:

```text
# Denial 1: port binding
avc: denied { name_bind } for pid=4521 comm="inventoryd" src=8765
  scontext=system_u:system_r:bin_t:s0
  tcontext=system_u:object_r:unreserved_port_t:s0
  tclass=tcp_socket

# Denial 2: file write
avc: denied { write } for pid=4521 comm="inventoryd"
  name="inventoryd" dev="vda3"
  scontext=system_u:system_r:bin_t:s0
  tcontext=unconfined_u:object_r:var_t:s0
  tclass=dir
```

**Step 2 — apply fix taxonomy**

Denial 1: port 8765, `unreserved_port_t` → **port label fix** (Fix type 3)
Denial 2: `/var/lib/inventoryd/` has `var_t` → **file context fix** (Fix type 1)

Note: the process is running as `bin_t` because the binary has no specific
SELinux type. In production you would write a full policy module for a custom
domain. For this scenario, apply the minimum fixes.

**Step 3 — fix port label**

```bash
sudo semanage port -a -t http_port_t -p tcp 8765
# inventoryd is an HTTP API server — http_port_t is appropriate
sudo semanage port -l | grep 8765
# http_port_t  tcp  8765, ...
```

**Step 4 — fix file context**

```bash
sudo semanage fcontext -a -t var_lib_t '/var/lib/inventoryd(/.*)?'
sudo restorecon -Rv /var/lib/inventoryd/
ls -Z /var/lib/inventoryd/
# system_u:object_r:var_lib_t:s0  inventoryd.db
```

**Step 5 — verify**

```bash
sudo systemctl start inventoryd.service
sudo systemctl status inventoryd.service
# Active: active (running)

sudo ausearch -m avc -ts recent
# No new denials

curl http://localhost:8765/health
# {"status": "ok"}
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

**1. Using `setenforce 0` to "confirm it's SELinux"**

Symptom: Service starts after `setenforce 0`. Conclusion: "it's an SELinux
problem". But this leaves the system in permissive mode indefinitely.
Fix: Use permissive mode *temporarily* to confirm, then re-enable enforcing
immediately (`setenforce 1`). Apply the correct fix from the taxonomy.

**2. Running `restorecon` without the `semanage fcontext` rule**

Symptom: `restorecon -Rv /srv/myapp/` runs without error but files still
have wrong labels after the service restarts.
Diagnosis: There is no `semanage fcontext` rule for `/srv/myapp/` so
`restorecon` uses the default `var_t` or `default_t` context.
Fix: `semanage fcontext -a -t <correct_type> '/srv/myapp(/.*)?'` first,
then `restorecon -Rv /srv/myapp/`.

**3. Using `setsebool` without `-P`**

Symptom: Boolean fix works immediately but the problem returns after reboot.
Diagnosis: `getsebool httpd_can_network_connect` shows `off`.
Fix: Always use `setsebool -P` for production fixes. The `-P` flag writes
the boolean to the persistent policy store.

**4. Using `semanage port -a` when `-m` is needed**

Symptom: `semanage port -a -t http_port_t -p tcp 8443` fails with
"ValueError: Port tcp/8443 already defined".
Diagnosis: Port 8443 is already labeled (probably `http_port_t` or
`http_cache_port_t` in the default policy).
Fix: Use `semanage port -m -t http_port_t -p tcp 8443` to modify the
existing label.

**5. Loading an unreviewed audit2allow module**

Symptom: Service starts, but the loaded policy module grants far more access
than necessary (e.g., allows `httpd_t` to read all files of type `etc_t`).
Diagnosis: `cat <module>.te` reveals overly broad allow rules.
Fix: Do not use the generated module. Investigate why the denial occurred
using `audit2why` and apply the targeted fix (label, boolean, or port).

**6. Not checking for dontaudit rules hiding denials**

Symptom: Service has odd failures but `ausearch -m avc` shows nothing.
Diagnosis: Some denials are silenced by `dontaudit` rules in the policy —
they are not logged.
Fix: Temporarily disable `dontaudit` rules to see all denials:
```bash
sudo semodule -DB    # disable dontaudit (D) and rebuild (B)
# reproduce the failure
sudo ausearch -m avc -ts recent
sudo semodule -B     # re-enable dontaudit
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Using SELinux: Troubleshooting](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/using_selinux/troubleshooting-problems-related-to-selinux_using-selinux) | Official RHEL SELinux fix guidance |
| [Dan Walsh's SELinux blog](https://danwalsh.livejournal.com/) | Authoritative commentary from the Red Hat SELinux lead |
| [`sepolicy` man page](https://man7.org/linux/man-pages/man8/sepolicy.8.html) | Introspect policy — understand what a confined domain can do |

---


[↑ Back to TOC](#toc)

## Next step

→ [semanage Reference](02-semanage.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
