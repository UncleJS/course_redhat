
[↑ Back to TOC](#toc)

# Scheduling — systemd Timers and cron
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

RHEL supports two scheduling mechanisms: **systemd timers** (modern, preferred)
and **cron** (legacy, still widely used). Know both.

Scheduled jobs are the backbone of operational automation — log rotation,
database backups, certificate renewal, report generation, and health checks
all rely on reliable task scheduling. Understanding the strengths and failure
modes of each mechanism lets you choose correctly and diagnose failures
systematically.

**systemd timers** pair a `.timer` unit with a `.service` unit. The timer
defines *when* to fire; the service defines *what* to run. Because both are
systemd units, all of systemd's features apply: full journald logging,
dependency ordering, restart policies, resource limits, and security
sandboxing. Missed runs are caught automatically with `Persistent=true`.

**cron** has been on UNIX systems since 1975 and is still present on every
RHEL system. Its strength is simplicity and near-universal familiarity. Its
weakness is that logging is minimal, missed runs are silently discarded,
and there is no integration with systemd's dependency or resource-limiting
machinery. For new work, prefer systemd timers. For existing cron jobs,
migration is low priority unless the limitations cause problems.

A critical operational difference: **cron uses the local system timezone**
while **systemd timer `OnCalendar` expressions default to UTC**. Specify a
timezone explicitly in timers when local-time scheduling is required, or
place the timer in a systemd user session that follows the user's locale.

---
<a name="toc"></a>

## Table of contents

- [systemd timers (recommended)](#systemd-timers-recommended)
  - [Create a scheduled job](#create-a-scheduled-job)
  - [Timer schedule syntax](#timer-schedule-syntax)
  - [List and monitor timers](#list-and-monitor-timers)
- [cron (legacy)](#cron-legacy)
  - [crontab format](#crontab-format)
  - [Edit your crontab](#edit-your-crontab)
  - [System-wide cron](#system-wide-cron)
  - [cron logs](#cron-logs)
- [anacron — handling missed jobs](#anacron-handling-missed-jobs)
- [at — one-time scheduling](#at-one-time-scheduling)
- [systemd timer vs cron: when to use which](#systemd-timer-vs-cron-when-to-use-which)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## systemd timers (recommended)

A timer consists of two unit files:
- `.timer` — defines when to run
- `.service` — defines what to run

### Create a scheduled job

**Step 1 — write the service unit:**

```bash
sudo vim /etc/systemd/system/cleanup.service
```

```ini
[Unit]
Description=Cleanup old temp files

[Service]
Type=oneshot
ExecStart=/usr/local/bin/cleanup.sh
```

**Step 2 — write the timer unit:**

```bash
sudo vim /etc/systemd/system/cleanup.timer
```

```ini
[Unit]
Description=Run cleanup daily at 2am

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

`Persistent=true` means: if the system was off at scheduled time, run
immediately at next boot.

**Step 3 — enable and start the timer:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cleanup.timer
```

> **Exam tip:** Enable the **timer unit**, not the service unit. Enabling
> the service unit directly means it runs at every boot, not on a schedule.
> The timer controls when the service fires.

### Timer schedule syntax

```ini
# Every day at 02:00
OnCalendar=*-*-* 02:00:00

# Every hour
OnCalendar=hourly

# Every Monday at 08:30
OnCalendar=Mon *-*-* 08:30:00

# Every 15 minutes
OnCalendar=*:0/15

# First day of every month at midnight
OnCalendar=*-*-01 00:00:00

# 5 minutes after boot
OnBootSec=5min

# Relative to last run
OnUnitActiveSec=1h

# Specify timezone explicitly (avoids UTC confusion)
OnCalendar=America/New_York *-*-* 02:00:00
```

Test calendar expressions before deploying:

```bash
systemd-analyze calendar "*:0/15"
systemd-analyze calendar "Mon *-*-* 08:30:00"

# Show the next 5 trigger times
systemd-analyze calendar --iterations=5 "*-*-* 02:00:00"
```

> **Exam tip:** cron uses local time; systemd timers default to UTC.
> Specify the timezone explicitly with `OnCalendar=America/New_York *-*-* 02:00:00`
> when local-time scheduling matters. Forgetting this causes jobs to fire at
> the wrong hour in non-UTC environments.

### List and monitor timers

```bash
# List all active timers with next trigger time
systemctl list-timers

# List all timers including inactive
systemctl list-timers --all

# View timer logs
journalctl -u cleanup.timer
journalctl -u cleanup.service

# Check when the timer last fired and when next
systemctl status cleanup.timer
```


[↑ Back to TOC](#toc)

---

## cron (legacy)

cron is still present on RHEL and familiar to many. Use it for legacy scripts
or when portability matters.

### crontab format

```text
minute  hour  day  month  weekday  command
  0       2    *    *        *      /usr/local/bin/cleanup.sh
```

| Field | Values |
|---|---|
| minute | 0–59 |
| hour | 0–23 |
| day of month | 1–31 |
| month | 1–12 |
| day of week | 0–7 (0 and 7 = Sunday) |

Step syntax: `*/5` means "every 5 units". Range syntax: `8-17` means 8 through
17. List syntax: `1,15` means 1st and 15th.

```text
# Every 5 minutes
*/5  *  *  *  *  /usr/local/bin/check.sh

# Weekdays at 08:00
0  8  *  *  1-5  /usr/local/bin/report.sh

# 1st and 15th of every month at midnight
0  0  1,15  *  *  /usr/local/bin/billing.sh
```

Special shortcuts:

| Shortcut | Equivalent |
|---|---|
| `@hourly` | `0 * * * *` |
| `@daily` | `0 0 * * *` |
| `@weekly` | `0 0 * * 0` |
| `@monthly` | `0 0 1 * *` |
| `@reboot` | On each system startup |

### Edit your crontab

```bash
crontab -e     # edit your own crontab
crontab -l     # list your current crontab
crontab -r     # remove your crontab (careful!)

# Edit another user's crontab (root only)
sudo crontab -e -u username
sudo crontab -l -u username
```

### System-wide cron

```bash
# Drop scripts directly into these directories:
/etc/cron.hourly/
/etc/cron.daily/
/etc/cron.weekly/
/etc/cron.monthly/

# Or add to system crontab
sudo vim /etc/cron.d/myjob
```

`/etc/cron.d/` entries include a username field:

```text
0 2 * * * root /usr/local/bin/cleanup.sh
```

Scripts in `/etc/cron.daily/` and similar directories must be executable
and must not have a file extension (`.sh` extensions are ignored by `run-parts`):

```bash
sudo chmod +x /etc/cron.daily/myjob
```

### cron logs

```bash
# cron execution logs
sudo journalctl -u crond

# Traditional log
grep CRON /var/log/messages

# See what ran recently
sudo journalctl -u crond --since today
```


[↑ Back to TOC](#toc)

---

## anacron — handling missed jobs

`anacron` handles jobs that may be missed because the system is not running
24/7 (e.g., laptops, systems that are shut down at night). Unlike cron, it
specifies a *delay after boot* rather than an exact time.

```bash
# anacron configuration
cat /etc/anacrontab
```

```text
# period  delay  job-id   command
1         5      cron.daily    run-parts /etc/cron.daily
7         25     cron.weekly   run-parts /etc/cron.weekly
@monthly  45     cron.monthly  run-parts /etc/cron.monthly
```

| Field | Meaning |
|---|---|
| period | Days between runs (1 = daily, 7 = weekly) |
| delay | Minutes after boot before running |
| job-id | Unique identifier for tracking last run |
| command | Command to execute |

anacron tracks last run dates in `/var/spool/anacron/`. If the system missed
a scheduled run, anacron fires it the next time the system boots and the
delay has elapsed.


[↑ Back to TOC](#toc)

---

## at — one-time scheduling

`at` schedules a command to run once at a future time — useful for maintenance
windows.

```bash
# Install if needed
sudo dnf install -y at
sudo systemctl enable --now atd

# Schedule a command
echo "/usr/local/bin/maintenance.sh" | at 23:00

# Schedule for a specific date/time
echo "systemctl restart httpd" | at 2:30 AM tomorrow
echo "systemctl restart httpd" | at 02:30 2026-04-01

# Interactive mode
at 23:00
# Type commands, press Ctrl+D to submit

# List pending at jobs
atq

# Remove a pending job (by job number from atq)
atrm 3

# View a job's content
at -c 3
```

Access control for `at` is managed via `/etc/at.allow` and `/etc/at.deny`.
If `at.allow` exists, only listed users may use `at`. If only `at.deny`
exists, everyone except listed users may use it.


[↑ Back to TOC](#toc)

---

## systemd timer vs cron: when to use which

| Scenario | Recommendation |
|---|---|
| New jobs on RHEL | systemd timer |
| Existing scripts you don't want to migrate | cron |
| Need dependency on network/other services | systemd timer (After=) |
| Centralized log review | systemd timer (journalctl) |
| Catch up missed runs | systemd timer (Persistent=true) |
| Need resource limits (CPU, memory) | systemd timer (uses cgroup) |
| Portability across Linux distributions | cron |
| One-time future execution | `at` |
| Jobs that must run even if system was off | anacron or systemd timer with Persistent=true |


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** Create a systemd timer that runs a database backup script
(`/usr/local/bin/db-backup.sh`) every day at 01:30 local time (US/Eastern),
run as the `dbadmin` user. Ensure it catches up if the system was down
at the scheduled time.

```bash
# 1 — Create the backup script (placeholder)
sudo tee /usr/local/bin/db-backup.sh <<'EOF'
#!/bin/bash
set -euo pipefail
BACKUP_DIR="/var/backups/db"
mkdir -p "$BACKUP_DIR"
mysqldump --all-databases | gzip > "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).sql.gz"
# Keep only last 7 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
EOF
sudo chmod +x /usr/local/bin/db-backup.sh

# 2 — Create the service unit
sudo tee /etc/systemd/system/db-backup.service <<'EOF'
[Unit]
Description=Daily database backup
After=mysql.service
Requires=mysql.service

[Service]
Type=oneshot
User=dbadmin
Group=dbadmin
ExecStart=/usr/local/bin/db-backup.sh
StandardOutput=journal
StandardError=journal
EOF

# 3 — Create the timer unit with explicit timezone
sudo tee /etc/systemd/system/db-backup.timer <<'EOF'
[Unit]
Description=Run database backup daily at 01:30 Eastern

[Timer]
OnCalendar=America/New_York *-*-* 01:30:00
Persistent=true
RandomizedDelaySec=5min

[Install]
WantedBy=timers.target
EOF

# 4 — Enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now db-backup.timer

# 5 — Verify next trigger
systemctl list-timers db-backup.timer

# 6 — Test the service manually before waiting for the timer
sudo systemctl start db-backup.service
sudo systemctl status db-backup.service
journalctl -u db-backup.service -n 30
```

`RandomizedDelaySec=5min` spreads the start time randomly within a 5-minute
window — useful when many timers fire at exactly the same time and could
create a resource spike.


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| Enabled the `.service` instead of `.timer` | Job runs at every boot instead of on schedule | `systemctl disable service`; `systemctl enable --now timer` |
| Timer fires at wrong hour (UTC vs local time) | Job runs at unexpected time | Add `America/City` timezone prefix to `OnCalendar`, verify with `systemd-analyze calendar` |
| `Persistent=true` missing | Missed runs silently skipped | Add `Persistent=true` to `[Timer]` section |
| Script not executable | Service enters failed state immediately | `chmod +x /path/to/script` |
| cron script has `.sh` extension in `/etc/cron.daily/` | `run-parts` silently skips it | Remove the `.sh` extension; scripts must have no extension |
| crontab uses wrong path (no `PATH` set) | Command not found at runtime | Use full paths in cron commands; or add `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` at top of crontab |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`systemd.timer` man page](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) | Timer unit directives and calendar expressions |
| [`systemd.time` man page](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html) | Timestamp and timespan format reference |
| [`crontab` man page](https://man7.org/linux/man-pages/man5/crontab.5.html) | Cron expression syntax |
| [crontab.guru](https://crontab.guru/) | Interactive cron expression editor and validator |

---


[↑ Back to TOC](#toc)

## Next step

→ [Networking Basics](08-networking-basics.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
