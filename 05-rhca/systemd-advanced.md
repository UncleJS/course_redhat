# Advanced systemd — Dependencies, Drop-ins

This chapter goes beyond basic `systemctl start/stop` to cover unit design,
dependency management, and safe customisation via drop-ins.

---

## Unit dependency directives

systemd uses directives to define ordering and requirements between units:

| Directive | Meaning |
|---|---|
| `Requires=` | Strong dependency — if the required unit fails, this unit fails too |
| `Wants=` | Weak dependency — if the required unit fails, this unit continues |
| `After=` | This unit starts **after** the listed units |
| `Before=` | This unit starts **before** the listed units |
| `BindsTo=` | Like Requires, but if the dependency stops, this unit stops too |
| `PartOf=` | If parent is restarted/stopped, this unit follows |
| `Conflicts=` | Cannot run simultaneously with the listed unit |

> **💡 After= does not imply Requires=**
> `After=network.target` only sets ordering. To ensure the network is
> present, also add `Wants=network-online.target After=network-online.target`.
>

### Example: service that needs the network and a database

```ini
[Unit]
Description=My Application
After=network-online.target postgresql.service
Wants=network-online.target
Requires=postgresql.service
```

---

## `network.target` vs `network-online.target`

| Target | Meaning |
|---|---|
| `network.target` | Network interfaces configured (may not have connectivity yet) |
| `network-online.target` | Network is up and reachable (NM reports connected) |

For services that make outbound connections at startup, use:

```ini
After=network-online.target
Wants=network-online.target
```

---

## Drop-in files — customise without modifying originals

Drop-ins override or extend a unit without touching the shipped file:

```bash
# Create a drop-in for sshd.service
sudo systemctl edit sshd.service
```

This creates `/etc/systemd/system/sshd.service.d/override.conf`.

Example — add a restart policy without touching the original unit:

```ini
[Service]
Restart=always
RestartSec=5s
```

View the merged effective unit:

```bash
systemctl cat sshd.service
```

After editing a drop-in:

```bash
sudo systemctl daemon-reload
sudo systemctl restart sshd.service
```

---

## Service restart policies

| Value | Meaning |
|---|---|
| `no` | Never restart (default) |
| `always` | Always restart, regardless of exit code |
| `on-failure` | Restart only on non-zero exit or signal |
| `on-abnormal` | Restart on signal, watchdog timeout, or core dump |

```ini
[Service]
Restart=on-failure
RestartSec=10s
StartLimitIntervalSec=60s
StartLimitBurst=3
```

This allows 3 restart attempts in 60 seconds, then gives up.

---

## Template units

Template units allow one unit file to instantiate multiple services:

```
sshd@.service → sshd@22.service, sshd@2222.service
```

A template unit file uses `%i` for the instance parameter:

```ini
# /etc/systemd/system/myapp@.service
[Unit]
Description=My App instance %i

[Service]
ExecStart=/usr/bin/myapp --port %i
```

Start instances:

```bash
sudo systemctl start myapp@8080.service
sudo systemctl start myapp@8081.service
```

---

## Target units (grouping)

```ini
# /etc/systemd/system/myapp.target
[Unit]
Description=All My Application Services
Wants=myapp@8080.service myapp@8081.service
After=network-online.target
```

Start everything:

```bash
sudo systemctl start myapp.target
```

---

## Analyse startup time

```bash
# Total boot time breakdown
systemd-analyze

# Per-unit time
systemd-analyze blame | head -20

# Dependency graph (saves SVG)
systemd-analyze dot --require | dot -Tsvg > boot.svg

# Critical chain to a unit
systemd-analyze critical-chain sshd.service
```

---

## Further reading

| Resource | Notes |
|---|---|
| [`systemd.unit` man page](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html) | Unit dependencies, ordering, and all `[Unit]` directives |
| [systemd — Instantiated units](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html#Description) | Template unit `@` syntax and instance passing |
| [systemd drop-in files](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html#id-1.8) | How override drop-ins work and merge rules |
| [systemd.io blog](https://systemd.io/) | Upstream release notes and advanced feature write-ups |

---

## Next step

→ [systemd Hardening Knobs](systemd-hardening.md)
