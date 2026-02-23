# systemd Essentials

systemd is the init system and service manager for RHEL 10. Understanding
it is non-negotiable for RHEL administration.

---

## Key concepts

| Term | Meaning |
|---|---|
| **unit** | A resource systemd manages (service, mount, socket, timer, etc.) |
| **service unit** | A daemon or process managed by systemd (`.service`) |
| **target** | A group of units representing a system state (e.g., `multi-user.target`) |
| **socket unit** | Socket activation — start service on first connection |
| **timer unit** | Scheduled activation (replaces cron for new services) |
| **drop-in** | Override file that extends a unit without modifying the original |

---

## The `systemctl` command

### Start, stop, restart, reload

```bash
sudo systemctl start sshd
sudo systemctl stop sshd
sudo systemctl restart sshd      # stop + start
sudo systemctl reload sshd       # reload config without stopping (if supported)
sudo systemctl reload-or-restart sshd  # try reload, fall back to restart
```

### Enable and disable (start at boot)

```bash
sudo systemctl enable sshd           # enable at boot
sudo systemctl disable sshd          # disable at boot
sudo systemctl enable --now sshd     # enable AND start immediately
sudo systemctl disable --now sshd    # disable AND stop immediately
```

### Status and introspection

```bash
# Rich status view (recent logs included)
sudo systemctl status sshd

# Is the service running?
systemctl is-active sshd

# Is it enabled at boot?
systemctl is-enabled sshd

# Did it fail?
systemctl is-failed sshd

# List all failed units
systemctl --failed
```

---

## Listing units

```bash
# All loaded and active units
systemctl list-units

# All service units (loaded)
systemctl list-units --type=service

# All units including inactive
systemctl list-units --all

# Units that failed
systemctl list-units --state=failed
```

---

## System state (targets)

```bash
# Current default target (runlevel equivalent)
systemctl get-default

# Change default target
sudo systemctl set-default multi-user.target    # headless (no GUI)
sudo systemctl set-default graphical.target     # GUI

# Switch to a target immediately (non-persistent)
sudo systemctl isolate rescue.target

# Common targets
# poweroff.target  — shutdown
# rescue.target    — single-user repair mode
# multi-user.target — full multi-user, no GUI
# graphical.target  — multi-user + GUI
```

---

## Unit files

Unit files live in:

| Path | Contents |
|---|---|
| `/usr/lib/systemd/system/` | Shipped by packages (do not edit) |
| `/etc/systemd/system/` | Admin-created or admin-modified units |
| `/run/systemd/system/` | Runtime units (ephemeral) |

### View a unit file

```bash
systemctl cat sshd.service
```

### Edit a unit (use systemctl — not vim directly)

```bash
# Create a drop-in (recommended — preserves original)
sudo systemctl edit sshd.service

# Edit the full unit file (replaces shipped file)
sudo systemctl edit --full sshd.service
```

### Reload after editing

```bash
sudo systemctl daemon-reload
```

---

## Creating a simple service unit

```bash
sudo vim /etc/systemd/system/myscript.service
```

```ini
[Unit]
Description=My Custom Script
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/myscript.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now myscript.service
sudo systemctl status myscript.service
```

---

## Power management

```bash
sudo systemctl poweroff
sudo systemctl reboot
sudo systemctl suspend
sudo systemctl hibernate
```

---

## Next step

→ [Logs and journalctl](logging-journald.md)
