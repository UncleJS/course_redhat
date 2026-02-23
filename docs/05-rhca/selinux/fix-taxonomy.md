# SELinux Fix Taxonomy — Label vs Boolean vs Port vs Policy

The most important SELinux skill is choosing the **correct type of fix** for
a given AVC denial. Applying the wrong fix either doesn't work or creates
a security hole.

---

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

!!! warning "Review audit2allow output carefully"
    audit2allow generates the minimum policy to allow what was denied,
    but it has no context about whether the access is *intended*. A module
    that allows `httpd_t` to read `shadow_t` (password hashes) would be
    generated if httpd somehow triggered that denial — and it would be wrong.

---

## Fix type 5: The application is wrong

If the AVC shows a service accessing something it should never need
(e.g., a web server reading `/etc/shadow`), the correct fix is to
**fix the application configuration**, not the SELinux policy.

SELinux is revealing a configuration problem or a security issue.
Granting access masks it.

---

## Next step

→ [semanage Reference](semanage.md)
