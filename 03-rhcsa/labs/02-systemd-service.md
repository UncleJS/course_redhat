
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab: Create a systemd Service
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCSA
**Estimated time:** 30 minutes
**Topology:** Single VM

---
<a name="toc"></a>

## Table of contents

- [Background](#background)
- [Steps](#steps)
  - [1 — Create the script](#1-create-the-script)
  - [2 — Create the service unit](#2-create-the-service-unit)
  - [3 — Enable and start the service](#3-enable-and-start-the-service)
  - [4 — Add a systemd timer to run it every 5 minutes](#4-add-a-systemd-timer-to-run-it-every-5-minutes)
  - [5 — Simulate a failure and debug it](#5-simulate-a-failure-and-debug-it)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)
- [Why this matters in production](#why-this-matters-in-production)


## Prerequisites

- Completed [systemd Essentials](../05-systemd-basics.md) and [Logs and journalctl](../06-logging-journald.md)
- VM snapshot taken

---


[↑ Back to TOC](#toc)

## Background

Virtually every persistent task on a RHEL system is managed by systemd.
When you install a package like `httpd` or `postgresql`, the installer
creates systemd unit files that define how to start, stop, and supervise
the service. These unit files are the contract between the application and
the init system: they specify the executable, the user to run as, dependencies,
restart behaviour, resource limits, and log handling.

As a sysadmin, you will routinely need to write your own unit files — for
in-house scripts, monitoring agents, backup jobs, and application-specific
startup tasks. Understanding the unit file format and the `systemctl` lifecycle
is not optional: it is the mechanism for deploying and managing any software
that runs on RHEL.

Systemd timers are the modern replacement for `cron`. Unlike cron entries
scattered across user crontabs, timers are systemd units with full journal
logging, dependency management, and `systemctl` lifecycle control. They are
more observable (`systemctl list-timers`), more reliable (catch-up on missed
runs with `Persistent=true`), and easier to debug (`journalctl -u <timer>`).
This lab builds both a service unit and a timer to run it — the canonical
pattern for any recurring automated task.

### Unit file sections reference

Understanding the three-section structure of a service unit helps when
creating units from scratch:

**`[Unit]`** — metadata and dependencies:

| Directive | Purpose |
|---|---|
| `Description=` | Human-readable name shown by `systemctl status` |
| `After=` | Start ordering — this unit starts after listed units |
| `Requires=` | Hard dependency — if the required unit fails, this fails too |
| `Wants=` | Soft dependency — listed unit is started, but failure is tolerated |
| `Documentation=` | Man page or URL for the unit's documentation |

**`[Service]`** — how to run the process:

| Directive | Purpose |
|---|---|
| `Type=simple` | Process stays in foreground; considered started immediately |
| `Type=forking` | Process forks; parent exits; child is the service |
| `Type=oneshot` | Process runs to completion and exits; `RemainAfterExit=yes` to stay "active" |
| `Type=notify` | Process sends a `sd_notify` message when ready |
| `ExecStart=` | The command to run |
| `ExecReload=` | Command to reload config (usually `kill -HUP $MAINPID`) |
| `ExecStop=` | Command to stop the service (default: SIGTERM) |
| `User=` | Run as this user (defaults to root) |
| `WorkingDirectory=` | Set working directory before starting |
| `EnvironmentFile=` | Load environment variables from a file |
| `Restart=` | When to restart: `no`, `on-failure`, `always`, `on-abnormal` |
| `RestartSec=` | Seconds to wait before restarting |

**`[Install]`** — how to enable the unit:

| Directive | Purpose |
|---|---|
| `WantedBy=multi-user.target` | Enable in the standard multi-user runlevel |
| `WantedBy=graphical.target` | Enable in the graphical runlevel |
| `RequiredBy=` | Hard dependency from another target |

---


[↑ Back to TOC](#toc)

## Success criteria

- A custom systemd service runs a script on boot
- The service is enabled and starts automatically
- Logs are visible in `journalctl`
- A failure scenario is understood and debugged

---


[↑ Back to TOC](#toc)

## Steps

### 1 — Create the script

```bash
sudo vim /usr/local/bin/healthcheck.sh
```

```bash
#!/usr/bin/env bash
set -euo pipefail

LOGFILE=/var/log/healthcheck.log
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "${TIMESTAMP} - Healthcheck: disk=$(df -h / | awk 'NR==2{print $5}') mem=$(free -m | awk '/Mem/{print $3}')MB used" >> "${LOGFILE}"
echo "${TIMESTAMP} - Healthcheck complete"
```

```bash
sudo chmod +x /usr/local/bin/healthcheck.sh
```

Test the script manually:

```bash
sudo /usr/local/bin/healthcheck.sh
```

> **✅ Verify**
> Look for: a line printed to stdout and written to `/var/log/healthcheck.log`.
>

> **Hint:** Always test scripts manually before creating a service unit.
> A script that fails due to a syntax error or missing command will cause
> the service to enter `failed` state immediately, and `journalctl` will
> show the error — but you can save yourself that debugging loop by testing
> first with `bash -x /usr/local/bin/healthcheck.sh` to trace execution.


[↑ Back to TOC](#toc)

---

### 2 — Create the service unit

```bash
sudo vim /etc/systemd/system/healthcheck.service
```

```ini
[Unit]
Description=System Healthcheck Script
After=network.target
Documentation=man:systemd.service(5)

[Service]
Type=oneshot
ExecStart=/usr/local/bin/healthcheck.sh
StandardOutput=journal
StandardError=journal
RemainAfterExit=yes
User=root

[Install]
WantedBy=multi-user.target
```

> **Hint:** `Type=oneshot` is for services that run to completion and exit —
> unlike `Type=simple` which expects the process to stay running. With
> `RemainAfterExit=yes`, systemd marks the service as `active (exited)` after
> a successful run, rather than `inactive`. This makes it easy to see from
> `systemctl status` whether the script ran successfully.

Key fields explained:

| Field | Value | Why |
|---|---|---|
| `After=network.target` | Dependency ordering | Ensures network is up before script runs |
| `Type=oneshot` | Service type | Script runs to completion and exits |
| `StandardOutput=journal` | Log routing | Captures stdout to the journal |
| `RemainAfterExit=yes` | Post-exit state | Service shows `active` after successful run |
| `WantedBy=multi-user.target` | Boot target | Service starts in normal multi-user mode |


[↑ Back to TOC](#toc)

---

### 3 — Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now healthcheck.service
```

> **Hint:** `daemon-reload` is required every time you create or modify a
> unit file. Systemd caches unit definitions in memory — without a reload,
> your changes are invisible to it.

> **✅ Verify — Service active**
> ```bash
> systemctl status healthcheck.service
> ```
> Look for: `Active: active (exited)` (oneshot services show "exited" not "running")
>

> **✅ Verify — Logs in journal**
> ```bash
> journalctl -u healthcheck.service
> ```
> Look for: the healthcheck output line.
>

> **✅ Verify — Enabled at boot**
> ```bash
> systemctl is-enabled healthcheck.service
> ```
> Expected: `enabled`
>


[↑ Back to TOC](#toc)

---

### 4 — Add a systemd timer to run it every 5 minutes

```bash
sudo vim /etc/systemd/system/healthcheck.timer
```

```ini
[Unit]
Description=Run healthcheck every 5 minutes
Requires=healthcheck.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now healthcheck.timer
```

> **Hint:** `Persistent=true` means if the timer missed a run (e.g., the VM
> was powered off), systemd will run the service immediately at next boot to
> "catch up". Without this, a missed run is silently skipped.

> **✅ Verify**
> ```bash
> systemctl list-timers | grep healthcheck
> ```
> Look for: `healthcheck.timer` with a next trigger time shown.
>


[↑ Back to TOC](#toc)

---

### 5 — Simulate a failure and debug it

Break the script on purpose:

```bash
sudo vim /usr/local/bin/healthcheck.sh
# Change the first executable line to:
# /nonexistent-binary
```

Restart the service:

```bash
sudo systemctl restart healthcheck.service
systemctl status healthcheck.service
```

Look for: `Failed` status and error details.

```bash
journalctl -u healthcheck.service -n 20
```

Find the error. Fix the script, then:

```bash
sudo systemctl restart healthcheck.service
systemctl status healthcheck.service
```

> **Hint:** The most useful information is in `journalctl -u <service> -n 20`.
> The status output from `systemctl status` shows the last few log lines but
> truncates them. For full output, use `journalctl`. Look for the exit code
> in the log — exit code 127 means "command not found", exit code 1 is a
> generic script error, and exit code 126 is "permission denied on executable".


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
sudo systemctl disable --now healthcheck.timer healthcheck.service
sudo rm /etc/systemd/system/healthcheck.{service,timer}
sudo rm /usr/local/bin/healthcheck.sh
sudo rm -f /var/log/healthcheck.log
sudo systemctl daemon-reload
```

---


[↑ Back to TOC](#toc)

## Troubleshooting guide

| Symptom | Likely cause | Fix |
|---|---|---|
| `daemon-reload` needed warning | Unit file changed but not reloaded | `sudo systemctl daemon-reload` |
| Service fails immediately | Script has syntax error or wrong path | `bash -n /usr/local/bin/healthcheck.sh` to check syntax; `which` to check path |
| `is-enabled: disabled` | Forgot `enable` step | `sudo systemctl enable healthcheck.service` |
| Timer doesn't trigger | Timer unit not enabled | `sudo systemctl enable --now healthcheck.timer` |
| `Active: failed` with exit code 1 | Script runtime error | `journalctl -u healthcheck.service -n 30` — read the full error |
| Service runs but log file not written | Wrong path or permission on `/var/log/` | Check `ls -l /var/log/healthcheck.log` — create with `sudo touch` and set permissions |
| `systemctl status` shows truncated output | Journal output longer than display | `journalctl -u healthcheck.service --no-pager` for full output |
| Timer runs but service not triggered | `Requires=` vs `Unit=` mismatch | Confirm timer `[Unit]` has `Requires=healthcheck.service` and `Unit=` is not overriding it |

---


[↑ Back to TOC](#toc)

## Why this matters in production

This pattern — a script, a service unit, and a timer — is the foundation for
automated maintenance tasks, health reporting, log rotation triggers, and
application-specific watchdogs. Knowing how to create, debug, and manage these
units is a daily skill for RHEL administrators.

Every production RHEL deployment you encounter will have custom unit files.
Database installations add `postgresql.service`. Monitoring agents add
`node_exporter.service`. Backup jobs add a service + timer pair. Being able
to read an existing unit file, understand its dependencies, and diagnose why
it failed is as fundamental as knowing `ls` and `cat`.

The `journalctl` integration is a key advantage over cron and shell scripts.
Every line written to stdout or stderr by a systemd service is automatically
tagged with the unit name, timestamp, and machine identifier. You can filter
the entire system log to just one service's output instantly, without hunting
for log files in custom locations:

```bash
# All logs for a service, most recent first
journalctl -u healthcheck.service -r

# Follow logs in real time
journalctl -u healthcheck.service -f

# Logs since last boot
journalctl -u healthcheck.service -b

# Logs with timestamps and priority
journalctl -u healthcheck.service -p err..warning --since "1 hour ago"
```

### Systemd target reference

When writing `WantedBy=` in the `[Install]` section, choose the correct target:

| Target | Used for |
|---|---|
| `multi-user.target` | Services needed in non-graphical multi-user mode (most server services) |
| `graphical.target` | Services that require a graphical environment |
| `network-online.target` | Services that need a fully operational network (not just "up") |
| `timers.target` | Systemd timer units |
| `default.target` | Alias for the default boot target (usually `multi-user.target` on servers) |

Note the difference between `network.target` and `network-online.target`:
- `network.target` = interfaces have been configured (addresses may not be assigned yet)
- `network-online.target` = NetworkManager confirms connectivity is available

For services that need to make outbound connections (e.g., register with a
service, fetch a config file), use `After=network-online.target` with
`Wants=network-online.target` to ensure the network is genuinely available.

### Common exam mistakes on systemd service tasks

| Mistake | Consequence | Prevention |
|---|---|---|
| Forgetting `daemon-reload` after creating/modifying unit | systemd uses stale unit; changes invisible | Always run `daemon-reload` before `enable` or `restart` |
| Using `enable` without `--now` | Service enabled but not started | Use `enable --now` or follow with `systemctl start` |
| Script not executable | Service fails immediately with "Permission denied" (exit 126) | Always `chmod +x` the script before creating the unit |
| Absolute path not used in `ExecStart=` | Service fails with "command not found" | Never use relative paths in unit files |
| Using `Type=simple` for a script that exits | Service shows "dead" immediately after start | Use `Type=oneshot` with `RemainAfterExit=yes` for scripts |
| `WantedBy=` missing or wrong target | Service not started on boot | Use `multi-user.target` for standard server services |
| Unit file syntax error | `daemon-reload` silently loads broken unit | Check with `systemctl status <unit>` after reload; look for load errors |

### Debugging failed services: systematic approach

When a service enters `failed` state, work through this sequence:

```bash
# Step 1: What is the current state?
systemctl status healthcheck.service
# Look for: exit code, last log lines

# Step 2: Full journal output (status truncates)
journalctl -u healthcheck.service -n 50 --no-pager
# Look for: actual error message

# Step 3: Check the unit file loaded correctly
systemctl cat healthcheck.service
# Look for: is this the unit you think it is?

# Step 4: Test the command directly
sudo /usr/local/bin/healthcheck.sh
# Does it run without error when called manually?

# Step 5: Check environment differences
# systemd runs with a minimal environment — no PATH, no HOME shortcuts
# If the script works manually but not in systemd, add:
# Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
# to the [Service] section

# Step 6: Verify with explicit shell invocation (for debugging only)
# ExecStart=/bin/bash -x /usr/local/bin/healthcheck.sh
# This prints each command before execution — very useful for diagnosing
# scripts that fail silently
```

### Exit codes reference

systemd reports the script's exit code in the unit status. Common codes:

| Exit code | Meaning | Common cause |
|---|---|---|
| `0` | Success | — |
| `1` | Generic error | Script reached `exit 1` or unhandled error |
| `126` | Permission denied on executable | Missing `chmod +x` or SELinux label issue |
| `127` | Command not found | Typo in `ExecStart=` path or missing dependency |
| `143` | Killed by SIGTERM | systemd stopped the service (normal during `stop`) |
| `137` | Killed by SIGKILL | OOM killer or `MemoryMax=` limit exceeded |

### Timer syntax reference

Systemd timer `OnCalendar=` expressions are more powerful than cron syntax:

| Expression | Equivalent cron | Meaning |
|---|---|---|
| `OnBootSec=5min` | *(no equivalent)* | 5 minutes after boot |
| `OnUnitActiveSec=1h` | *(no equivalent)* | 1 hour after last activation |
| `OnCalendar=daily` | `0 0 * * *` | Midnight every day |
| `OnCalendar=weekly` | `0 0 * * 0` | Sunday midnight |
| `OnCalendar=Mon *-*-* 09:00:00` | `0 9 * * 1` | Monday at 09:00 |
| `OnCalendar=*:0/5` | `*/5 * * * *` | Every 5 minutes |
| `OnCalendar=*-*-* 02:30:00` | `30 2 * * *` | 02:30 every day |

Test calendar expressions before deploying:

```bash
systemd-analyze calendar "Mon *-*-* 09:00:00"
# Shows: next trigger time and normalized form
```

List all active timers on the system:

```bash
systemctl list-timers --all
# Columns: NEXT (next trigger), LEFT (time until), LAST (last run), PASSED (time since), UNIT, ACTIVATES
```

---


[↑ Back to TOC](#toc)

## Extension tasks

**Extension 1 — Add restart-on-failure behaviour**

Modify the service to restart automatically if it exits with a non-zero
status. Use `Restart=on-failure` and `RestartSec=10` in the `[Service]`
section. Break the script again and observe `systemctl status` showing the
restart attempts. Then fix it.

```ini
[Service]
Type=simple          # change from oneshot for this extension
ExecStart=/usr/local/bin/healthcheck.sh
Restart=on-failure
RestartSec=10
```

Note: `Restart=` does not work well with `Type=oneshot` in all systemd
versions — change the type to `simple` for this extension.

**Extension 2 — Run as a non-root user**

Create a dedicated system user `healthd`:

```bash
sudo useradd -r -s /sbin/nologin -d /var/lib/healthd -m healthd
sudo mkdir -p /var/lib/healthd
sudo chown healthd:healthd /var/log/healthcheck.log 2>/dev/null || \
  sudo touch /var/log/healthcheck.log && sudo chown healthd /var/log/healthcheck.log
```

Change `User=root` to `User=healthd` in the service unit. Reload and restart.
Verify the script runs as `healthd` by adding `id` to the script output and
checking the journal.

**Extension 3 — Resource limits**

Add resource constraints to the service to simulate a real production
constraint:

```ini
[Service]
MemoryMax=64M
CPUQuota=10%
```

Reload and restart. Use `systemctl status` to verify the cgroup constraints
are applied. Then add a memory allocation loop to the script and observe
whether the service is killed when it exceeds the limit.

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab — LVM + XFS Grow](03-lvm-xfs-grow.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
