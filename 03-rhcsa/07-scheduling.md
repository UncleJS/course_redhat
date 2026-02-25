# Scheduling — systemd Timers and cron

RHEL supports two scheduling mechanisms: **systemd timers** (modern, preferred)
and **cron** (legacy, still widely used). Know both.

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
- [systemd timer vs cron: when to use which](#systemd-timer-vs-cron-when-to-use-which)


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

# 5 minutes after boot
OnBootSec=5min

# Relative to last run
OnUnitActiveSec=1h
```

Test calendar expressions before deploying:

```bash
systemd-analyze calendar "*:0/15"
systemd-analyze calendar "Mon *-*-* 08:30:00"
```

### List and monitor timers

```bash
# List all active timers with next trigger time
systemctl list-timers

# View timer logs
journalctl -u cleanup.timer
journalctl -u cleanup.service
```


[↑ Back to TOC](#toc)

---

## cron (legacy)

cron is still present on RHEL and familiar to many. Use it for legacy scripts
or when portability matters.

### crontab format

```
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

Special shortcuts:

| Shortcut | Equivalent |
|---|---|
| `@hourly` | `0 * * * *` |
| `@daily` | `0 0 * * *` |
| `@weekly` | `0 0 * * 0` |
| `@reboot` | On each system startup |

### Edit your crontab

```bash
crontab -e     # edit your own crontab
crontab -l     # list your current crontab
crontab -r     # remove your crontab (careful!)
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

```
0 2 * * * root /usr/local/bin/cleanup.sh
```

### cron logs

```bash
# cron execution logs
sudo journalctl -u crond
grep CRON /var/log/messages
```


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

## Next step

→ [Networking Basics](08-networking-basics.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
