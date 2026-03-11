
[↑ Back to TOC](#toc)

# systemd-Managed Containers
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Running containers as systemd services gives you automatic start on boot,
restart on failure, journald logging, and integration with `systemctl`.

---
<a name="toc"></a>

## Table of contents

- [Two approaches](#two-approaches)
- [Approach 1: Quadlet (recommended for RHEL 10)](#approach-1-quadlet-recommended-for-rhel-10)
  - [Rootless container (user service)](#rootless-container-user-service)
  - [System-level rootful container](#system-level-rootful-container)
- [Quadlet file types](#quadlet-file-types)
  - [Manage a volume with Quadlet](#manage-a-volume-with-quadlet)
- [Approach 2: podman generate systemd](#approach-2-podman-generate-systemd)
- [Auto-update with Podman](#auto-update-with-podman)
- [Lingering (keep user services running after logout)](#lingering-keep-user-services-running-after-logout)


## Two approaches

| Approach | How | Best for |
|---|---|---|
| **Quadlet** (RHEL 10 default) | Declare containers in `.container` unit files | New workloads — simpler, declarative |
| **podman generate systemd** | Generate unit file from a running container | Migrating existing containers |


[↑ Back to TOC](#toc)

---

## Approach 1: Quadlet (recommended for RHEL 10)

Quadlet is a systemd generator built into Podman. You write a `.container`
file and systemd handles the rest.

### Rootless container (user service)

```bash
mkdir -p ~/.config/containers/systemd/
```

```ini
# ~/.config/containers/systemd/webserver.container

[Unit]
Description=My Web Server
After=network-online.target

[Container]
Image=nginx:latest
PublishPort=8080:80
Volume=%h/webdata:/usr/share/nginx/html:Z
Secret=tls_cert,target=/etc/nginx/certs/tls.crt
Environment=NGINX_HOST=localhost
Label=app=webserver

[Service]
Restart=always
TimeoutStartSec=30

[Install]
WantedBy=default.target
```

```bash
# Reload systemd user daemon to pick up new file
systemctl --user daemon-reload

# Start and enable the service
systemctl --user enable --now webserver.service

# Check status
systemctl --user status webserver.service

# View logs
journalctl --user -u webserver.service -f
```

### System-level rootful container

```bash
sudo mkdir -p /etc/containers/systemd/
sudo vim /etc/containers/systemd/nginx.container
```

```ini
[Unit]
Description=Nginx Web Server
After=network-online.target

[Container]
Image=docker.io/library/nginx:latest
PublishPort=80:80
Volume=/srv/webroot:/usr/share/nginx/html:Z
Secret=tls_cert

[Service]
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nginx.service
```


[↑ Back to TOC](#toc)

---

## Quadlet file types

| Extension | What it manages |
|---|---|
| `.container` | A container |
| `.volume` | A named volume |
| `.network` | A Podman network |
| `.pod` | A Podman pod |
| `.image` | An image pull |

### Manage a volume with Quadlet

```ini
# ~/.config/containers/systemd/dbdata.volume
[Volume]
Label=app=mydb
```

Reference it in the container file:

```ini
Volume=dbdata.volume:/var/lib/mysql:Z
```


[↑ Back to TOC](#toc)

---

## Approach 2: podman generate systemd

For containers already running, generate a unit file:

```bash
# Generate for an existing container
podman generate systemd --new --name myapp > myapp.service

# Review the file
cat myapp.service

# Install it
cp myapp.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now myapp.service
```

`--new` regenerates the container from scratch on each start (preferred over
starting an existing container).


[↑ Back to TOC](#toc)

---

## Auto-update with Podman

Podman can automatically update containers to newer image digests:

```ini
# In the .container file:
[Container]
AutoUpdate=registry
```

```bash
# Enable the auto-update timer
systemctl --user enable --now podman-auto-update.timer

# Or trigger manually
podman auto-update
```


[↑ Back to TOC](#toc)

---

## Lingering (keep user services running after logout)

By default, user services stop when you log out. Enable lingering for services
that must run 24/7:

```bash
sudo loginctl enable-linger $(whoami)
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Quadlet documentation](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) | Full `.container` file directive reference |
| [Podman — Quadlet tutorial](https://www.redhat.com/sysadmin/quadlet-podman) | Red Hat blog walkthrough of Quadlet-based deployments |
| [`systemd.unit` man page](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html) | Unit dependency model referenced by Quadlet |

---


[↑ Back to TOC](#toc)

## Next step

→ [Container SELinux Gotchas](06-selinux-containers.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
