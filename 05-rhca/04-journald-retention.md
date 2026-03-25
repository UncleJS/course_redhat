
[↑ Back to TOC](#toc)

# Journald Retention and Forwarding
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

On a RHEL host, the journal is your primary log source. At RHCA level, you
need to design journal retention, size policies, and log forwarding correctly.

In a production environment, log management is an operational requirement
with compliance implications. Retention policies must balance storage costs
against audit and forensics needs. Forwarding architecture must be resilient
to host failure — a journal that only exists locally is lost when the host
crashes, which is precisely when you most need the logs.

The mental model for journald is a circular buffer with configurable size and
time bounds. When the buffer fills, the oldest entries are vacuumed. Every
configuration knob is a constraint on that buffer: `SystemMaxUse` caps absolute
size, `MaxRetentionSec` caps age, `RateLimitBurst` protects against log storms.
Forwarding taps the buffer in real time and ships entries to a durable
destination before they might be vacuumed.

Getting this wrong means either filling the disk with logs (bringing down the
host) or retaining so little that a security incident cannot be reconstructed.
A log forwarding misconfiguration means critical audit events are silently
dropped without any error visible to operators.

---
<a name="toc"></a>

## Table of contents

- [Journal storage location](#journal-storage-location)
- [`journald.conf` — configuration file](#journaldconf-configuration-file)
- [Check current journal disk usage](#check-current-journal-disk-usage)
- [Manual vacuum (immediate cleanup)](#manual-vacuum-immediate-cleanup)
- [Forwarding to syslog (rsyslog)](#forwarding-to-syslog-rsyslog)
- [Forwarding to a remote journal (systemd-journal-remote)](#forwarding-to-a-remote-journal-systemd-journal-remote)
- [Per-service log namespaces](#per-service-log-namespaces)
- [Forwarding to a SIEM (rsyslog → remote)](#forwarding-to-a-siem-rsyslog-remote)
- [Worked example — designing retention for a web server](#worked-example-designing-retention-for-a-web-server)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## Journal storage location

| Path | Meaning |
|---|---|
| `/run/log/journal/` | Volatile (RAM); cleared on reboot |
| `/var/log/journal/` | Persistent; survives reboots |

RHEL 10 creates `/var/log/journal/` by default, making the journal persistent.

To confirm persistence:

```bash
ls /var/log/journal/
# Should show a machine-ID directory

journalctl --disk-usage
# Shows total size across all journal files
```

To switch from persistent to volatile (not recommended for production):

```ini
[Journal]
Storage=volatile
```


[↑ Back to TOC](#toc)

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

**How the limits interact:** journald enforces whichever limit is hit first.
If `SystemMaxUse=2G` is set but `MaxRetentionSec=1week` expires first,
old files are vacuumed by age. Both constraints apply simultaneously — the
journal never exceeds the size limit even if the time limit has not expired.

> **Exam tip:** `SystemMaxUse` is the ceiling. `SystemKeepFree` is a floor
> on available disk space. If the disk fills to within `SystemKeepFree` of
> capacity, journald vacuums even if `SystemMaxUse` has not been reached.


[↑ Back to TOC](#toc)

---

## Check current journal disk usage

```bash
journalctl --disk-usage
```

To see individual journal files:

```bash
ls -lh /var/log/journal/$(ls /var/log/journal/)/
```

To verify which boot entries are available:

```bash
journalctl --list-boots
```


[↑ Back to TOC](#toc)

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

These commands operate immediately on existing journal files. They do not
change the ongoing retention configuration in `journald.conf` — use both
the config file for policy and vacuum commands for one-time cleanup.

To verify the result:

```bash
journalctl --disk-usage
# Size should reflect the vacuum applied
```


[↑ Back to TOC](#toc)

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

Other forwarding targets available in `journald.conf`:

| Directive | Destination |
|---|---|
| `ForwardToSyslog=yes` | rsyslog socket `/run/systemd/journal/syslog` |
| `ForwardToKMsg=yes` | Kernel message buffer (rarely needed) |
| `ForwardToConsole=yes` | System console (useful for headless debugging) |
| `ForwardToWall=yes` | All logged-in users via `wall` (default: yes for ERR+) |


[↑ Back to TOC](#toc)

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

On the collection server, received journals are stored in
`/var/log/journal/remote/` and can be read with:

```bash
journalctl --directory=/var/log/journal/remote/
```

For TLS-secured transport (required in production):

```ini
[Upload]
URL=https://logserver.lab.local:19532
ServerKeyFile=/etc/systemd/journal-remote.key
ServerCertificateFile=/etc/systemd/journal-remote.cert
TrustedCertificateFile=/etc/ssl/certs/ca-bundle.crt
```


[↑ Back to TOC](#toc)

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

Set independent retention for a namespace by creating
`/etc/systemd/journald@myapp.conf`:

```ini
[Journal]
SystemMaxUse=500M
MaxRetentionSec=1week
```

Then restart the namespace journal:

```bash
sudo systemctl restart systemd-journald@myapp.service
```


[↑ Back to TOC](#toc)

---

## Forwarding to a SIEM (rsyslog → remote)

Most enterprise environments forward to a SIEM (Splunk, Elastic, etc.) via rsyslog:

```bash
sudo vim /etc/rsyslog.d/99-remote.conf
```

```text
# Forward all logs to remote syslog server (UDP 514)
*.* @logserver.example.com:514

# TCP (more reliable)
*.* @@logserver.example.com:514
```

```bash
sudo systemctl restart rsyslog
```

For structured forwarding (JSON, which SIEMs prefer), use rsyslog's
`mmjsonparse` module to forward journal metadata intact:

```text
module(load="imjournal" StateFile="imjournal.state" Ratelimit.Burst="20000")
module(load="omfwd")

*.* action(
  type="omfwd"
  target="logserver.example.com"
  port="514"
  protocol="tcp"
  template="RSYSLOG_SyslogProtocol23Format"
)
```


[↑ Back to TOC](#toc)

---

## Worked example — designing retention for a web server

**Scenario:** A RHEL 10 web server hosts a PCI-DSS-scoped application. The
compliance requirement is 90 days of log retention. The root filesystem is
20 GB, with `/var` on a separate 10 GB LV. A central Splunk instance receives
logs via rsyslog.

**Requirements:**
- 90 days minimum local retention (in case Splunk is unavailable)
- Journal must not fill `/var` (keep at least 2 GB free)
- High-volume access logs go to the `webapp` namespace to avoid crowding
  the system journal
- All logs forwarded to Splunk in near-real-time

**Design:**

```ini
# /etc/systemd/journald.conf
[Journal]
Storage=persistent
SystemMaxUse=6G          # cap at 6G (leaves ~4G free on 10G /var)
SystemKeepFree=2G        # hard floor: always keep 2G free
MaxRetentionSec=90days   # PCI-DSS 90-day requirement
MaxFileSec=1week         # rotate weekly for easier vacuum management
Compress=yes
RateLimitIntervalSec=30s
RateLimitBurst=5000      # web server generates high log volume
ForwardToSyslog=yes      # enable rsyslog forwarding
```

```ini
# /etc/systemd/journald@webapp.conf
[Journal]
SystemMaxUse=2G
MaxRetentionSec=90days
```

```ini
# /etc/httpd/conf.d/logging.conf (or the app's unit)
# In the app's unit:
[Service]
LogNamespace=webapp
```

```bash
# /etc/rsyslog.d/50-splunk.conf
*.* @@splunk.example.com:5514
```

**Verify the design:**

```bash
# Confirm retention setting
journalctl --disk-usage
grep MaxRetentionSec /etc/systemd/journald.conf

# Confirm rsyslog is forwarding
logger -t test "PCI audit test entry"
# Check Splunk receives the entry within ~30 seconds

# Confirm namespace is active
journalctl --namespace=webapp --since "5 minutes ago"
```

> **Exam tip:** In the exam, `journalctl --vacuum-time=` and
> `journalctl --vacuum-size=` operate on the journal immediately. Setting
> `MaxRetentionSec=` in `journald.conf` applies the limit going forward
> and on the next restart — use `--vacuum-time=` for immediate cleanup.


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

**1. Journal does not persist across reboots**

Symptom: `journalctl -b -1` returns "No entries" — no logs from the previous
boot.
Diagnosis: `ls /var/log/journal/` — directory does not exist or is empty.
Fix: Create the directory and restart journald:
```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
```
Alternatively set `Storage=persistent` in `journald.conf`.

**2. Journal fills the disk despite SystemMaxUse**

Symptom: `/var` reaches 100% capacity even though `SystemMaxUse=2G` is set
and the journal is only 1.5 GB.
Diagnosis: `df -h /var` — other data (application logs, RPM cache, container
images) is filling the partition, not the journal.
Fix: Use `du -xh /var --max-depth=2 | sort -rh | head -10` to find the real
disk hog. Consider moving `/var/log` to its own LV.

**3. Rate limiting drops legitimate log entries**

Symptom: Service logs appear truncated during busy periods. `journalctl -u
<service>` shows "Suppressed N messages from <service>".
Diagnosis: Default `RateLimitBurst=1000` is too low for a high-volume service.
Fix: Increase `RateLimitBurst` or move the service to its own log namespace
with higher limits.

**4. rsyslog forwarding silently stops**

Symptom: Splunk / remote syslog server stops receiving log entries but
rsyslog appears to be running.
Diagnosis: `journalctl -u rsyslog` may show TCP connection errors.
`rsyslogd -N1` validates the configuration syntax.
Fix: Check network connectivity to the remote host. For TCP forwarding, add
queue settings to buffer and retry:
```text
action(type="omfwd" target="..." queue.type="LinkedList" queue.size="10000"
       action.resumeRetryCount="-1")
```

**5. semanage fcontext change not applied to existing files**

Symptom: After changing `journald.conf` to use a new log path, journald
cannot write because SELinux denies access.
Diagnosis: `ausearch -m avc -c systemd-journald` shows label mismatch.
Fix: `semanage fcontext -a -t var_log_t '/new/path(/.*)?' && restorecon -Rv /new/path`.

**6. Log namespace not isolated as expected**

Symptom: A service with `LogNamespace=myapp` still writes to the system journal.
Diagnosis: `systemctl status systemd-journald@myapp.service` — the namespace
journal may not be running.
Fix: `sudo systemctl start systemd-journald@myapp.service`. The namespace
journal must be running for entries to be stored separately.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`journald.conf` man page](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html) | All retention, storage, compression, and forwarding options |
| [rsyslog documentation](https://www.rsyslog.com/doc/master/index.html) | Forwarding journal to rsyslog or remote syslog servers |
| [RHEL 10 — Viewing and managing log files](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/using_systemd_unit_files_in_rhel/index) | Official journal management guide |

---


[↑ Back to TOC](#toc)

## Next step

→ [SELinux Deep Dive: Fix Taxonomy](selinux/01-fix-taxonomy.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
