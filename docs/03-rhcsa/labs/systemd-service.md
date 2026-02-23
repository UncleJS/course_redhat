# Lab: Create a systemd Service

**Track:** RHCSA
**Estimated time:** 30 minutes
**Topology:** Single VM

---

## Prerequisites

- Completed [systemd Essentials](../systemd-basics.md) and [Logs and journalctl](../logging-journald.md)
- VM snapshot taken

---

## Success criteria

- A custom systemd service runs a script on boot
- The service is enabled and starts automatically
- Logs are visible in `journalctl`
- A failure scenario is understood and debugged

---

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

!!! success "Verify"
    Look for: a line printed to stdout and written to `/var/log/healthcheck.log`.

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

---

### 3 — Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now healthcheck.service
```

!!! success "Verify — Service active"
    ```bash
    systemctl status healthcheck.service
    ```
    Look for: `Active: active (exited)` (oneshot services show "exited" not "running")

!!! success "Verify — Logs in journal"
    ```bash
    journalctl -u healthcheck.service
    ```
    Look for: the healthcheck output line.

!!! success "Verify — Enabled at boot"
    ```bash
    systemctl is-enabled healthcheck.service
    ```
    Expected: `enabled`

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

!!! success "Verify"
    ```bash
    systemctl list-timers | grep healthcheck
    ```
    Look for: `healthcheck.timer` with a next trigger time shown.

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

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `daemon-reload` needed warning | Unit file changed but not reloaded | `sudo systemctl daemon-reload` |
| Service fails immediately | Script has syntax error or wrong path | `bash -n /usr/local/bin/healthcheck.sh` |
| `is-enabled: disabled` | Forgot `enable` step | `sudo systemctl enable healthcheck.service` |
| Timer doesn't trigger | Timer unit not enabled | `sudo systemctl enable --now healthcheck.timer` |

---

## Why this matters in production

This pattern — a script, a service unit, and a timer — is the foundation for
automated maintenance tasks, health reporting, log rotation triggers, and
application-specific watchdogs. Knowing how to create, debug, and manage these
units is a daily skill for RHEL administrators.
