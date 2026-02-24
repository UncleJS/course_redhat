# Logs and journalctl

systemd captures all service output in the **journal** — a binary, indexed
log store. `journalctl` is your primary tool for reading it.

---

## Basic usage

```bash
# Show all logs (newest at bottom), page through with less
journalctl

# Reverse order (newest first)
journalctl -r

# Follow in real time (like tail -f)
journalctl -f

# Show only the last 50 lines
journalctl -n 50
```

---

## Filter by unit (service)

```bash
# Logs for one service
journalctl -u sshd.service

# Follow a service's logs live
journalctl -f -u sshd.service

# Multiple units
journalctl -u sshd.service -u firewalld.service
```

---

## Filter by time

```bash
# Since a specific time
journalctl --since "2026-02-23 08:00:00"

# Between two times
journalctl --since "2026-02-23 08:00:00" --until "2026-02-23 09:00:00"

# Since boot
journalctl -b

# Previous boot
journalctl -b -1

# List available boots
journalctl --list-boots
```

---

## Filter by priority (log level)

| Level | Meaning |
|---|---|
| `emerg` (0) | System unusable |
| `alert` (1) | Immediate action required |
| `crit` (2) | Critical condition |
| `err` (3) | Error |
| `warning` (4) | Warning |
| `notice` (5) | Normal but significant |
| `info` (6) | Informational |
| `debug` (7) | Debug messages |

```bash
# Only errors and above
journalctl -p err

# Between warning and error
journalctl -p warning..err
```

---

## Kernel messages

```bash
# Journal kernel messages
journalctl -k

# Since last boot
journalctl -k -b
```

---

## Search output

```bash
# Grep inside journalctl output
journalctl -u sshd | grep "Failed"

# Case-insensitive
journalctl -u sshd | grep -i "failed"
```

---

## Persistent journal

By default on RHEL, the journal is persistent across reboots (stored in
`/var/log/journal/`). If yours is not:

```bash
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo systemctl restart systemd-journald
```

### Control journal disk usage

```bash
# View current disk usage
journalctl --disk-usage

# Vacuum to keep only last 2 weeks
sudo journalctl --vacuum-time=2weeks

# Vacuum to 1 GB max
sudo journalctl --vacuum-size=1G
```

Journal retention is configured in `/etc/systemd/journald.conf`:

```ini
[Journal]
SystemMaxUse=2G
MaxRetentionSec=1month
```

---

## Traditional log files

systemd-journald forwards to `rsyslog` on RHEL, so traditional log files
in `/var/log/` still exist:

| File | Contents |
|---|---|
| `/var/log/messages` | General system messages |
| `/var/log/secure` | Authentication events (SSH, sudo) |
| `/var/log/audit/audit.log` | SELinux AVC denials, audit events |
| `/var/log/dnf.log` | Package operations |
| `/var/log/boot.log` | Boot messages |

---

## Further reading

| Resource | Notes |
|---|---|
| [`journalctl` man page](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) | Complete option and filter reference |
| [`journald.conf` man page](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html) | Retention, storage, and forwarding configuration |
| [RHEL 10 — Using the journal](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/using_systemd_unit_files_in_rhel/index) | Official logging and journal guide |

---

## Next step

→ [Scheduling (timers + cron)](scheduling.md)
