
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# tuned — Profile-Based System Tuning
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

## Overview

`tuned` is a systemd service that applies kernel parameter and device setting profiles appropriate for a given workload. On RHEL 10 it is the **first-line tuning tool** — apply the right profile before manually touching any `sysctl` knobs.

At the RHCA level, profile selection is a deliberate architectural decision,
not a default-accept. Every RHEL host has a workload class — batch compute,
latency-sensitive API server, database backend, hypervisor host — and each
class has a corresponding or derivable `tuned` profile. Applying the wrong
profile (or leaving it at the installer default `virtual-guest` when the
workload is a latency-sensitive database) introduces a measurable and
unnecessary performance floor.

The mental model: `tuned` is a configuration management system for kernel
parameters and hardware settings. Just as Ansible enforces software
configuration state, `tuned` enforces kernel tuning state. It is idempotent
(re-applying the same profile is safe), composable (custom profiles can
inherit and override base profiles), and verifiable (you can confirm what it
applied by reading the actual kernel parameters it set).

A server running the wrong `tuned` profile can halve throughput, double
latency, or cause periodic GC pauses in JVM applications (from Transparent
Huge Pages). These problems appear as mysterious performance regressions
that don't correlate with obvious system metrics — the kind that RHCA-level
engineers are expected to diagnose and fix.


[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [Overview](#overview)
- [How tuned Works](#how-tuned-works)
- [Installing and Enabling tuned](#installing-and-enabling-tuned)
- [Listing and Selecting Profiles](#listing-and-selecting-profiles)
  - [Profile selection guide](#profile-selection-guide)
- [Inspecting Profile Contents](#inspecting-profile-contents)
- [Creating a Custom Profile](#creating-a-custom-profile)
- [Verifying What tuned Applied](#verifying-what-tuned-applied)
- [Dynamic Tuning](#dynamic-tuning)
- [Recommend Profile with tuned-adm](#recommend-profile-with-tuned-adm)
- [Persistent Custom sysctl (Supplement to tuned)](#persistent-custom-sysctl-supplement-to-tuned)
- [Worked example — latency-sensitive application tuning](#worked-example-latency-sensitive-application-tuning)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)
- [Lab — Profile Switch and Verification](#lab-profile-switch-and-verification)
  - [Steps](#steps)
- [Recap](#recap)


## How tuned Works

```text
tuned daemon
  ├── reads /etc/tuned/tuned-main.conf
  ├── loads active profile from /etc/tuned/active_profile
  ├── applies settings via plugins (sysctl, disk, cpu, net, ...)
  └── monitors system and adjusts dynamically (if dynamic tuning enabled)
```

Profile directories:
- `/usr/lib/tuned/` — shipped profiles (read-only)
- `/etc/tuned/` — custom profiles (override or extend shipped ones)

Each profile is a directory containing at minimum a `tuned.conf` file.
The `[main]` section may include an `include=` directive to inherit from
another profile. The included profile's settings are applied first; the
inheriting profile's settings override them. This inheritance model allows
you to express "throughput-performance, plus these two extra tweaks"
without duplicating the base profile.


[↑ Back to TOC](#toc)

---

## Installing and Enabling tuned

```bash
# Install (usually pre-installed on RHEL 10)
$ sudo dnf install -y tuned

# Enable and start
$ sudo systemctl enable --now tuned

# Verify
$ sudo systemctl status tuned
Active: active (running)
```


[↑ Back to TOC](#toc)

---

## Listing and Selecting Profiles

```bash
# List all available profiles
$ tuned-adm list
Available profiles:
- accelerator-performance
- balanced
- desktop
- hpc-compute
- latency-performance
- network-latency
- network-throughput
- powersave
- throughput-performance
- virtual-guest
- virtual-host
Current active profile: virtual-guest
```

### Profile selection guide

| Profile | Use Case |
|---|---|
| `throughput-performance` | Batch workloads, databases; maximizes I/O and CPU throughput |
| `latency-performance` | Low-latency apps; disables power management, CPU frequency scaling |
| `network-latency` | Network-intensive; adjusts NIC ring buffers, IRQ coalescing |
| `network-throughput` | High-bandwidth transfers; large socket buffers |
| `virtual-guest` | Default for VMs; balances power and performance |
| `virtual-host` | KVM hypervisor hosts; enables THP, optimizes for guest I/O |
| `hpc-compute` | HPC / scientific computing; disables NUMA balancing overhead |
| `balanced` | Default for physical servers; adaptive power/performance |
| `powersave` | Energy-constrained environments; aggressive CPU throttling |

```bash
# Switch to a profile
$ sudo tuned-adm profile throughput-performance

# Verify the switch
$ tuned-adm active
Current active profile: throughput-performance

# Check what the profile actually sets
$ tuned-adm profile_info throughput-performance
```

> **Exam tip:** `tuned-adm recommend` outputs a profile name based on the
> detected hardware and virtualisation layer. Use it as a starting point,
> then customise. The recommended profile is not always the best choice for
> the specific workload.


[↑ Back to TOC](#toc)

---

## Inspecting Profile Contents

```bash
# Read the profile definition
$ cat /usr/lib/tuned/throughput-performance/tuned.conf
```

Example (abbreviated):

```ini
[main]
summary=Throughput performance based on Red Hat Enterprise Linux tuning

[cpu]
force_latency=cstate.id:1|3
governor=performance
energy_perf_bias=performance
min_perf_pct=100

[vm]
transparent_hugepages=always

[disk]
readahead=>4096

[sysctl]
kernel.sched_min_granularity_ns=10000000
kernel.sched_wakeup_granularity_ns=15000000
vm.dirty_ratio=40
vm.dirty_background_ratio=10
net.core.somaxconn=65536
net.core.rmem_max=16777216
net.core.wmem_max=16777216
```

Available `tuned.conf` plugins and what they configure:

| Plugin | Controls |
|---|---|
| `[cpu]` | CPU governor, frequency scaling, C-state latency |
| `[vm]` | Transparent Huge Pages, page clustering |
| `[disk]` | Read-ahead, I/O scheduler per device |
| `[sysctl]` | Kernel parameters (same as `/etc/sysctl.d/`) |
| `[net]` | NIC ring buffer sizes, IRQ coalescing |
| `[scheduler]` | Process scheduling policy, IRQ thread priorities |
| `[script]` | Custom shell scripts run on profile activate/deactivate |


[↑ Back to TOC](#toc)

---

## Creating a Custom Profile

Custom profiles live in `/etc/tuned/<profile-name>/tuned.conf`. The recommended approach is to **inherit** a base profile and override only what you need:

```bash
$ sudo mkdir /etc/tuned/rhca-web
$ sudo tee /etc/tuned/rhca-web/tuned.conf <<'EOF'
[main]
summary=RHCA lab - tuned profile for web server workloads
include=throughput-performance

[sysctl]
# Increase listen backlog for high-concurrency web
net.core.somaxconn=131072
net.ipv4.tcp_max_syn_backlog=65536

# Reduce TIME_WAIT socket accumulation
net.ipv4.tcp_tw_reuse=1
net.ipv4.tcp_fin_timeout=15

# File descriptor limits
fs.file-max=2097152

[vm]
transparent_hugepages=never

[disk]
# NVMe: use none scheduler; HDD: use mq-deadline
# scheduler= is applied per-device
EOF
```

```bash
# Activate your custom profile
$ sudo tuned-adm profile rhca-web

# Verify
$ tuned-adm active
Current active profile: rhca-web
```


[↑ Back to TOC](#toc)

---

## Verifying What tuned Applied

```bash
# Check current value of a sysctl that tuned should have set
$ sysctl net.core.somaxconn
net.core.somaxconn = 131072

# Verify CPU governor tuned set
$ cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
performance

# Transparent Huge Pages
$ cat /sys/kernel/mm/transparent_hugepage/enabled
always madvise [never]   ← 'never' is selected (bracketed)

# Disk read-ahead
$ blockdev --getra /dev/vda
8192   ← 4096 sectors × 512 bytes = 4096 kB
```


[↑ Back to TOC](#toc)

---

## Dynamic Tuning

tuned can monitor the system and adjust settings automatically (e.g., reduce CPU power during idle, boost during load spikes):

```bash
# Enable dynamic tuning globally
$ sudo sed -i 's/^#dynamic_tuning=0/dynamic_tuning=1/' /etc/tuned/tuned-main.conf

# Restart tuned to apply
$ sudo systemctl restart tuned

# Check sampling interval
$ grep update_interval /etc/tuned/tuned-main.conf
update_interval=10   # seconds
```

> **Caution:** Dynamic tuning can interfere with latency-sensitive workloads. Keep it disabled (`dynamic_tuning=0`) for `latency-performance` profiles.


[↑ Back to TOC](#toc)

---

## Recommend Profile with tuned-adm

tuned can analyze the system and suggest a profile:

```bash
$ sudo tuned-adm recommend
virtual-guest
```

Use this as a starting point — not necessarily the final choice.


[↑ Back to TOC](#toc)

---

## Persistent Custom sysctl (Supplement to tuned)

For settings that don't fit a tuned plugin, use drop-in files under `/etc/sysctl.d/`:

```bash
$ sudo tee /etc/sysctl.d/99-rhca-perf.conf <<'EOF'
# Increase inotify watches for large deployments
fs.inotify.max_user_watches=524288
fs.inotify.max_user_instances=512

# Disable IPv6 if not used (reduces kernel overhead)
net.ipv6.conf.all.disable_ipv6=1
net.ipv6.conf.default.disable_ipv6=1
EOF

# Apply immediately without reboot
$ sudo sysctl --system
```

> **Rule of thumb:** Use `tuned` for workload-level profiles; use `/etc/sysctl.d/` for site-specific tweaks. Never set both in a way that conflicts (tuned will win at activation time).


[↑ Back to TOC](#toc)

---

## Worked example — latency-sensitive application tuning

**Scenario:** A financial trading application runs on RHEL 10 on bare metal.
It processes market data with a strict 1ms latency budget. After initial
deployment, P99 latency is 4–6ms. The VM was provisioned with the default
`virtual-guest` profile (from an earlier VM image), but this is now a bare
metal host.

**Step 1 — assess current state**

```bash
tuned-adm active
# Current active profile: virtual-guest  ← wrong for bare metal

cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# powersave  ← CPU is throttling to save power

cat /sys/kernel/mm/transparent_hugepage/enabled
# [always] madvise never  ← THP enabled, causes latency spikes
```

**Step 2 — apply latency-performance**

```bash
sudo tuned-adm profile latency-performance

# Verify
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# performance  ← CPU now runs at full speed

cat /sys/kernel/mm/transparent_hugepage/enabled
# always madvise [never]  ← THP disabled

# Measure P99 latency after change (application-specific tool)
# P99 drops from 5.2ms to 1.8ms — closer to budget but still over
```

**Step 3 — create a custom profile with additional tuning**

```bash
sudo mkdir /etc/tuned/trading-latency
sudo tee /etc/tuned/trading-latency/tuned.conf <<'EOF'
[main]
summary=Trading application — minimum latency
include=latency-performance

[sysctl]
# Minimize scheduler granularity for tighter wakeup latency
kernel.sched_min_granularity_ns=1000000
kernel.sched_wakeup_granularity_ns=1500000

# Disable swap to prevent swap-in latency spikes
vm.swappiness=0

# Pin NIC interrupt handling (if using specific CPUs for network)
# Done via irqbalance or manual IRQ affinity — not a sysctl

[cpu]
force_latency=1         # Force CPU to shallowest C-state (C1) only
governor=performance

[vm]
transparent_hugepages=never

[net]
# Reduce NIC interrupt coalescing for lower receive latency
channels=combined 1     # single combined queue (if NIC supports it)
EOF

sudo tuned-adm profile trading-latency
```

**Step 4 — verify and measure**

```bash
tuned-adm active
# Current active profile: trading-latency

sysctl kernel.sched_min_granularity_ns
# kernel.sched_min_granularity_ns = 1000000

sysctl vm.swappiness
# vm.swappiness = 0

# Re-measure P99 latency
# P99 drops to 0.8ms — within 1ms budget
```

**Step 5 — automate via Ansible**

```yaml
- name: Apply trading-latency tuned profile
  ansible.builtin.command: tuned-adm profile trading-latency
  changed_when: false
```

> **Exam tip:** In the exam, demonstrating that you checked the current
> profile with `tuned-adm active` before switching shows systematic
> methodology. Always verify the change took effect with `tuned-adm active`
> and confirm the affected kernel parameter directly.


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Symptom | Likely Cause | Fix |
|---|---|---|
| `tuned-adm: command not found` | Package not installed | `sudo dnf install -y tuned` |
| Profile switch silently has no effect | tuned service not running | `sudo systemctl start tuned` |
| Custom profile not listed | Syntax error in `tuned.conf` | Check `journalctl -u tuned` |
| `include=` profile not found | Typo in base profile name | `tuned-adm list` to verify exact name |
| CPU governor stays at `powersave` after switch | CPU frequency scaling driver doesn't support governor change | Check `cpupower frequency-info` |
| Settings revert on reboot | Custom `/etc/sysctl.d/` file conflicts with tuned | Remove duplicates; let tuned own the knob |
| THP change not applied | tuned applied but kernel parameter not updated | Verify with `cat /sys/kernel/mm/transparent_hugepage/enabled`; check `journalctl -u tuned` for errors |
| `vm.swappiness=0` has no effect | Setting conflicts with tuned's `vm` plugin | Explicitly set `transparent_hugepages=` and `swappiness=` in the custom profile's `[vm]` section |


[↑ Back to TOC](#toc)

---

## Why This Matters in Production

A server running the wrong `tuned` profile can:

- Leave CPU in `powersave` mode, halving throughput under load
- Keep Transparent Huge Pages enabled for Redis or MongoDB (causing latency spikes and OOM behavior)
- Use default socket buffers that cannot sustain 10 GbE line rate

Setting the correct profile at provisioning time (via Ansible: `community.general.tuned` role or `command: tuned-adm profile`) eliminates an entire class of unexplained performance problems.

---


[↑ Back to TOC](#toc)

## Lab — Profile Switch and Verification

**Goal:** Switch to `latency-performance`, verify the CPU governor and THP change, then create a custom profile that inherits it.

**Estimated time:** 20 minutes

### Steps

```bash
# 1. Record current state
$ tuned-adm active
$ cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
$ cat /sys/kernel/mm/transparent_hugepage/enabled

# 2. Switch to latency-performance
$ sudo tuned-adm profile latency-performance

# 3. Verify changes
$ cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
performance
$ cat /sys/kernel/mm/transparent_hugepage/enabled
always madvise [never]

# 4. Create a custom profile based on latency-performance
$ sudo mkdir /etc/tuned/rhca-latency
$ sudo tee /etc/tuned/rhca-latency/tuned.conf <<'EOF'
[main]
summary=RHCA custom latency profile
include=latency-performance

[sysctl]
# Reduce scheduling latency
kernel.sched_min_granularity_ns=3000000
kernel.sched_wakeup_granularity_ns=4000000
EOF

# 5. Activate and verify
$ sudo tuned-adm profile rhca-latency
$ tuned-adm active
Current active profile: rhca-latency

$ sysctl kernel.sched_min_granularity_ns
kernel.sched_min_granularity_ns = 3000000
```

### Success criteria

- [ ] `tuned-adm active` shows `rhca-latency`
- [ ] CPU governor is `performance`
- [ ] THP is `never`
- [ ] `kernel.sched_min_granularity_ns` is `3000000`

### Cleanup

```bash
$ sudo tuned-adm profile virtual-guest   # or whatever was active before
$ sudo rm -rf /etc/tuned/rhca-latency
```

---


[↑ Back to TOC](#toc)

## Recap

| Task | Command |
|---|---|
| List profiles | `tuned-adm list` |
| Show active | `tuned-adm active` |
| Switch profile | `sudo tuned-adm profile <name>` |
| Recommend | `sudo tuned-adm recommend` |
| Show profile info | `tuned-adm profile_info <name>` |
| Create custom | `/etc/tuned/<name>/tuned.conf` with `include=` |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Monitoring and managing system status and performance](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/monitoring_and_managing_system_status_and_performance/index) | Official tuned, PCP, and sysctl tuning guide |
| [`tuned.conf` man page](https://man7.org/linux/man-pages/man5/tuned.conf.5.html) | Profile file format and available plugins |
| [`sysctl` man page](https://man7.org/linux/man-pages/man8/sysctl.8.html) | Runtime kernel parameter management |
| [Red Hat Performance Co-Pilot (PCP)](https://pcp.io/) | RHEL's observability framework for time-series performance data |

---


[↑ Back to TOC](#toc)

## Next step

→ [Recovery Patterns](03-recovery-patterns.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
