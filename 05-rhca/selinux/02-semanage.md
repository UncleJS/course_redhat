
[↑ Back to TOC](#toc)

# semanage — fcontext, port, boolean
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

`semanage` (SELinux Policy Management) is the tool for making **persistent**
SELinux policy customisations without recompiling the full policy.

At the RHCA level, `semanage` is the authoritative tool for all day-to-day
SELinux policy customisation. Understanding its sub-commands — `fcontext`,
`port`, `boolean`, `login`, `user` — and the precise semantics of each
(`-a` vs `-m` vs `-d`, the role of `restorecon` as a separate step from
`fcontext`) is a hard exam requirement.

The mental model: `semanage` manages the local policy customisation layer
that sits on top of the compiled base policy. The base policy is installed
by the `selinux-policy-targeted` package and cannot be edited directly.
`semanage` writes your customisations to `/etc/selinux/targeted/contexts/`
and related stores. These customisations survive policy package updates
because they are layered on top, not embedded in the base.

Every `semanage` command has a `-C` flag to list only **custom** (local)
entries — not the full default policy. This is critical for auditing what
changes have been made on a specific host, and for the `export`/`import`
workflow used to replicate configuration across a fleet.

Getting `semanage` wrong is subtle: the command succeeds, the policy database
is updated, but nothing on disk changes until `restorecon` is run. This
two-step requirement is the most common source of "SELinux fix applied but
service still fails" in both production and exam environments.

---
<a name="toc"></a>

## Table of contents

- [Install](#install)
- [semanage fcontext](#semanage-fcontext)
  - [Common types](#common-types)
- [semanage port](#semanage-port)
- [semanage boolean](#semanage-boolean)
- [semanage login and user](#semanage-login-and-user)
- [Export and import policy customisations](#export-and-import-policy-customisations)
- [Worked example — applying multiple semanage customisations](#worked-example-applying-multiple-semanage-customisations)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## Install

```bash
sudo dnf install -y policycoreutils-python-utils
```


[↑ Back to TOC](#toc)

---

## semanage fcontext

Manage file context definitions — what SELinux type a path should have.

```bash
# List all custom fcontext rules
sudo semanage fcontext -l -C

# List all rules (including defaults) for a path
sudo semanage fcontext -l | grep /var/www

# Add a rule for a directory and all its contents
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/webapp(/.*)?"

# Add a rule for a specific file
sudo semanage fcontext -a -t sshd_key_t "/etc/ssh/keys/id_rsa_custom"

# Modify an existing custom rule
sudo semanage fcontext -m -t httpd_sys_rw_content_t "/srv/webapp/uploads(/.*)?"

# Delete a custom rule
sudo semanage fcontext -d "/srv/webapp(/.*)?"

# Apply rules to existing files
sudo restorecon -Rv /srv/webapp/
```

> **⚠️ semanage fcontext alone is not enough**
> `semanage fcontext` defines the rule in policy. It does **not** change
> the labels on existing files. Always follow with `restorecon -Rv <path>`.
>

**Understanding the regex pattern:**

The pattern `/srv/webapp(/.*)?` uses a standard extended regex:
- `/srv/webapp` — matches the directory itself
- `(/.*)?` — optionally matches a `/` followed by any characters (any
  file or subdirectory within)

Without the `(/.*)?`, the rule only applies to the directory itself, not
its contents. Always include `(/.*)?` for recursive coverage.

### Common types

| Type | Used for |
|---|---|
| `httpd_sys_content_t` | Web server read-only content |
| `httpd_sys_rw_content_t` | Web server read-write content (uploads) |
| `sshd_key_t` | SSH private keys |
| `postgresql_db_t` | PostgreSQL data |
| `mysqld_db_t` | MySQL/MariaDB data |
| `container_file_t` | Files accessible by rootless containers |
| `var_log_t` | Log files |
| `admin_home_t` | Admin user home directory |

To find the correct type for a similar path in the default policy:

```bash
# What type does /var/www/html use?
ls -Z /var/www/html/
# system_u:object_r:httpd_sys_content_t:s0

# Search policy for types matching a keyword
seinfo -t | grep httpd
```


[↑ Back to TOC](#toc)

---

## semanage port

Manage port-to-type mappings:

```bash
# List all port definitions
sudo semanage port -l

# List ports for a specific type
sudo semanage port -l | grep http_port

# Add a port
sudo semanage port -a -t http_port_t -p tcp 8080
sudo semanage port -a -t ssh_port_t -p tcp 2222

# Modify (change type of an existing custom port)
sudo semanage port -m -t http_port_t -p tcp 8443

# Delete a custom port
sudo semanage port -d -t http_port_t -p tcp 8080

# View custom (non-default) entries only
sudo semanage port -l -C
```

**When to use `-a` vs `-m`:**

`-a` (add) creates a new entry. It fails if the port already has any label.
`-m` (modify) changes an existing entry. It fails if the port has no entry.

To determine which to use:

```bash
sudo semanage port -l | grep " 8443 "
# If found → use -m
# If not found → use -a
```

**Common port types:**

| Type | Default ports |
|---|---|
| `http_port_t` | 80, 443, 8080, 8443 |
| `ssh_port_t` | 22 |
| `postgresql_port_t` | 5432 |
| `mysqld_port_t` | 3306 |
| `smtp_port_t` | 25, 465, 587 |
| `dns_port_t` | 53 (tcp and udp) |

> **Exam tip:** `semanage port -a` adds a rule; the change takes effect
> immediately for new connections. Unlike `fcontext`, there is no separate
> "apply" step — the kernel reads the port label database at bind time.


[↑ Back to TOC](#toc)

---

## semanage boolean

Manage SELinux booleans persistently (same as `setsebool -P`):

```bash
# List all booleans
sudo semanage boolean -l

# List custom (non-default) booleans
sudo semanage boolean -l -C

# Set a boolean (persistent)
sudo semanage boolean -m --on httpd_can_network_connect
sudo semanage boolean -m --off httpd_can_network_connect
```

Both `semanage boolean -m --on <name>` and `setsebool -P <name> on` produce
the same result — a persistent boolean change. Use whichever is clearer in
context. `setsebool -P` is more commonly documented in official RHEL guides.

To check the current value and whether it was changed from the default:

```bash
sudo semanage boolean -l | grep httpd_can_network_connect
# httpd_can_network_connect  (on , off)  Allow httpd to make network connections
# Format: (current, default)
# (on, off) means currently on, default is off — a customisation exists
```


[↑ Back to TOC](#toc)

---

## semanage login and user

Map Linux users to SELinux users:

```bash
# List login mappings
sudo semanage login -l

# Map a Linux user to an SELinux user
sudo semanage login -a -s staff_u alice
sudo semanage login -a -s sysadm_u admin

# Delete mapping
sudo semanage login -d alice
```

**SELinux user types and their privilege levels:**

| SELinux user | Linux privilege level |
|---|---|
| `user_u` | Unprivileged user — cannot use sudo |
| `staff_u` | Can use sudo; standard admin user |
| `sysadm_u` | Full system administrator |
| `system_u` | System processes (not interactive users) |
| `unconfined_u` | Runs without MLS/MCS constraints (default for root) |

Mapping users to confined SELinux users (`staff_u`, `user_u`) is a
defence-in-depth measure: even if a user's credentials are compromised,
the SELinux user mapping limits the domains they can transition to.


[↑ Back to TOC](#toc)

---

## Export and import policy customisations

```bash
# Export all local customisations
sudo semanage export -f /tmp/selinux-customisations.txt

# Import on another host
sudo semanage import -f /tmp/selinux-customisations.txt
```

This is very useful for applying the same SELinux customisations across
multiple hosts via Ansible.

The export file is a plain-text list of `semanage` commands. Review it
before importing — it will overwrite existing customisations on the
target host without warning.

```bash
# Review what will be imported
cat /tmp/selinux-customisations.txt
# fcontext -a -t httpd_sys_content_t "/srv/webapp(/.*)?"
# port -a -t http_port_t -p tcp 8765
# boolean -m --on httpd_can_network_connect
```

**Ansible integration:**

```yaml
- name: Apply SELinux customisations from exported file
  ansible.builtin.copy:
    src: selinux-customisations.txt
    dest: /tmp/selinux-customisations.txt

- name: Import SELinux customisations
  ansible.builtin.command: semanage import -f /tmp/selinux-customisations.txt

- name: Restore file contexts
  ansible.builtin.command: restorecon -Rv /srv/webapp/
```


[↑ Back to TOC](#toc)

---

## Worked example — applying multiple semanage customisations

**Scenario:** A new RHEL 10 host is being configured for a Gitea installation.
Gitea serves on port 3000, stores repositories under `/data/gitea/repos/`,
stores its app data under `/data/gitea/app/`, and runs as the `git` user.
SELinux is enforcing and all paths are non-standard.

**Step 1 — determine required changes**

```bash
# What denials occur when gitea starts?
sudo ausearch -m avc -ts recent | sudo audit2why
# Denial 1: gitea cannot bind port 3000 (unreserved_port_t)
# Denial 2: gitea cannot read/write /data/gitea/ (default_t)
```

**Step 2 — port label**

```bash
sudo semanage port -a -t http_port_t -p tcp 3000
sudo semanage port -l | grep 3000
# http_port_t  tcp  3000, ...
```

**Step 3 — file context for repositories**

```bash
# Repository data: read-write web content
sudo semanage fcontext -a -t httpd_sys_rw_content_t '/data/gitea/repos(/.*)?'

# App data: similar to var_lib
sudo semanage fcontext -a -t var_lib_t '/data/gitea/app(/.*)?'

# Apply
sudo restorecon -Rv /data/gitea/

# Verify
ls -Z /data/gitea/repos/
# system_u:object_r:httpd_sys_rw_content_t:s0
```

**Step 4 — boolean for outbound git operations (if needed)**

```bash
# Gitea calls git fetch/push to remote repositories (outbound network)
sudo setsebool -P httpd_can_network_connect on
```

**Step 5 — export for fleet replication**

```bash
sudo semanage export -f /tmp/gitea-selinux.txt
cat /tmp/gitea-selinux.txt
# fcontext -a -t httpd_sys_rw_content_t '/data/gitea/repos(/.*)?'
# fcontext -a -t var_lib_t '/data/gitea/app(/.*)?'
# port -a -t http_port_t -p tcp 3000
# boolean -m --on httpd_can_network_connect
```

**Step 6 — start and verify**

```bash
sudo systemctl start gitea.service
sudo systemctl status gitea.service
# Active: active (running)

sudo ausearch -m avc -ts recent
# No new denials

curl http://localhost:3000/
# Gitea welcome page
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

**1. Forgetting `restorecon` after `semanage fcontext`**

Symptom: AVC denial persists after `semanage fcontext -a -t ...`. The
`semanage` command succeeded with no error.
Diagnosis: `ls -Z /path/` shows the old label — `semanage fcontext` only
updates the policy database, not files on disk.
Fix: `sudo restorecon -Rv /path/` to apply the rule to existing files.

**2. Pattern does not match subdirectories**

Symptom: `semanage fcontext -a -t httpd_sys_content_t '/srv/web'` added.
`restorecon -Rv /srv/web/` runs. But files inside the directory still have
wrong labels.
Diagnosis: The pattern `/srv/web` only matches the directory itself, not its
contents. `ls -Z /srv/web/file.html` shows the old label.
Fix: Use `/srv/web(/.*)?` to match the directory and all contents.

**3. Using `-a` when `-m` is needed**

Symptom: `semanage port -a -t ssh_port_t -p tcp 2222` fails with
"ValueError: Port tcp/2222 already defined".
Diagnosis: Port 2222 already has a label in the policy (possibly
`unreserved_port_t` explicitly set by a previous admin).
Fix: `sudo semanage port -m -t ssh_port_t -p tcp 2222`.

**4. `semanage` not installed**

Symptom: `semanage: command not found`.
Fix: `sudo dnf install -y policycoreutils-python-utils`.

**5. Exporting and importing without reviewing the file**

Symptom: After importing `selinux-customisations.txt` on a new host, a
previously working service breaks because an old fcontext rule was imported
that conflicts with the new host's directory layout.
Fix: Always `cat` the export file and review every rule before `semanage import`.

**6. Confusing `semanage boolean` and `setsebool`**

Symptom: `semanage boolean -m --on httpd_can_network_connect` sets the
boolean to `on` persistently. `setsebool httpd_can_network_connect on`
(without `-P`) sets it only for the current session.
Diagnosis: After reboot, boolean reverts.
Fix: Use `setsebool -P` or `semanage boolean -m --on` for persistence.
Both are equivalent for persistence; only `setsebool` without `-P` is
session-only.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`semanage` man page](https://man7.org/linux/man-pages/man8/semanage.8.html) | Full subcommand reference: fcontext, port, boolean, user, login |
| [`semanage-fcontext` man page](https://man7.org/linux/man-pages/man8/semanage-fcontext.8.html) | File context management in detail |
| [`semanage-port` man page](https://man7.org/linux/man-pages/man8/semanage-port.8.html) | Port labeling — add, delete, list |
| [RHEL 10 — Customizing SELinux policy](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/using_selinux/customizing-selinux-policy_using-selinux) | Official semanage and fcontext customization guide |

---


[↑ Back to TOC](#toc)

## Next step

→ [Audit Workflow](03-audit-workflow.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
