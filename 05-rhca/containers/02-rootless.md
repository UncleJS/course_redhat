# Rootless Podman — Storage and Networking
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Rootless containers are Podman's default and the correct way to run containers
on RHEL for most workloads.

---
<a name="toc"></a>

## Table of contents

- [How rootless works](#how-rootless-works)
- [User namespace mapping in practice](#user-namespace-mapping-in-practice)
- [Rootless storage](#rootless-storage)
- [Rootless networking](#rootless-networking)
  - [Port redirect for port 80 → 8080](#port-redirect-for-port-80-8080)
- [Rootless networking: container-to-container](#rootless-networking-container-to-container)
- [Inspect networking](#inspect-networking)
- [Clean up rootless storage](#clean-up-rootless-storage)


## How rootless works

Rootless containers use **user namespaces**: your UID is mapped to a range of
sub-UIDs inside the container, so root inside the container is not root on the
host.

```bash
# Check your sub-UID and sub-GID mappings
cat /etc/subuid | grep $(whoami)
cat /etc/subgid | grep $(whoami)
```

Expected: `rhel:100000:65536` — 65536 UIDs mapped starting at 100000.

If missing (fresh system):

```bash
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $(whoami)
```


[↑ Back to TOC](#toc)

---

## User namespace mapping in practice

Inside a rootless container:

```bash
podman run --rm alpine id
# uid=0(root) gid=0(root) — root INSIDE the container
```

On the host:

```bash
ps aux | grep "podman\|alpine"
# Process runs as YOUR UID — not root
```

Files created by root inside the container appear owned by a high UID on the host:

```bash
podman run --rm -v /tmp/test:/data:Z alpine sh -c "echo hello > /data/file"
ls -ln /tmp/test/file
# -rw-r--r-- 1 100000 100000 ...   (mapped UID on host)
```


[↑ Back to TOC](#toc)

---

## Rootless storage

Rootless containers store images and container data in:

```bash
~/.local/share/containers/storage/
```

```bash
# View storage usage
podman system df

# Inspect storage driver
podman info | grep -A5 store
```

RHEL defaults to the **overlay** storage driver using `~/.local/share/containers/`.


[↑ Back to TOC](#toc)

---

## Rootless networking

Rootless containers use **pasta** (RHEL 10) or **slirp4netns** for network
namespacing, which provides NAT-like networking.

```bash
# Run container with port mapping
podman run -d --name web -p 8080:80 nginx:latest

# Test
curl http://localhost:8080/
```

> **📝 Ports below 1024**
> Rootless containers cannot bind to ports below 1024 on the host.
> Use a port above 1024 (e.g., 8080) or set a redirect in firewalld.
>

### Port redirect for port 80 → 8080

```bash
sudo firewall-cmd --permanent \
  --add-forward-port=port=80:proto=tcp:toport=8080:toaddr=127.0.0.1
sudo firewall-cmd --reload
```


[↑ Back to TOC](#toc)

---

## Rootless networking: container-to-container

Containers in the same **pod** or **network** can communicate:

```bash
# Create a custom network
podman network create mynet

# Run containers on it
podman run -d --name app --network mynet myapp:latest
podman run -d --name db --network mynet mariadb:latest

# Container 'app' can reach 'db' by hostname
podman exec app ping -c 2 db
```


[↑ Back to TOC](#toc)

---

## Inspect networking

```bash
# List networks
podman network ls

# Inspect a network
podman network inspect mynet

# Show container IP
podman inspect web | grep IPAddress

# Show port mappings
podman port web
```


[↑ Back to TOC](#toc)

---

## Clean up rootless storage

```bash
# Remove stopped containers
podman container prune

# Remove unused images
podman image prune

# Remove everything unused (containers, images, volumes, networks)
podman system prune

# Full reset (dangerous — removes everything)
podman system reset
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Podman — Rootless containers](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md) | Official rootless setup and troubleshooting guide |
| [User namespaces (`user_namespaces` man page)](https://man7.org/linux/man-pages/man7/user_namespaces.7.html) | Kernel feature that makes rootless containers possible |
| [slirp4netns](https://github.com/rootless-containers/slirp4netns) | Userspace networking for rootless containers |

---

## Next step

→ [Volumes and Persistent Data](03-volumes.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
