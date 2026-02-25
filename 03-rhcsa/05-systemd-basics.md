# systemd Essentials

systemd is the init system and service manager for RHEL 10. Understanding
it is non-negotiable for RHEL administration.

---
<a name="toc"></a>

## Table of contents

- [Key concepts](#key-concepts)
- [The `systemctl` command](#the-systemctl-command)
  - [Start, stop, restart, reload](#start-stop-restart-reload)
  - [Enable and disable (start at boot)](#enable-and-disable-start-at-boot)
  - [Status and introspection](#status-and-introspection)
- [Listing units](#listing-units)
- [System state (targets)](#system-state-targets)
- [Unit files](#unit-files)
  - [View a unit file](#view-a-unit-file)
  - [Edit a unit (use systemctl — not vim directly)](#edit-a-unit-use-systemctl-not-vim-directly)
  - [Reload after editing](#reload-after-editing)
- [Creating a simple service unit](#creating-a-simple-service-unit)
- [Power management](#power-management)


## Key concepts

| Term | Meaning |
|---|---|
| **unit** | A resource systemd manages (service, mount, socket, timer, etc.) |
| **service unit** | A daemon or process managed by systemd (`.service`) |
| **target** | A group of units representing a system state (e.g., `multi-user.target`) |
| **socket unit** | Socket activation — start service on first connection |
| **timer unit** | Scheduled activation (replaces cron for new services) |
| **drop-in** | Override file that extends a unit without modifying the original |


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

---

## Power management

```bash
sudo systemctl poweroff
sudo systemctl reboot
sudo systemctl suspend
sudo systemctl hibernate
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`systemd.unit` man page](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html) | Unit file format and all common directives |
| [`systemd.service` man page](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) | Service-specific directives |
| [systemd.io](https://systemd.io/) | Upstream blog and documentation index |
| [RHEL 10 — Configuring services using systemd](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_basic_system_settings/index) | Official RHEL systemd configuration guide |

---

## Next step

→ [Logs and journalctl](06-logging-journald.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
