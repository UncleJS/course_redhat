# Journald Retention and Forwarding

On a RHEL host, the journal is your primary log source. At RHCA level, you
need to design journal retention, size policies, and log forwarding correctly.

---

## Journal storage location

| Path | Meaning |
|---|---|
| `/run/log/journal/` | Volatile (RAM); cleared on reboot |
| `/var/log/journal/` | Persistent; survives reboots |

RHEL 10 creates `/var/log/journal/` by default, making the journal persistent.

---

## `journald.conf` — configuration file

```bash
sudo vim /etc/systemd/journald.conf
```

Key settings:

```ini
[Journal]
# Storage location
Storage=persistent          # persistent (default), volatile, auto, none

# Maximum disk space for the journal
SystemMaxUse=2G             # default: 10% of filesystem
SystemKeepFree=1G           # always keep 1G free

# Per-boot limit
SystemMaxFileSize=128M      # max size of one journal file

# Runtime (volatile) limits
RuntimeMaxUse=512M

# Max retention by time
MaxRetentionSec=3months

# Max file size before rotation
MaxFileSec=1week

# Compression
Compress=yes                # enabled by default

# Rate limiting (prevent log storms from crashing journald)
RateLimitIntervalSec=30s
RateLimitBurst=1000
```

After editing:

```bash
sudo systemctl restart systemd-journald
```

---

## Check current journal disk usage

```bash
journalctl --disk-usage
```

---

## Manual vacuum (immediate cleanup)

```bash
# Keep only last 2 weeks
sudo journalctl --vacuum-time=2weeks

# Keep only 500 MB
sudo journalctl --vacuum-size=500M

# Keep only 5 files
sudo journalctl --vacuum-files=5
```

---

## Forwarding to syslog (rsyslog)

By default on RHEL, journald forwards to rsyslog, which writes to `/var/log/`.

Check the forwarding is active:

```bash
grep "^ForwardToSyslog" /etc/systemd/journald.conf
# If not set, default is 'yes' when rsyslog is installed
```

To disable syslog forwarding (if using a centralised log shipper):

```ini
[Journal]
ForwardToSyslog=no
```

---

## Forwarding to a remote journal (systemd-journal-remote)

For centralised collection without a SIEM, RHEL ships `systemd-journal-remote`:

```bash
# On log collection server
sudo dnf install -y systemd-journal-remote
sudo systemctl enable --now systemd-journal-remote.socket

# On sending hosts
sudo dnf install -y systemd-journal-upload
sudo vim /etc/systemd/journal-upload.conf
```

```ini
[Upload]
URL=http://logserver.lab.local:19532
```

```bash
sudo systemctl enable --now systemd-journal-upload.service
```

---

## Per-service log namespaces

RHEL 10 supports log namespaces — a service can write to an isolated journal:

```ini
[Service]
LogNamespace=myapp
```

View:

```bash
journalctl --namespace=myapp
```

Useful for high-volume services to avoid filling the system journal.

---

## Forwarding to a SIEM (rsyslog → remote)

Most enterprise environments forward to a SIEM (Splunk, Elastic, etc.) via rsyslog:

```bash
sudo vim /etc/rsyslog.d/99-remote.conf
```

```
# Forward all logs to remote syslog server (UDP 514)
*.* @logserver.example.com:514

# TCP (more reliable)
*.* @@logserver.example.com:514
```

```bash
sudo systemctl restart rsyslog
```

---

## Further reading

| Resource | Notes |
|---|---|
| [`journald.conf` man page](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html) | All retention, storage, compression, and forwarding options |
| [rsyslog documentation](https://www.rsyslog.com/doc/master/index.html) | Forwarding journal to rsyslog or remote syslog servers |
| [RHEL 10 — Viewing and managing log files](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/using_systemd_unit_files_in_rhel/index) | Official journal management guide |

---

## Next step

→ [SELinux Deep Dive: Fix Taxonomy](selinux/fix-taxonomy.md)
