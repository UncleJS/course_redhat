
[↑ Back to TOC](#toc)

# Volumes and Persistent Data
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Containers are ephemeral by default. Volumes and bind mounts let you persist
data across container restarts and replacements.

At RHCA level, the distinction between the three storage types is not just
academic — the wrong choice causes either data loss, SELinux permission
failures, or security incidents. Named volumes are the right default for
stateful services: Podman manages their location and SELinux labels
automatically. Bind mounts are the right choice for injecting configuration
or accessing logs from the host. `tmpfs` mounts are the right choice for
sensitive temporary data that must never reach disk.

The most common exam pitfall with volumes is SELinux. A bind-mounted host
directory retains its host SELinux type (`user_home_t`, `etc_t`, etc.). The
container process runs as `container_t` and the SELinux policy does not allow
`container_t` to read or write files labeled with host types. The `:Z` and
`:z` suffixes on the volume mount invoke `chcon` on the host path, changing
its type to `container_file_t` so the container can access it. Forgetting
`:Z` is the single most common cause of silent "permission denied" errors in
container volume mounts on RHEL.

For rootless containers, there is an additional UID mapping concern. The
container process runs as UID 0 inside the namespace but the kernel maps
this to a sub-UID on the host (e.g., 100000). If the host directory is owned
by your login UID (1000) rather than the sub-UID (100000), the container
cannot write to it. Use `:U` to have Podman remap the directory's ownership
automatically, or `chown` the directory to the sub-UID before mounting.

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
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## Types of storage in Podman

| Type | Description | Use case |
|---|---|---|
| **Named volume** | Managed by Podman, stored in container storage | Databases, app state |
| **Bind mount** | A host path mapped into the container | Config files, logs, dev mounts |
| **tmpfs** | In-memory, cleared on container stop | Sensitive temp data |

Named volumes are the safest default because:
- Podman sets the correct SELinux context automatically (`container_file_t`)
- They are isolated from the host filesystem — only containers can access them
  via `podman run -v`
- They survive `podman container prune` but not `podman volume prune`


[↑ Back to TOC](#toc)

---

## Named volumes

```bash
# Create a volume
podman volume create mydata

# List volumes
podman volume ls

# Inspect (find the mountpoint on the host)
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

The actual data lives at the path shown by `podman volume inspect mydata`
under `Mountpoint` — typically
`~/.local/share/containers/storage/volumes/mydata/_data/` for rootless.


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
| `:exec` | Allow execution of binaries in the mount |
| `:noexec` | Prevent execution of binaries (security hardening) |

Options can be combined: `-v ~/myapp/data:/app/data:ro,Z`

> **Exam tip:** The `:z` flag relabels with a shared label — multiple
> containers can access the directory. The `:Z` flag uses a private label —
> only one container. Use `:Z` for single-container bind mounts.


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

The `size=` parameter limits how much RAM the tmpfs can consume. Without it,
the default is 50% of RAM — potentially causing OOM issues on small hosts.

```bash
# Multiple tmpfs mounts
podman run -d --name app \
  --tmpfs /app/tmp:rw,size=64m,mode=1777 \
  --tmpfs /app/sessions:rw,size=32m \
  myapp:latest
```


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

Read-only bind mounts (`:ro,Z`) are the correct pattern for configuration
injection — the container cannot accidentally overwrite its own config.


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

This pattern uses a disposable container as a data-mover — the backup happens
inside the container so SELinux contexts are handled correctly for both source
and destination mounts.


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** Run a PostgreSQL container with a named volume so the database
survives container recreation. Verify data persistence.

```bash
# 1. Create the volume
podman volume create pgdata

# 2. Start PostgreSQL
podman run -d \
  --name pgtest \
  -v pgdata:/var/lib/postgresql/data:Z \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=myapp \
  -p 5432:5432 \
  docker.io/library/postgres:16-alpine

# 3. Wait for it to be ready
sleep 5
podman logs pgtest | tail -5

# 4. Create a test table and insert data
podman exec -it pgtest psql -U postgres -d myapp -c \
  "CREATE TABLE items (id SERIAL PRIMARY KEY, name TEXT);"

podman exec -it pgtest psql -U postgres -d myapp -c \
  "INSERT INTO items (name) VALUES ('widget'), ('gadget');"

# 5. Verify data exists
podman exec pgtest psql -U postgres -d myapp -c "SELECT * FROM items;"

# 6. Destroy the container (NOT the volume)
podman stop pgtest && podman rm pgtest

# 7. Confirm the volume still exists
podman volume ls | grep pgdata

# 8. Start a new container version with the same volume
podman run -d \
  --name pgtest2 \
  -v pgdata:/var/lib/postgresql/data:Z \
  -e POSTGRES_PASSWORD=testpass \
  -p 5432:5432 \
  docker.io/library/postgres:16-alpine

# 9. Verify data survived container recreation
sleep 5
podman exec pgtest2 psql -U postgres -d myapp -c "SELECT * FROM items;"
# Should return: widget, gadget

# 10. Check the volume SELinux label (Podman sets it correctly for named volumes)
ls -Z $(podman volume inspect pgdata --format '{{.Mountpoint}}')
# system_u:object_r:container_file_t:s0

# 11. Clean up
podman stop pgtest2 && podman rm pgtest2
podman volume rm pgdata
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

**1. Forgetting `:Z` on bind mounts — silent permission denied**

Symptom: container starts but application logs show "permission denied" on
its data directory; `podman logs` shows I/O errors.

Fix:
```bash
ls -Z ~/myapp/data    # should show container_file_t
# If it shows user_home_t or similar, re-run with :Z
podman stop app && podman rm app
podman run -d -v ~/myapp/data:/app/data:Z myapp:latest
```

---

**2. Using `:Z` on the entire home directory**

Symptom: after running a container with `-v ~:/home/user:Z`, the host user
cannot log in or access files; SELinux denials in audit log.

Fix:
```bash
# Restore home directory labels
sudo restorecon -Rv ~
# Never use :Z on ~, /etc, /var — only on subdirectories
```

---

**3. Named volume has no data after container recreation**

Symptom: new container starts but database is empty.

Diagnosis:
```bash
podman volume ls           # is the volume still there?
podman volume inspect pgdata | grep Mountpoint
ls -la <mountpoint>        # is data actually in the volume?
# Check: was the SAME volume name used in the new run command?
```

---

**4. rootless container cannot write to bind-mounted directory**

Symptom: `:Z` is set but writes still fail; `ls -Z` shows correct SELinux type.

Fix: this is a UID mapping issue, not SELinux:
```bash
# Find the sub-UID that the container's root maps to
awk -F: '/^student/{print $2}' /etc/subuid   # e.g., 100000
ls -ln ~/myapp/data   # if owned by 1000, container UID 0 cannot write
sudo chown -R 100000:100000 ~/myapp/data
# Or use :U option:
podman run -v ~/myapp/data:/app/data:Z,U myapp:latest
```

---

**5. Volume not removed by `podman container prune`**

Symptom: `podman system df` still shows volume disk usage after pruning containers.

Fix: this is expected behavior — volumes must be pruned separately:
```bash
podman volume prune    # removes volumes not currently attached to any container
# Or to remove a specific volume:
podman volume rm mydata
```

---

**6. `tmpfs` fills up and crashes the container**

Symptom: container exits with OOM or "no space left on device" inside `/app/tmp`.

Fix: always set an explicit `size=` limit on tmpfs mounts:
```bash
--tmpfs /app/tmp:rw,size=128m
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
