
[↑ Back to TOC](#toc)

# Advanced systemd — Dependencies, Drop-ins
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

This chapter goes beyond basic `systemctl start/stop` to cover unit design,
dependency management, and safe customisation via drop-ins.

At the RHCA level you are expected to design service orchestration — not just
start and stop individual units. That means understanding how systemd builds a
dependency graph from unit directives, how ordering relates to (but differs
from) requirements, and how to safely customise vendor-provided units without
touching files that a package update would overwrite.

The mental model: think of systemd as a DAG (directed acyclic graph) scheduler.
Every `After=` adds an edge; every `Requires=` or `Wants=` adds a dependency.
At boot, systemd resolves this graph, parallelises as much as possible, and
activates units in dependency order. Understanding the graph is the key to
diagnosing unexpectedly slow boots, services that start before their
dependencies are ready, and services that silently fail because a soft dependency
never came up.

Getting dependency directives wrong in production causes intermittent failures
that are hard to reproduce: a service that "usually works" but occasionally
starts before the database is ready, leading to 30-second retries on every cold
boot. Drop-in mistakes are worse — editing a vendor unit directly means the next
`dnf update` silently discards your changes.

---
<a name="toc"></a>

## Table of contents

- [Unit dependency directives](#unit-dependency-directives)
  - [Example: service that needs the network and a database](#example-service-that-needs-the-network-and-a-database)
- [`network.target` vs `network-online.target`](#networktarget-vs-network-onlinetarget)
- [Drop-in files — customise without modifying originals](#drop-in-files-customise-without-modifying-originals)
- [Service restart policies](#service-restart-policies)
- [Template units](#template-units)
- [Target units (grouping)](#target-units-grouping)
- [Socket activation](#socket-activation)
- [Analyse startup time](#analyse-startup-time)
- [Worked example — socket-activated burst service](#worked-example-socket-activated-burst-service)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


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


[↑ Back to TOC](#toc)

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

> **Exam tip:** `network.target` is reached very early in boot — interfaces
> are configured but DHCP may not have completed. Use `network-online.target`
> for any service that actually connects to something at start time.


[↑ Back to TOC](#toc)

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

**Drop-in merge rules:**

- Multiple drop-ins are merged in lexicographic order (e.g., `10-foo.conf`
  before `20-bar.conf`).
- To clear a list directive set by the original unit (e.g., `ExecStart=`),
  first set the directive to empty, then set the new value:

```ini
[Service]
ExecStart=
ExecStart=/usr/local/bin/myapp --custom-flag
```

Failing to clear `ExecStart=` first results in systemd running both the
original command and yours — a subtle bug.

> **Exam tip:** `systemctl edit --full <unit>` creates a complete copy of the
> unit under `/etc/systemd/system/`. Prefer `systemctl edit` (without
> `--full`) to create a minimal drop-in that survives package updates.


[↑ Back to TOC](#toc)

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

When systemd gives up (Result=start-limit-hit), the unit must be manually
reset before it will try again:

```bash
sudo systemctl reset-failed myapp.service
sudo systemctl start myapp.service
```


[↑ Back to TOC](#toc)

---

## Template units

Template units allow one unit file to instantiate multiple services:

```text
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

Additional specifiers available in templates:

| Specifier | Expands to |
|---|---|
| `%i` | Instance name (between `@` and `.service`) |
| `%I` | Unescaped instance name |
| `%n` | Full unit name |
| `%H` | Hostname |
| `%u` | User running the unit |


[↑ Back to TOC](#toc)

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

Targets are also used as milestones in the boot process. Common targets
in order of activation: `sysinit.target` → `basic.target` →
`network.target` → `network-online.target` → `multi-user.target` →
`graphical.target`.

To change the default boot target:

```bash
# Boot to multi-user (text console) instead of graphical
sudo systemctl set-default multi-user.target

# Temporarily isolate to rescue (all non-rescue services stop)
sudo systemctl isolate rescue.target
```


[↑ Back to TOC](#toc)

---

## Socket activation

Socket activation lets systemd create a socket and pass it to the service
only when a connection arrives. Benefits: faster boot (service not started
until needed), burst tolerance (kernel queues connections while the service
starts).

```ini
# /etc/systemd/system/myapp.socket
[Unit]
Description=My App Socket

[Socket]
ListenStream=8080
Accept=no

[Install]
WantedBy=sockets.target
```

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My App Service
Requires=myapp.socket
After=myapp.socket

[Service]
Type=simple
ExecStart=/usr/local/bin/myapp
StandardInput=socket
```

```bash
# Enable the socket (not the service directly)
sudo systemctl enable --now myapp.socket

# The service activates automatically on first connection
```

The socket unit and service unit are linked by name convention:
`myapp.socket` activates `myapp.service`.

> **Exam tip:** With socket activation, `systemctl status myapp.service` may
> show inactive until the first connection arrives. Check
> `systemctl status myapp.socket` to confirm the socket is listening.


[↑ Back to TOC](#toc)

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

The **critical chain** is the sequence of units that determines the total
boot time — the longest dependency path. To speed up boot, focus on units
on the critical chain, not just the slowest individual units.


[↑ Back to TOC](#toc)

---

## Worked example — socket-activated burst service

**Scenario:** A custom metrics collector (`metricsd`) must handle burst
traffic when dozens of hosts simultaneously send data at the top of each
minute. Without socket activation, the service is always running and
consuming memory. With socket activation, the kernel queues connections
during the burst and the service processes them in order.

**Create the socket unit:**

```ini
# /etc/systemd/system/metricsd.socket
[Unit]
Description=Metrics Collector Socket

[Socket]
ListenStream=4000
# Queue up to 128 connections before dropping
Backlog=128
Accept=no

[Install]
WantedBy=sockets.target
```

**Create the service unit:**

```ini
# /etc/systemd/system/metricsd.service
[Unit]
Description=Metrics Collector Service
Requires=metricsd.socket
After=metricsd.socket

[Service]
Type=simple
User=metrics
Group=metrics
ExecStart=/usr/local/bin/metricsd --socket-activation
StandardInput=socket

# Restart if it crashes between bursts
Restart=on-failure
RestartSec=5s

# Harden: metrics daemon needs no special privileges
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
StateDirectory=metricsd
```

**Enable and test:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now metricsd.socket

# Verify socket is listening
ss -tlnp | grep 4000

# Trigger activation
echo "test" | nc localhost 4000

# Confirm the service started
systemctl status metricsd.service
```

**Observe burst behaviour:**

```bash
# Open 50 simultaneous connections (simulate burst)
for i in $(seq 1 50); do echo "data" | nc -q1 localhost 4000 &; done

# Watch the socket queue
ss -tlnp | grep 4000
# Backlog shows queued connections while metricsd processes them in order
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

**1. Using `After=` without `Requires=` or `Wants=`**

Symptom: Service starts in the right order during a normal boot but fails
on a degraded boot where the dependency unit did not start.
Diagnosis: `systemctl status <dep-unit>` shows it never started.
Fix: Add `Wants=<dep-unit>` (weak) or `Requires=<dep-unit>` (strong).

**2. Editing the vendor unit file directly**

Symptom: After `dnf update`, custom configuration (restart policy,
environment variables, resource limits) silently disappears.
Diagnosis: `systemctl cat <unit>` shows the post-update defaults.
Fix: Use `systemctl edit <unit>` to create a drop-in under
`/etc/systemd/system/<unit>.d/override.conf`.

**3. Forgetting `daemon-reload` after editing a unit**

Symptom: Changes to a unit file appear to have no effect — the old
behaviour persists.
Diagnosis: `systemctl cat <unit>` still shows the old file if the daemon
has not reloaded its configuration.
Fix: `sudo systemctl daemon-reload` after every unit file edit.

**4. Clearing a list directive incorrectly**

Symptom: After overriding `ExecStart=` in a drop-in, two processes start
(the original and the new one). For `Type=simple` this means the second
process immediately conflicts with the first.
Diagnosis: `systemctl cat <unit>` shows two `ExecStart=` lines.
Fix: In the drop-in, set `ExecStart=` (empty) on its own line, then set
the new value on the next line.

**5. Using `network.target` for a service that makes connections**

Symptom: Service starts but fails with "connection refused" or "name or
service not known" because DHCP has not completed.
Diagnosis: `journalctl -u <service> -b` shows connection errors immediately
after start.
Fix: Change to `After=network-online.target` and `Wants=network-online.target`.

**6. Template instance not found**

Symptom: `systemctl start myapp@8080.service` fails with "Unit not found".
Diagnosis: `systemctl list-unit-files | grep myapp` shows no template.
Fix: Verify the template file is named `myapp@.service` (with the `@`
before the dot). The `%i` specifier in the file must match the instance
name used on the command line.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`systemd.unit` man page](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html) | Unit dependencies, ordering, and all `[Unit]` directives |
| [systemd — Instantiated units](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html#Description) | Template unit `@` syntax and instance passing |
| [systemd drop-in files](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html#id-1.8) | How override drop-ins work and merge rules |
| [systemd.io blog](https://systemd.io/) | Upstream release notes and advanced feature write-ups |

---


[↑ Back to TOC](#toc)

## Next step

→ [systemd Hardening Knobs](03-systemd-hardening.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
