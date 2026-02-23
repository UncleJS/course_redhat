# Container Fundamentals — RHEL View

Containers on RHEL use **Podman** — an OCI-compatible, daemonless container
engine that is the Red Hat default. Unlike Docker, Podman does not require a
root daemon.

---

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

---

## Install Podman on RHEL 10

```bash
sudo dnf install -y podman
podman --version
```

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

---

## Next step

→ [Rootless Podman](rootless.md)
