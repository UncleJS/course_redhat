# SELinux Fix Taxonomy — Label vs Boolean vs Port vs Policy

The most important SELinux skill is choosing the **correct type of fix** for
a given AVC denial. Applying the wrong fix either doesn't work or creates
a security hole.

---
<a name="toc"></a>

## Table of contents

- [The fix decision tree](#the-fix-decision-tree)
- [Fix type 1: File context (most common)](#fix-type-1-file-context-most-common)
- [Fix type 2: Boolean (targeted policy switch)](#fix-type-2-boolean-targeted-policy-switch)
- [Fix type 3: Port label](#fix-type-3-port-label)
- [Fix type 4: audit2allow (last resort)](#fix-type-4-audit2allow-last-resort)
- [Fix type 5: The application is wrong](#fix-type-5-the-application-is-wrong)


## The fix decision tree

```
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


[↑ Back to TOC](#toc)

---

## Fix type 5: The application is wrong

If the AVC shows a service accessing something it should never need
(e.g., a web server reading `/etc/shadow`), the correct fix is to
**fix the application configuration**, not the SELinux policy.

SELinux is revealing a configuration problem or a security issue.
Granting access masks it.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Using SELinux: Troubleshooting](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/using_selinux/troubleshooting-problems-related-to-selinux_using-selinux) | Official RHEL SELinux fix guidance |
| [Dan Walsh's SELinux blog](https://danwalsh.livejournal.com/) | Authoritative commentary from the Red Hat SELinux lead |
| [`sepolicy` man page](https://man7.org/linux/man-pages/man8/sepolicy.8.html) | Introspect policy — understand what a confined domain can do |

---

## Next step

→ [semanage Reference](02-semanage.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
