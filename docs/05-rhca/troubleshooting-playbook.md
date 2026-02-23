# Troubleshooting Playbook — First 10 Minutes

When something breaks on a RHEL host, this playbook gives you a repeatable,
ordered approach that finds the majority of problems efficiently.

---

## The mindset

> Observe before you change. Gather evidence, form a hypothesis, test one
> thing at a time, and document what you tried.

Changing random settings hoping something fixes it wastes time and can
make the problem worse.

---

## The First 10 Minutes Checklist

### 0 — What is the reported symptom?

- What exactly is broken? (service unreachable / command fails / system slow)
- When did it start?
- What changed recently? (update, config edit, deploy, cron job)

---

### 1 — System health (30 seconds)

```bash
# System load and uptime
uptime

# Memory pressure
free -m

# Disk space (full disk breaks many things silently)
df -h

# Inode exhaustion (disk "full" but df shows space)
df -ih

# Failed systemd units
systemctl --failed
```

If disk is full → find and clean large files first.
If a unit failed → jump to Step 3.

---

### 2 — Recent changes (1 minute)

```bash
# Last 50 messages across all services
journalctl -n 50 -r

# Since last hour
journalctl --since "1 hour ago"

# Package changes
sudo dnf history | head -20

# Recently modified files in /etc
find /etc -mtime -1 -type f 2>/dev/null | sort
```

---

### 3 — Service status (2 minutes)

```bash
# Is the service running?
sudo systemctl status <service-name>

# Detailed logs
journalctl -u <service-name> -n 100

# Did it fail to start?
journalctl -u <service-name> -b | grep -i "failed\|error\|denied"
```

Common causes of service failures:

| Error in log | Likely cause |
|---|---|
| `Permission denied` | File/dir permissions or SELinux |
| `avc: denied` | SELinux AVC denial |
| `Address already in use` | Port conflict |
| `No such file or directory` | Missing binary, config, or data file |
| `Failed to bind` | Port blocked or SELinux port policy |

---

### 4 — SELinux check (1 minute)

```bash
# Current mode
getenforce

# Recent denials
sudo ausearch -m avc -ts recent

# Denials for specific process
sudo ausearch -m avc -c httpd -ts today
```

If you see AVC denials → see [SELinux Troubleshooting](../03-rhcsa/selinux-avc-basics.md).

!!! warning "Do NOT set setenforce 0 as a fix"
    Use permissive mode for **diagnosis only**, immediately re-enable
    enforcing, and fix the root cause.

---

### 5 — Network connectivity (2 minutes)

```bash
# Is the interface up?
ip link show
ip addr show

# Can we reach the gateway?
ip route show
ping -c 2 $(ip route | awk '/default/{print $3}')

# DNS working?
ping -c 2 8.8.8.8          # IP (bypass DNS)
ping -c 2 access.redhat.com # needs DNS

# Is the service listening?
ss -tlnp | grep <port>

# Firewall blocking?
sudo firewall-cmd --list-all
```

---

### 6 — The "DNS vs routing vs firewall" decision tree

```
Can ping 8.8.8.8?
  No  → routing/network problem → check ip route, gateway, interface
  Yes → Can ping access.redhat.com?
          No  → DNS problem → check resolvectl, /etc/resolv.conf
          Yes → Can curl http://service/?
                  No  → Is it listening? (ss -tlnp)
                          No  → service not running
                          Yes → firewall blocking? (firewall-cmd --list-all)
                                  Still blocked? → SELinux? (ausearch -m avc)
```

---

### 7 — Resource exhaustion (1 minute)

```bash
# CPU and memory hogs
top -b -n 1 | head -30

# Or htop if installed
htop

# I/O wait
iostat -x 1 3   # install: sudo dnf install -y sysstat

# Open file limits
ulimit -n
cat /proc/sys/fs/file-max
```

---

### 8 — Log files (catch-all)

```bash
# Everything since last boot
journalctl -b | grep -iE "error|fail|denied|refused" | tail -50

# Auth failures
sudo grep "Failed\|Invalid" /var/log/secure | tail -20

# Kernel ring buffer
dmesg | tail -30
dmesg | grep -iE "error|fail|oom"
```

---

## Escalation checklist

Before escalating, document:

1. The exact error message
2. Steps you already tried
3. Output of: `journalctl -u <service> -n 100`
4. Output of: `systemctl status <service>`
5. Output of: `ausearch -m avc -ts recent`
6. Output of: `df -h`, `free -m`, `ip addr`, `firewall-cmd --list-all`

---

## Next step

→ [Advanced systemd](systemd-advanced.md)
