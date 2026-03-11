
[↑ Back to TOC](#toc)

# Volumes and Persistent Data
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Containers are ephemeral by default. Volumes and bind mounts let you persist
data across container restarts and replacements.

---
<a name="toc"></a>

## Table of contents

- [Types of storage in Podman](#types-of-storage-in-podman)
- [Named volumes](#named-volumes)
- [Bind mounts](#bind-mounts)
  - [Mount options](#mount-options)
- [tmpfs mounts](#tmpfs-mounts)
- [Data persistence patterns](#data-persistence-patterns)
  - [Pattern 1: Named volume for stateful service](#pattern-1-named-volume-for-stateful-service)
  - [Pattern 2: Bind mount for config injection](#pattern-2-bind-mount-for-config-injection)
- [Backup and restore volumes](#backup-and-restore-volumes)


## Types of storage in Podman

| Type | Description | Use case |
|---|---|---|
| **Named volume** | Managed by Podman, stored in container storage | Databases, app state |
| **Bind mount** | A host path mapped into the container | Config files, logs, dev mounts |
| **tmpfs** | In-memory, cleared on container stop | Sensitive temp data |


[↑ Back to TOC](#toc)

---

## Named volumes

```bash
# Create a volume
podman volume create mydata

# List volumes
podman volume ls

# Inspect
podman volume inspect mydata

# Use in a container
podman run -d --name db \
  -v mydata:/var/lib/mysql:Z \
  -e MYSQL_ROOT_PASSWORD=secret \
  mariadb:latest

# Remove a volume (only if not in use)
podman volume rm mydata

# Remove all unused volumes
podman volume prune
```


[↑ Back to TOC](#toc)

---

## Bind mounts

```bash
# Mount a host directory into the container
mkdir -p ~/myapp/data

podman run -d --name app \
  -v ~/myapp/data:/app/data:Z \
  myapp:latest
```

The `:Z` suffix is critical on RHEL — it sets the correct SELinux context
on the host directory for the container to access it. See [Container SELinux Gotchas](06-selinux-containers.md).

### Mount options

| Option | Meaning |
|---|---|
| `:ro` | Read-only |
| `:rw` | Read-write (default) |
| `:Z` | Relabel for SELinux (private, this container only) |
| `:z` | Relabel for SELinux (shared, multiple containers) |
| `:U` | Map UID/GID to container user |


[↑ Back to TOC](#toc)

---

## tmpfs mounts

```bash
podman run -d --name app \
  --tmpfs /app/tmp:rw,size=64m \
  myapp:latest
```

Contents of `/app/tmp` inside the container are in RAM and never touch disk.
Use for sensitive temporary files.


[↑ Back to TOC](#toc)

---

## Data persistence patterns

### Pattern 1: Named volume for stateful service

```bash
podman volume create pgdata

podman run -d \
  --name postgres \
  -v pgdata:/var/lib/postgresql/data:Z \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  postgres:16

# Update: stop, remove container, start new version — data survives
podman stop postgres
podman rm postgres
podman run -d \
  --name postgres \
  -v pgdata:/var/lib/postgresql/data:Z \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  postgres:16.1
```


[↑ Back to TOC](#toc)

---

### Pattern 2: Bind mount for config injection

```bash
mkdir -p ~/nginx/conf
cat > ~/nginx/conf/nginx.conf << 'EOF'
events {}
http {
  server {
    listen 8080;
    location / { root /usr/share/nginx/html; }
  }
}
EOF

podman run -d \
  --name nginx \
  -v ~/nginx/conf/nginx.conf:/etc/nginx/nginx.conf:ro,Z \
  -p 8080:8080 \
  nginx:latest
```


[↑ Back to TOC](#toc)

---

## Backup and restore volumes

```bash
# Backup a named volume
podman run --rm \
  -v mydata:/data:ro,Z \
  -v $(pwd):/backup:Z \
  ubi9 tar czf /backup/mydata-backup.tar.gz -C /data .

# Restore a volume
podman run --rm \
  -v mydata:/data:Z \
  -v $(pwd):/backup:ro,Z \
  ubi9 tar xzf /backup/mydata-backup.tar.gz -C /data
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Podman — Working with volumes](https://docs.podman.io/en/latest/markdown/podman-volume.1.html) | Volume create, inspect, and prune reference |
| [Podman — Bind mounts and SELinux](https://www.redhat.com/sysadmin/user-namespaces-selinux-rootless-containers) | Red Hat blog on `:z`/`:Z` and rootless bind mounts |
| [`podman-volume` man page](https://docs.podman.io/en/latest/markdown/podman-volume.1.html) | CLI reference for named volumes |

---


[↑ Back to TOC](#toc)

## Next step

→ [Podman Secrets](04-secrets.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
