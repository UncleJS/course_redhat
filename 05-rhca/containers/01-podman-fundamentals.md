
[↑ Back to TOC](#toc)

# Container Fundamentals — RHEL View
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Containers on RHEL use **Podman** — an OCI-compatible, daemonless container
engine that is the Red Hat default. Unlike Docker, Podman does not require a
root daemon.

---
<a name="toc"></a>

## Table of contents

- [Key concepts](#key-concepts)
- [Podman vs Docker](#podman-vs-docker)
- [Install Podman on RHEL 10](#install-podman-on-rhel-10)
- [Basic workflow](#basic-workflow)
- [Image management](#image-management)
- [Registry configuration](#registry-configuration)
- [Rootless vs rootful](#rootless-vs-rootful)


## Key concepts

| Term | Meaning |
|---|---|
| **OCI** | Open Container Initiative — standard for images and runtimes |
| **image** | Read-only template for a container (layers of filesystem changes) |
| **container** | Running instance of an image |
| **registry** | Server hosting images (quay.io, registry.access.redhat.com, docker.io) |
| **tag** | Version label for an image (e.g., `nginx:latest`, `nginx:1.25`) |
| **digest** | Immutable SHA-256 identifier for an image |
| **rootless** | Container running without root privileges (default on RHEL) |


[↑ Back to TOC](#toc)

---

## Podman vs Docker

| Feature | Podman | Docker |
|---|---|---|
| Root daemon required | No | Yes (dockerd) |
| Rootless containers | Native | Requires configuration |
| systemd integration | Native (`podman generate systemd`) | Via restart policies |
| SELinux integration | Native | Extra config required |
| Drop-in replacement | Nearly full CLI compatibility | — |
| RHEL support | Fully supported | Not in RHEL repos |


[↑ Back to TOC](#toc)

---

## Install Podman on RHEL 10

```bash
sudo dnf install -y podman
podman --version
```


[↑ Back to TOC](#toc)

---

## Basic workflow

```bash
# Search for an image
podman search nginx

# Pull an image
podman pull docker.io/library/nginx:latest

# List local images
podman images

# Run a container
podman run -d --name webtest -p 8080:80 nginx:latest

# List running containers
podman ps

# List all containers (including stopped)
podman ps -a

# View logs
podman logs webtest

# Execute a command inside a running container
podman exec -it webtest bash

# Stop and remove
podman stop webtest
podman rm webtest
```


[↑ Back to TOC](#toc)

---

## Image management

```bash
# Pull from Red Hat's registry (preferred on RHEL)
podman pull registry.access.redhat.com/ubi9/ubi

# Inspect image layers and metadata
podman inspect nginx:latest

# Remove an image
podman rmi nginx:latest

# Remove all unused images
podman image prune

# Tag an image
podman tag nginx:latest myregistry.example.com/nginx:1.0
```


[↑ Back to TOC](#toc)

---

## Registry configuration

RHEL configures trusted registries in `/etc/containers/registries.conf`:

```bash
cat /etc/containers/registries.conf
```

You can add unqualified search registries:

```toml
# /etc/containers/registries.conf.d/myregs.conf
[[registry]]
prefix = "myapp"
location = "myregistry.example.com"
```


[↑ Back to TOC](#toc)

---

## Rootless vs rootful

| Feature | Rootless | Rootful |
|---|---|---|
| Runs as | Your UID | root |
| Port binding < 1024 | Not allowed | Allowed |
| Host filesystem access | Mapped UIDs | Direct |
| SELinux considerations | User namespace mapping | Standard labels |

**Use rootless by default.** Switch to rootful (`sudo podman`) only when
specifically required (e.g., port 80 binding, direct device access).


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Podman documentation](https://docs.podman.io/en/latest/) | Official Podman CLI reference |
| [RHEL 10 — Building, running, and managing containers](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/building_running_and_managing_containers/index) | Official RHEL container guide |
| [OCI Image Specification](https://github.com/opencontainers/image-spec) | What a container image actually is |
| [Red Hat Container Catalog](https://catalog.redhat.com/software/containers/explore) | Certified UBI base images for RHEL |

---


[↑ Back to TOC](#toc)

## Next step

→ [Rootless Podman](02-rootless.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
