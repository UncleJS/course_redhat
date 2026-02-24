# Lab - Rootless Web Server with Quadlet

## Overview

Deploy a rootless Nginx container as a persistent systemd user service using a Quadlet `.container` file. The service survives reboots, restarts on failure, and runs entirely without root privileges.

**Track:** D — RHCA-style  
**Estimated time:** 45 minutes  
**Difficulty:** Intermediate

---

## Prerequisites

- RHEL 10 host with Podman installed
- A non-root user account (`student` used throughout)
- Lingering enabled for the user (`loginctl enable-linger student`)
- Port 8080 accessible (firewalld rule added in lab steps)

---

## Success Criteria

- [ ] Quadlet `.container` file created under `~/.config/containers/systemd/`
- [ ] `systemctl --user status nginx-web` shows **active (running)**
- [ ] `curl http://localhost:8080` returns the default Nginx page
- [ ] Service auto-starts after a full reboot (no manual intervention)
- [ ] Container runs as the student UID (verified with `podman ps`)

---

## Background

Quadlet is the RHEL 10–preferred way to run containers under systemd. You write a declarative `.container` file; systemd generates the unit at runtime. This replaces the older `podman generate systemd` workflow.

Key path: `~/.config/containers/systemd/` for user-scoped services (no root needed).

---

## Steps

### 1 — Prepare the user environment

```bash
# Confirm linger is on (service must survive logout)
$ loginctl show-user student | grep Linger
Linger=yes

# Enable it if not already set
$ sudo loginctl enable-linger student

# Confirm the XDG_RUNTIME_DIR is available
$ echo $XDG_RUNTIME_DIR
/run/user/1000
```

> **Why linger?** Without it, systemd user services are stopped when the last session for that user ends.

---

### 2 — Create the content directory and a custom index page

```bash
$ mkdir -p ~/nginx-web/html

$ cat > ~/nginx-web/html/index.html <<'EOF'
<!DOCTYPE html>
<html>
<head><title>RHCA Lab - Rootless Nginx</title></head>
<body>
  <h1>Running rootless on RHEL 10</h1>
  <p>Served by Nginx in a Podman container, managed by systemd via Quadlet.</p>
</body>
</html>
EOF
```

---

### 3 — Pull the image first (optional but recommended)

```bash
$ podman pull docker.io/library/nginx:stable-alpine

# Verify the image is cached locally
$ podman images | grep nginx
docker.io/library/nginx  stable-alpine  ...
```

> Pre-pulling avoids a long first-start delay when systemd activates the service.

---

### 4 — Create the Quadlet `.container` file

```bash
$ mkdir -p ~/.config/containers/systemd

$ cat > ~/.config/containers/systemd/nginx-web.container <<'EOF'
[Unit]
Description=Rootless Nginx web server (RHCA lab)
After=network-online.target

[Container]
Image=docker.io/library/nginx:stable-alpine
PublishPort=8080:80
Volume=%h/nginx-web/html:/usr/share/nginx/html:Z,ro
Environment=NGINX_ENTRYPOINT_QUIET_LOGS=1

[Service]
Restart=always
TimeoutStartSec=60

[Install]
WantedBy=default.target
EOF
```

Key annotations:

| Directive | Meaning |
|---|---|
| `PublishPort=8080:80` | Map host port 8080 → container port 80 |
| `Volume=...:Z,ro` | Mount content read-only; `:Z` sets private SELinux label |
| `%h` | Systemd specifier that expands to the user's home directory |
| `Restart=always` | Restart on any exit (crash, OOM, etc.) |

---

### 5 — Reload systemd and start the service

```bash
# Tell systemd to pick up the new Quadlet file
$ systemctl --user daemon-reload

# Confirm the generated unit was created
$ systemctl --user list-unit-files | grep nginx-web
nginx-web.service  generated

# Start the service
$ systemctl --user start nginx-web

# Verify it is running
$ systemctl --user status nginx-web
● nginx-web.service - Rootless Nginx web server (RHCA lab)
     Loaded: loaded (/home/student/.config/containers/systemd/nginx-web.container; generated)
     Active: active (running) since ...
```

---

### 6 — Open the firewall port

```bash
# Allow inbound traffic on port 8080
$ sudo firewall-cmd --add-port=8080/tcp --permanent
$ sudo firewall-cmd --reload

# Confirm the rule
$ sudo firewall-cmd --list-ports | grep 8080
8080/tcp
```

---

### 7 — Test from the host

```bash
$ curl -s http://localhost:8080 | grep -o '<h1>.*</h1>'
<h1>Running rootless on RHEL 10</h1>

# Also test from a remote machine (replace IP accordingly)
$ curl -s http://192.168.122.10:8080 | grep -o '<h1>.*</h1>'
```

---

### 8 — Enable auto-start and reboot test

```bash
# The [Install] section already sets WantedBy=default.target
# Enable the service so it starts at login/boot
$ systemctl --user enable nginx-web

# Reboot
$ sudo reboot
```

After reboot, log back in and verify:

```bash
$ systemctl --user status nginx-web
Active: active (running) ...

$ curl -s http://localhost:8080 | grep '<h1>'
<h1>Running rootless on RHEL 10</h1>
```

---

## Verify Checkpoints

```bash
# 1. Container is rootless (UID matches your user)
$ podman ps --format "{{.Names}} {{.Status}}"
systemd-nginx-web  Up X minutes

$ podman inspect systemd-nginx-web --format '{{.HostConfig.UsernsMode}}'
# (empty or "host" is expected for rootless with default userns)

# 2. No root-owned processes
$ ps -ef | grep nginx | grep -v grep
student  ...  nginx: master process ...

# 3. SELinux label on the content directory
$ ls -Z ~/nginx-web/html/
system_u:object_r:container_file_t:s0:cX,cY  index.html

# 4. Journal for the service
$ journalctl --user -u nginx-web -n 20
```

---

## Cleanup

```bash
# Stop and disable the service
$ systemctl --user stop nginx-web
$ systemctl --user disable nginx-web

# Remove the Quadlet file and reload
$ rm ~/.config/containers/systemd/nginx-web.container
$ systemctl --user daemon-reload

# Remove the content and image
$ rm -rf ~/nginx-web
$ podman rmi docker.io/library/nginx:stable-alpine

# Remove the firewall rule
$ sudo firewall-cmd --remove-port=8080/tcp --permanent
$ sudo firewall-cmd --reload
```

---

## Common Failures

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Failed to connect to bus` when running `systemctl --user` | `DBUS_SESSION_BUS_ADDRESS` not set | Run as the actual user in a proper session, not via `sudo -u student` |
| Service starts then stops immediately | Image pull failure or wrong image name | `journalctl --user -u nginx-web -n 50`; check image name |
| `curl` returns connection refused | Port not published or firewalld blocking | Verify `podman ps` shows the port mapping; check `firewall-cmd --list-ports` |
| Content shows default Nginx page, not custom one | Volume mount path wrong | Check `%h` expansion: `systemctl --user show nginx-web | grep ExecStart` |
| Permission denied on volume mount | SELinux label missing | Ensure `:Z` is on the volume directive; run `restorecon -Rv ~/nginx-web` |
| Service not running after reboot | Linger disabled | `sudo loginctl enable-linger student` |

---

## Why This Matters in Production

- **Attack surface reduction:** rootless containers cannot escalate to root even if the application is compromised.
- **Quadlet declarative model:** `.container` files are version-controllable and auditable — no transient shell commands to regenerate units.
- **Systemd lifecycle integration:** health checks, restart policies, rate limiting, and dependency ordering are all expressed natively in the unit, not in a wrapper script.
- **Separation of duty:** developers ship a container image; the `.container` file is the ops-owned deployment descriptor.

---

## Recap

You deployed an Nginx container as a rootless systemd user service using Quadlet. The deployment:

- Survives reboots via `WantedBy=default.target` and linger
- Is isolated from the host filesystem using a read-only, SELinux-labeled volume mount
- Respects RHEL 10 conventions: no `podman generate systemd`, no Docker socket, no root

---

## Next step

→ [Lab: Secrets Rotation](secrets-rotate.md)
