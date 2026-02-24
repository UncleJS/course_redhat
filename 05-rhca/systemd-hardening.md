# systemd Hardening Knobs — Service Sandboxing

systemd provides service-level sandboxing directives that limit what a service
can do — without SELinux and without containers. These are defence-in-depth
controls that reduce the blast radius if a service is compromised.

---

## Why sandbox services?

Even with SELinux enforcing, reducing a service's capabilities at the systemd
level provides an additional layer:

- Limits filesystem visibility
- Prevents privilege escalation
- Restricts system call surface
- Limits network access

---

## Key hardening directives

### User and group

```ini
[Service]
User=myapp
Group=myapp
```

Run the service as a dedicated unprivileged user, not root.

---

### Filesystem restrictions

```ini
[Service]
# Protect the entire filesystem as read-only
ProtectSystem=strict

# Make /home and /root inaccessible
ProtectHome=true

# Writable runtime directory (auto-created as /run/myapp)
RuntimeDirectory=myapp
RuntimeDirectoryMode=0750

# Writable state directory (persistent, /var/lib/myapp)
StateDirectory=myapp

# Writable log directory (/var/log/myapp)
LogsDirectory=myapp

# Writable cache (/var/cache/myapp)
CacheDirectory=myapp
```

With `ProtectSystem=strict` and the above directories, the service can only
write to its designated directories.

---

### Private /tmp

```ini
[Service]
PrivateTmp=true
```

The service gets its own private `/tmp`. Files there are invisible to other
services and cleaned up when the service stops.

---

### Network restrictions

```ini
[Service]
# No network access at all
PrivateNetwork=true

# Or restrict to specific address families
RestrictAddressFamilies=AF_INET AF_INET6

# Block all socket creation
RestrictAddressFamilies=none
```

---

### Capabilities

Linux capabilities break root's all-or-nothing model into granular
permissions. Drop all capabilities and add only what's needed:

```ini
[Service]
# Drop all capabilities
CapabilityBoundingSet=

# If the service needs to bind to port < 1024:
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE
```

---

### Prevent privilege escalation

```ini
[Service]
NoNewPrivileges=true
```

Prevents `setuid` binaries and `execve` privilege escalation within the service.

---

### System call filtering

```ini
[Service]
# Allow only typical server syscalls
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

# Strict syscall sets:
SystemCallFilter=@basic-io @file-system @network-io @process
```

Syscall groups (`@system-service`, `@basic-io`, etc.) are pre-defined sets.
View available groups:

```bash
systemd-analyze syscall-filter
```

---

### Protect kernel and host configuration

```ini
[Service]
ProtectKernelTunables=true    # /proc/sys, /sys read-only
ProtectKernelModules=true     # cannot load/unload kernel modules
ProtectKernelLogs=true        # cannot read kernel ring buffer
ProtectControlGroups=true     # cgroup filesystem read-only
ProtectClock=true             # cannot set system clock
ProtectHostname=true          # cannot change hostname
```

---

## Full example: hardened web service

```ini
[Unit]
Description=Hardened Web Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=webapp
Group=webapp
ExecStart=/usr/local/bin/webapp --port 8080

# Filesystem
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
StateDirectory=webapp
LogsDirectory=webapp

# Privileges
NoNewPrivileges=true
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE

# Syscalls
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

# Kernel
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
ProtectClock=true
ProtectHostname=true

# Network
RestrictAddressFamilies=AF_INET AF_INET6

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

---

## Verify restrictions with systemd-analyze security

```bash
# Score a service (lower = more secure)
systemd-analyze security sshd.service
systemd-analyze security myapp.service
```

This gives a security score and a list of hardening improvements available.

---

## Next step

→ [Journald Retention and Forwarding](journald-retention.md)
