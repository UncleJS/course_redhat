# semanage — fcontext, port, boolean

`semanage` (SELinux Policy Management) is the tool for making **persistent**
SELinux policy customisations without recompiling the full policy.

---

## Install

```bash
sudo dnf install -y policycoreutils-python-utils
```

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

---

## Next step

→ [Audit Workflow](audit-workflow.md)
