
[↑ Back to TOC](#toc)

# Performance Resource Triage
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

## Overview

When a system is slow, the instinct is to immediately tune or add hardware. The disciplined approach is **triage first**: identify the constrained resource, confirm the bottleneck, then act. This chapter provides a repeatable triage workflow covering CPU, memory, disk I/O, and network.


[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [Overview](#overview)
- [The Triage Hierarchy](#the-triage-hierarchy)
- [Quick Assessment — First 60 Seconds](#quick-assessment-first-60-seconds)
  - [Reading Load Average](#reading-load-average)
- [CPU Triage](#cpu-triage)
  - [Identify CPU consumers](#identify-cpu-consumers)
  - [Distinguish user-space vs kernel-space](#distinguish-user-space-vs-kernel-space)
  - [Syscall overhead](#syscall-overhead)
  - [CPU throttling in containers / cgroups](#cpu-throttling-in-containers-cgroups)
- [Memory Triage](#memory-triage)
  - [Baseline memory usage](#baseline-memory-usage)
  - [Detect swapping](#detect-swapping)
  - [OOM kill history](#oom-kill-history)
  - [Memory overcommit settings](#memory-overcommit-settings)
- [Disk I/O Triage](#disk-io-triage)
  - [iostat — the primary tool](#iostat-the-primary-tool)
  - [Identify the process causing I/O](#identify-the-process-causing-io)
  - [Filesystem saturation](#filesystem-saturation)
  - [I/O scheduler](#io-scheduler)
- [Network Triage](#network-triage)
  - [Interface-level statistics](#interface-level-statistics)
  - [TCP retransmits and errors](#tcp-retransmits-and-errors)
  - [Bandwidth utilization](#bandwidth-utilization)
  - [Connection table saturation](#connection-table-saturation)
- [Putting It Together — Triage Worksheet](#putting-it-together-triage-worksheet)
- [Useful One-Liners Reference](#useful-one-liners-reference)
- [Recap](#recap)


## The Triage Hierarchy

```
Is the system responding?
  └── Yes → Are processes stuck or thrashing?
        └── Check CPU / Memory first
              └── High CPU? → Who owns it? System or user?
              └── High Memory? → Swapping? OOM events?
                    └── I/O wait high? → Disk bottleneck
                          └── Network issues? → Packet drops / retransmits
```

Start at the top. Fix the most constrained layer before optimizing anything else.


[↑ Back to TOC](#toc)

---

## Quick Assessment — First 60 Seconds

Run these in sequence when you first encounter a slow system:

```bash
# 1. Is the system reachable and how loaded?
$ uptime
 14:22:05 up 3 days, 2:14,  2 users,  load average: 8.21, 6.44, 4.12

# 2. What is consuming CPU and memory right now?
$ top -b -n 1 | head -20

# 3. Any OOM kills in recent history?
$ journalctl -k --since "1 hour ago" | grep -i oom

# 4. Disk I/O wait
$ iostat -x 1 3

# 5. Memory pressure
$ free -m

# 6. Network errors
$ ip -s link show ens3
```

### Reading Load Average

| Load average vs CPU count | Interpretation |
|---|---|
| Load < CPU count | System has headroom |
| Load ≈ CPU count | Fully utilized but not overloaded |
| Load > CPU count | Runqueue backed up; likely bottleneck |
| Load >> CPU count | Severe overload — expect process starvation |

```bash
# CPU count
$ nproc
4

# If load average is 8 on a 4-core system → 2× overloaded
```


[↑ Back to TOC](#toc)

---

## CPU Triage

### Identify CPU consumers

```bash
# Sort by CPU%, show top 10 processes
$ ps aux --sort=-%cpu | head -11

# More detailed: show threads, not just processes
$ top -H   # press 'H' in interactive top to toggle threads

# Per-CPU usage (useful for identifying single-threaded bottlenecks)
$ mpstat -P ALL 1 5
```

### Distinguish user-space vs kernel-space

```bash
$ vmstat 1 5
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 6  0      0 123456  12345 678901    0    0     0     2 1234 5678 72 15 12  1  0
```

| Column | Meaning |
|---|---|
| `us` | User-space CPU time |
| `sy` | Kernel/system CPU time |
| `id` | Idle |
| `wa` | I/O wait |
| `st` | Stolen time (relevant in VMs) |

**High `sy`:** kernel is busy — check for excessive syscalls, IRQ handling, or context switches.  
**High `us`:** application-level problem — identify the process.  
**High `wa`:** disk or NFS I/O is the real bottleneck, not CPU.

### Syscall overhead

```bash
# How many context switches per second?
$ vmstat 1 | awk '{print $12, $13}'
# columns: interrupts/s  context-switches/s

# Which process is making the most syscalls?
$ strace -c -p <PID>   # attach to running process, Ctrl+C to stop and see summary
```

### CPU throttling in containers / cgroups

```bash
# Is a container being CPU-throttled?
$ systemctl status <service>
# Look for: CPUQuota= in the unit

# cgroup v2 throttling stats
$ cat /sys/fs/cgroup/system.slice/<service.service>/cpu.stat
nr_throttled 1234
throttled_usec 5678000
```


[↑ Back to TOC](#toc)

---

## Memory Triage

### Baseline memory usage

```bash
$ free -m
              total        used        free      shared  buff/cache   available
Mem:           7823        4521         312         234        2990        2834
Swap:          2047          42        2005
```

> **`available`** is the most useful column — it includes reclaimable cache and shows how much memory a new process could actually get.

### Detect swapping

```bash
# Is the system actively swapping? (non-zero si/so is the concern)
$ vmstat 1 5 | awk 'NR>2 {print "swap-in:", $7, "swap-out:", $8}'

# Which processes have the most swap usage?
$ for pid in $(ls /proc | grep -E '^[0-9]+$'); do
    swap=$(awk '/VmSwap/{print $2}' /proc/$pid/status 2>/dev/null)
    [ -n "$swap" ] && [ "$swap" -gt 0 ] && \
      echo "$swap kB  $(cat /proc/$pid/comm 2>/dev/null) (PID $pid)"
  done | sort -rn | head -10
```

### OOM kill history

```bash
# Recent OOM kills from kernel ring buffer
$ journalctl -k | grep -E "oom|killed process" | tail -20

# Identify which cgroup was killed
$ journalctl -k | grep "oom_kill_process"
```

### Memory overcommit settings

```bash
$ sysctl vm.overcommit_memory vm.overcommit_ratio
vm.overcommit_memory = 0    # 0=heuristic, 1=always allow, 2=never overcommit
vm.overcommit_ratio = 50

# Committed virtual memory vs physical
$ cat /proc/meminfo | grep -E "CommitLimit|Committed_AS"
CommitLimit:    5963000 kB
Committed_AS:   4812000 kB
```


[↑ Back to TOC](#toc)

---

## Disk I/O Triage

### iostat — the primary tool

```bash
# Extended stats, 1-second interval, 5 iterations
$ iostat -x 1 5

Device            r/s     w/s     rkB/s     wkB/s  await  %util
vda              0.00   145.00      0.00  18560.00  45.23   98.2
```

| Column | Meaning | Concern threshold |
|---|---|---|
| `r/s` / `w/s` | Read/write operations per second | Depends on device |
| `await` | Average I/O wait time in ms | > 20ms for HDD, > 2ms for SSD |
| `%util` | Device utilization | > 80% sustained = bottleneck |
| `svctm` | Service time (deprecated but still present) | — |

### Identify the process causing I/O

```bash
# iotop: per-process I/O (requires root or CAP_NET_ADMIN)
$ sudo iotop -o -b -n 3 | head -20
# -o = only show processes doing I/O

# Alternative: pidstat
$ pidstat -d 1 5
# Shows per-process disk read/write rates
```

### Filesystem saturation

```bash
# Disk space
$ df -h

# Inode exhaustion (a full inode table looks like a full disk)
$ df -i
Filesystem       Inodes  IUsed   IFree IUse% Mounted on
/dev/vda3        524288 523900     388   99% /var/log   ← inode exhausted

# Find inode hogs
$ find /var/log -xdev -printf '%h\n' | sort | uniq -c | sort -rn | head -10
```

### I/O scheduler

```bash
# Current scheduler for each block device
$ cat /sys/block/vda/queue/scheduler
[none] mq-deadline kyber bfq

# For NVMe/SSDs, 'none' is typically optimal
# For HDDs, 'mq-deadline' reduces latency for sequential workloads
```


[↑ Back to TOC](#toc)

---

## Network Triage

### Interface-level statistics

```bash
# Errors, drops, overruns per interface
$ ip -s link show ens3
    RX: bytes  packets  errors  dropped missed  mcast
    ...        ...      0       12      0       0
    TX: bytes  packets  errors  dropped carrier collsns
    ...        ...      0       0       0       0

# Watch in real-time
$ watch -n 1 'ip -s link show ens3'
```

### TCP retransmits and errors

```bash
# Global TCP stats
$ ss -s
Total: 312
TCP:   45 (estab 18, closed 12, orphaned 0, timewait 12)

# Retransmit counters
$ netstat -s | grep -i retran
    3456 segments retransmitted

# Per-socket retransmit info
$ ss -ti | grep retrans
```

### Bandwidth utilization

```bash
# Install nload or use iftop for live bandwidth
$ sudo dnf install -y nload
$ sudo nload ens3

# Or use sar for historical data
$ sar -n DEV 1 10
```

### Connection table saturation

```bash
# Are we running out of ephemeral ports or conntrack entries?
$ sysctl net.ipv4.ip_local_port_range
net.ipv4.ip_local_port_range = 32768	60999

$ sysctl net.nf_conntrack_max net.netfilter.nf_conntrack_count
# If count is close to max, conntrack is saturated
```


[↑ Back to TOC](#toc)

---

## Putting It Together — Triage Worksheet

When responding to a performance issue, capture these data points before making changes:

```
Date/Time of investigation:
Reported symptom:

--- CPU ---
Load average (1/5/15):
CPU count:
Top CPU consumer (process + %):
us/sy/id/wa breakdown:

--- Memory ---
Total / Used / Available:
Swap used / active swapping (si/so):
Recent OOM kills (Y/N):

--- Disk ---
vda %util:
await (ms):
Top I/O process:
Disk space / inode usage:

--- Network ---
RX/TX errors or drops:
TCP retransmit rate:
Conntrack utilization:

--- Conclusion ---
Primary bottleneck:
Secondary bottleneck (if any):
Recommended action:
```


[↑ Back to TOC](#toc)

---

## Useful One-Liners Reference

```bash
# Top 10 memory-consuming processes
$ ps aux --sort=-%mem | head -11

# Processes in uninterruptible sleep (D state) — usually stuck on I/O
$ ps aux | awk '$8=="D"'

# Open file count per process
$ lsof | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# Listening ports and owning processes
$ ss -tlnp

# Which process has a specific port open?
$ ss -tlnp sport = :8080

# Interrupt distribution across CPUs
$ cat /proc/interrupts | sort -k2 -rn | head -20

# Huge pages (important for databases)
$ grep -E "HugePages|Hugepagesize" /proc/meminfo
```


[↑ Back to TOC](#toc)

---

## Recap

Effective performance triage is systematic: start with load average, identify the bottleneck layer (CPU → memory → disk → network), then zoom into the specific process or subsystem. **Never tune what you haven't measured.** Capture a before snapshot, make one change, measure again.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Brendan Gregg — Linux Performance](https://www.brendangregg.com/linuxperf.html) | The definitive performance tools map and methodology |
| [USE Method](https://www.brendangregg.com/usemethod.html) | Utilisation, Saturation, Errors — the systematic triage framework |
| [`sar` man page](https://man7.org/linux/man-pages/man1/sar.1.html) | System Activity Reporter — historical performance data |
| [*Systems Performance* by Brendan Gregg](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) | Essential book for RHCA-level performance work |

---


[↑ Back to TOC](#toc)

## Next step

→ [tuned Profiles and Kernel Parameter Tuning](02-tuned.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
