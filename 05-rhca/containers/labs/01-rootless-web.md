
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab - Rootless Web Server with Quadlet
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

## Overview

Deploy a rootless Nginx container as a persistent systemd user service using a Quadlet `.container` file. The service survives reboots, restarts on failure, and runs entirely without root privileges.

**Track:** D — RHCA-style  
**Estimated time:** 45 minutes  
**Difficulty:** Intermediate


[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [Overview](#overview)
- [Background](#background)
- [Prerequisites](#prerequisites)
- [Success Criteria](#success-criteria)
- [Steps](#steps)
  - [1 — Prepare the user environment](#1-prepare-the-user-environment)
  - [2 — Create the content directory and a custom index page](#2-create-the-content-directory-and-a-custom-index-page)
  - [3 — Pull the image first (optional but recommended)](#3-pull-the-image-first-optional-but-recommended)
  - [4 — Create the Quadlet `.container` file](#4-create-the-quadlet-container-file)
  - [5 — Reload systemd and start the service](#5-reload-systemd-and-start-the-service)
  - [6 — Open the firewall port](#6-open-the-firewall-port)
  - [7 — Test from the host](#7-test-from-the-host)
  - [8 — Enable auto-start and reboot test](#8-enable-auto-start-and-reboot-test)
- [Verify Checkpoints](#verify-checkpoints)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)
- [Cleanup](#cleanup)
- [Why This Matters in Production](#why-this-matters-in-production)
- [Recap](#recap)


## Prerequisites

- RHEL 10 host with Podman installed
- A non-root user account (`student` used throughout)
- Lingering enabled for the user (`loginctl enable-linger student`)
- Port 8080 accessible (firewalld rule added in lab steps)

---


[↑ Back to TOC](#toc)

## Success Criteria

- [ ] Quadlet `.container` file created under `~/.config/containers/systemd/`
- [ ] `systemctl --user status nginx-web` shows **active (running)**
- [ ] `curl http://localhost:8080` returns the default Nginx page
- [ ] Service auto-starts after a full reboot (no manual intervention)
- [ ] Container runs as the student UID (verified with `podman ps`)

---


[↑ Back to TOC](#toc)

## Background

Quadlet is the RHEL 10–preferred way to run containers under systemd. You write
a declarative `.container` file; systemd generates the unit at runtime via the
`podman-user-generator` systemd generator. This replaces the older
`podman generate systemd` workflow and is the method tested on RHCA exams.

The key advantage of Quadlet over `podman generate systemd` is that the
`.container` file *is* the source of truth. If the file changes, a
`daemon-reload` picks up the new configuration immediately — no re-running
`podman run` and capturing new unit output. This makes the deployment
auditable and version-controllable.

Key path: `~/.config/containers/systemd/` for user-scoped services (no root
needed). Files placed here are picked up automatically by the user systemd
instance on `daemon-reload`. The generated service unit is named after the
file base name (e.g., `nginx-web.container` → `nginx-web.service`).

For the service to survive reboots and logouts without an active session,
**lingering** must be enabled. Linger causes the user's systemd instance to
start at boot time, independent of any login session. Without it, user services
run only while a session is active and stop when you disconnect.


[↑ Back to TOC](#toc)

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

> **Hint:** Without linger, the service runs only while you are logged in.
> All RHCA container exam tasks that ask for a "persistent" service require
> linger to be enabled.


[↑ Back to TOC](#toc)

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

> **Hint:** The `:Z` flag on the volume mount will relabel `~/nginx-web/html`
> with the container's SELinux MCS category. Verify with `ls -Z ~/nginx-web/html/`
> after the container starts.


[↑ Back to TOC](#toc)

---

### 3 — Pull the image first (optional but recommended)

```bash
$ podman pull docker.io/library/nginx:stable-alpine

# Verify the image is cached locally
$ podman images | grep nginx
docker.io/library/nginx  stable-alpine  ...
```

> **Hint:** Pre-pulling avoids a long first-start delay when systemd activates
> the service. On slow networks, the default `TimeoutStartSec` in the unit may
> expire before the image finishes downloading.


[↑ Back to TOC](#toc)

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
| `WantedBy=default.target` | Start automatically at user session start (with linger: at boot) |


[↑ Back to TOC](#toc)

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

> **Hint:** If the service fails to start, check the journal first:
> `journalctl --user -u nginx-web -n 50`. The most common cause at this
> stage is a misspelled image name.


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

---

### 7 — Test from the host

```bash
$ curl -s http://localhost:8080 | grep -o '<h1>.*</h1>'
<h1>Running rootless on RHEL 10</h1>

# Also test from a remote machine (replace IP accordingly)
$ curl -s http://192.168.122.10:8080 | grep -o '<h1>.*</h1>'
```


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

---

## Troubleshooting guide

| Symptom | Likely Cause | Diagnostic | Fix |
|---|---|---|---|
| `Failed to connect to bus` when running `systemctl --user` | `DBUS_SESSION_BUS_ADDRESS` not set | `echo $DBUS_SESSION_BUS_ADDRESS` | Run as the actual user in a proper session, not via `sudo -u student` |
| Service starts then stops immediately | Image pull failure or wrong image name | `journalctl --user -u nginx-web -n 50` | Check image name; pre-pull with `podman pull` |
| `curl` returns connection refused on 8080 | Port not published or firewalld blocking | `podman ps` (check port column); `firewall-cmd --list-ports` | Verify `PublishPort=8080:80` in `.container` file; add firewall rule |
| Content shows default Nginx page, not custom one | Volume mount path wrong | `systemctl --user show nginx-web \| grep ExecStart` | Verify `%h` expansion; check directory path |
| Permission denied on volume mount | SELinux label missing | `ls -Z ~/nginx-web/html/` | Ensure `:Z` is on the Volume directive; run `restorecon -Rv ~/nginx-web` |
| Service not running after reboot | Linger disabled | `loginctl show-user student \| grep Linger` | `sudo loginctl enable-linger student` |
| `systemctl --user list-unit-files` does not show nginx-web | Quadlet file not read by generator | Check file path and extension (must end in `.container`) | `systemctl --user daemon-reload`; verify file is in `~/.config/containers/systemd/` |
| Port 8080 accessible locally but not remotely | Firewall rule not persistent | `sudo firewall-cmd --list-ports` (no `--permanent`) | Re-add with `--permanent` and `--reload` |


[↑ Back to TOC](#toc)

---

## Extension tasks

### Extension 1 — Add a firewalld redirect from port 80 to 8080

Configure firewalld so external clients reach the container on port 80 even
though the rootless container listens on 8080.

```bash
sudo firewall-cmd --permanent \
  --add-forward-port=port=80:proto=tcp:toport=8080:toaddr=127.0.0.1
sudo firewall-cmd --reload

# Verify
curl http://localhost/    # port 80, redirected to 8080
```

Confirm masquerade is enabled (required for forwarding):
```bash
sudo firewall-cmd --query-masquerade || sudo firewall-cmd --add-masquerade --permanent
```

---

### Extension 2 — Add a Quadlet `.volume` file and reference it

Replace the direct bind mount with a Quadlet-managed named volume. Populate it
with the HTML content using a helper container.

```bash
# 1. Create the volume file
cat > ~/.config/containers/systemd/nginx-content.volume <<'EOF'
[Volume]
Label=app=nginx-web
EOF

# 2. Update the container file to use the volume
# Change: Volume=%h/nginx-web/html:/usr/share/nginx/html:Z,ro
# To:     Volume=nginx-content.volume:/usr/share/nginx/html:Z

# 3. Reload and populate the volume
systemctl --user daemon-reload

# Populate via a temporary container
podman run --rm \
  -v nginx-content.volume:/data:Z \
  -v ~/nginx-web/html:/source:ro,Z \
  ubi9 cp -r /source/. /data/

# 4. Start the service
systemctl --user start nginx-web
curl http://localhost:8080/
```

---

### Extension 3 — Enable auto-update and test it

Configure the container to auto-update when a new image is published.

```ini
# Add to [Container] section in nginx-web.container:
AutoUpdate=registry
```

```bash
systemctl --user daemon-reload
systemctl --user restart nginx-web

# Enable the auto-update timer
systemctl --user enable --now podman-auto-update.timer

# Simulate an update (dry-run)
podman auto-update --dry-run

# Check the timer schedule
systemctl --user list-timers | grep auto-update
```


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

## Why This Matters in Production

- **Attack surface reduction:** rootless containers cannot escalate to root even if the application is compromised.
- **Quadlet declarative model:** `.container` files are version-controllable and auditable — no transient shell commands to regenerate units.
- **Systemd lifecycle integration:** health checks, restart policies, rate limiting, and dependency ordering are all expressed natively in the unit, not in a wrapper script.
- **Separation of duty:** developers ship a container image; the `.container` file is the ops-owned deployment descriptor.

---


[↑ Back to TOC](#toc)

## Recap

You deployed an Nginx container as a rootless systemd user service using Quadlet. The deployment:

- Survives reboots via `WantedBy=default.target` and linger
- Is isolated from the host filesystem using a read-only, SELinux-labeled volume mount
- Respects RHEL 10 conventions: no `podman generate systemd`, no Docker socket, no root


[↑ Back to TOC](#toc)

---

## Next step

→ [Lab: Secrets Rotation](02-secrets-rotate.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
