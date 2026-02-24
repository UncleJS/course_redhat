# SELinux Fundamentals

SELinux (Security-Enhanced Linux) is a **Mandatory Access Control (MAC)**
system built into the Linux kernel. It enforces security policies that go
far beyond standard Unix permissions.

---

## MAC vs DAC

| Model | Name | Controls access via |
|---|---|---|
| **DAC** | Discretionary Access Control | File owner sets permissions (`chmod`) |
| **MAC** | Mandatory Access Control | Policy defines what processes can access |

With SELinux, even if a file has `777` permissions, a process still needs
the correct SELinux type to access it. This is why "fix it with chmod 777"
is wrong — SELinux may still block the access.

---

## SELinux modes

| Mode | Behaviour |
|---|---|
| **Enforcing** | Policy is enforced; violations are blocked and logged |
| **Permissive** | Policy is NOT enforced; violations are logged only |
| **Disabled** | SELinux is completely off — requires reboot to re-enable |

```bash
# Check current mode
getenforce

# Detailed status
sestatus
```

### Temporarily switch modes (no reboot, not persistent)

```bash
sudo setenforce 0    # Permissive (troubleshooting ONLY)
sudo setenforce 1    # Enforcing (put it back immediately)
```

> **⚠️ Do NOT set Permissive as a fix**
> Permissive mode is for **temporary troubleshooting only**. Running in
> permissive mode defeats the entire point of SELinux. Always fix the
> root cause and return to enforcing.
>

### Permanent mode (requires reboot)

```bash
sudo vim /etc/selinux/config
```

```
SELINUX=enforcing    # recommended
SELINUX=permissive   # temp troubleshooting only
SELINUX=disabled     # never in production
```

> **🚨 Never set SELINUX=disabled in production**
> Re-enabling after disabling requires a full filesystem relabel at next
> boot, which takes time and can cause issues if interrupted.
>

---

## SELinux contexts

Every file, process, and socket has a **security context** (label):

```
user:role:type:level
```

The **type** is the most important component — it determines what can access what.

```bash
# Show file context
ls -Z /etc/hosts
ls -Z /var/www/html/

# Show process context
ps -eZ | grep httpd
ps -eZ | grep sshd

# Show your own context
id -Z
```

---

## File contexts — `restorecon`

Files must have the correct context for the service that accesses them.
The most common SELinux issue is a file with the wrong context.

```bash
# Restore the correct context (from policy definition)
sudo restorecon -v /var/www/html/index.html

# Recursive restore
sudo restorecon -Rv /var/www/html/

# Check what context a path should have (without changing it)
sudo matchpathcon /var/www/html/index.html
```

If you move files with `mv`, they keep the context from the source.
If you copy with `cp`, they get the context of the destination.

> **💡 Use cp not mv for web content**
> When placing content into `/var/www/html/`, use `cp` or `restorecon` after
> moving to ensure the correct `httpd_sys_content_t` context is applied.
>

---

## SELinux booleans

Booleans are policy switches that enable/disable specific behaviours
without writing custom policy.

```bash
# List all booleans
sudo getsebool -a

# Search booleans related to httpd
sudo getsebool -a | grep httpd

# Get status of a specific boolean
getsebool httpd_can_network_connect

# Turn a boolean ON (runtime only)
sudo setsebool httpd_can_network_connect on

# Turn a boolean ON persistently (survives reboot)
sudo setsebool -P httpd_can_network_connect on
```

Common booleans for new admins:

| Boolean | What it enables |
|---|---|
| `httpd_can_network_connect` | Apache to make outbound network connections |
| `httpd_use_nfs` | Apache to serve NFS-mounted content |
| `samba_enable_home_dirs` | Samba to share home directories |
| `ftpd_anon_write` | FTP anonymous upload |

---

## Install SELinux tools

```bash
sudo dnf install -y policycoreutils-python-utils setroubleshoot-server
```

These provide `semanage`, `sealert`, and improved audit analysis.

---

## Next step

→ [SELinux Troubleshooting (AVCs)](selinux-avc-basics.md)
