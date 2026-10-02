# Process Management — ps, kill, nice
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Finding, signaling, and prioritizing processes is core RHCSA work. You identify
CPU or memory hogs with `ps`/`top`, stop misbehaving tasks with `kill`/`pkill`,
and adjust scheduling with `nice`/`renice`. Pair this chapter with
[Resource Triage](../05-rhca/perf/01-resource-triage.md) for deeper production
diagnosis.

---
<a name="toc"></a>

## Table of contents

- [Inspect processes](#inspect-processes)
- [Signals and kill](#signals-and-kill)
- [pkill and killall](#pkill-and-killall)
- [Priority — nice and renice](#priority--nice-and-renice)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)
- [Further reading](#further-reading)
- [Next step](#next-step)


## Inspect processes

```bash
# Snapshot of all processes (BSD syntax)
ps aux | head

# Full listing (System V style)
ps -ef | head

# Find by name
pgrep -a sshd
pidof chronyd

# Interactive monitor (press q to quit)
top
# or: htop   # if installed
```

Useful `ps` columns: `USER`, `%CPU`, `%MEM`, `VSZ`/`RSS`, `STAT`, `COMMAND`.
State `D` is uninterruptible sleep (usually I/O) — see recovery chapter before
blindly `kill -9`.


[↑ Back to TOC](#toc)

---

## Signals and kill

```bash
# Default SIGTERM (15) — ask process to exit cleanly
kill 1234
kill -TERM 1234

# Hangup — often reloads daemons that handle SIGHUP
kill -HUP 1234

# SIGKILL (9) — cannot be caught; last resort
kill -9 1234
kill -KILL 1234

# List signal names
kill -l
```

> **Exam tip:** Prefer `SIGTERM` first. Use `SIGKILL` only when the process
> ignores TERM. Never `kill -9` a process stuck in `D` state hoping it will
> help — it will not until the underlying I/O completes.


[↑ Back to TOC](#toc)

---

## pkill and killall

```bash
# By process name pattern
pkill -TERM httpd
pkill -u student sleep

# killall requires exact name (more precise than loose pkill patterns)
killall -TERM firefox
```


[↑ Back to TOC](#toc)

---

## Priority — nice and renice

Niceness ranges from **-20** (highest priority) to **19** (lowest). Default
new processes usually start at `0`. Only root can lower niceness (raise
priority).

```bash
# Start a command with lower priority (higher nice number)
nice -n 10 tar czf /tmp/big.tar.gz /var/log

# Change a running process
renice -n 15 -p 1234
sudo renice -n -5 -p 1234   # raise priority (root)
```


[↑ Back to TOC](#toc)

---

## Worked example

Find a runaway `dd` (or similar), terminate it, and start a backup at low
priority:

```bash
pgrep -a dd
# Suppose PID 4321
kill -TERM 4321
sleep 2
ps -p 4321 || echo "stopped"

nice -n 15 tar czf /tmp/home-backup.tar.gz -C /home student
ps -o pid,ni,cmd -C tar
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| `kill -9` first | No chance to flush / clean up | Try TERM, then KILL |
| Wrong PID | Unrelated process dies | Confirm with `ps -p` / `pgrep -a` |
| `renice -5` as user | "Permission denied" | Only root can decrease nice |
| `pkill http` matches too much | Extra processes die | Use exact name or `pgrep` first |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`kill` man page](https://man7.org/linux/man-pages/man1/kill.1.html) | Signals |
| [`nice` / `renice`](https://man7.org/linux/man-pages/man1/nice.1.html) | Priority |
| [Resource Triage](../05-rhca/perf/01-resource-triage.md) | CPU/mem/IO diagnosis |


[↑ Back to TOC](#toc)

---

## Next step

→ [NFS and automount](16-nfs-automount.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
