# tuned — Profile-Based System Tuning

## Overview

`tuned` is a systemd service that applies kernel parameter and device setting profiles appropriate for a given workload. On RHEL 10 it is the **first-line tuning tool** — apply the right profile before manually touching any `sysctl` knobs.

---

## How tuned Works

```
tuned daemon
  ├── reads /etc/tuned/tuned-main.conf
  ├── loads active profile from /etc/tuned/active_profile
  ├── applies settings via plugins (sysctl, disk, cpu, net, ...)
  └── monitors system and adjusts dynamically (if dynamic tuning enabled)
```

Profile directories:
- `/usr/lib/tuned/` — shipped profiles (read-only)
- `/etc/tuned/` — custom profiles (override or extend shipped ones)

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

---

## Recommend Profile with tuned-adm

tuned can analyze the system and suggest a profile:

```bash
$ sudo tuned-adm recommend
virtual-guest
```

Use this as a starting point — not necessarily the final choice.

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

---

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

## Common Failures

| Symptom | Likely Cause | Fix |
|---|---|---|
| `tuned-adm: command not found` | Package not installed | `sudo dnf install -y tuned` |
| Profile switch silently has no effect | tuned service not running | `sudo systemctl start tuned` |
| Custom profile not listed | Syntax error in `tuned.conf` | Check `journalctl -u tuned` |
| `include=` profile not found | Typo in base profile name | `tuned-adm list` to verify exact name |
| CPU governor stays at `powersave` after switch | CPU frequency scaling driver doesn't support governor change | Check `cpupower frequency-info` |
| Settings revert on reboot | Custom `/etc/sysctl.d/` file conflicts with tuned | Remove duplicates; let tuned own the knob |

---

## Why This Matters in Production

A server running the wrong `tuned` profile can:

- Leave CPU in `powersave` mode, halving throughput under load
- Keep Transparent Huge Pages enabled for Redis or MongoDB (causing latency spikes and OOM behavior)
- Use default socket buffers that cannot sustain 10 GbE line rate

Setting the correct profile at provisioning time (via Ansible: `community.general.tuned` role or `command: tuned-adm profile`) eliminates an entire class of unexplained performance problems.

---

## Recap

| Task | Command |
|---|---|
| List profiles | `tuned-adm list` |
| Show active | `tuned-adm active` |
| Switch profile | `sudo tuned-adm profile <name>` |
| Recommend | `sudo tuned-adm recommend` |
| Show profile info | `tuned-adm profile_info <name>` |
| Create custom | `/etc/tuned/<name>/tuned.conf` with `include=` |

Next: [Recovery Patterns](recovery-patterns.md)
