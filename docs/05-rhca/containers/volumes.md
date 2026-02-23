# Volumes and Persistent Data

Containers are ephemeral by default. Volumes and bind mounts let you persist
data across container restarts and replacements.

---

## Types of storage in Podman

| Type | Description | Use case |
|---|---|---|
| **Named volume** | Managed by Podman, stored in container storage | Databases, app state |
| **Bind mount** | A host path mapped into the container | Config files, logs, dev mounts |
| **tmpfs** | In-memory, cleared on container stop | Sensitive temp data |

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
on the host directory for the container to access it. See [Container SELinux Gotchas](selinux-containers.md).

### Mount options

| Option | Meaning |
|---|---|
| `:ro` | Read-only |
| `:rw` | Read-write (default) |
| `:Z` | Relabel for SELinux (private, this container only) |
| `:z` | Relabel for SELinux (shared, multiple containers) |
| `:U` | Map UID/GID to container user |

---

## tmpfs mounts

```bash
podman run -d --name app \
  --tmpfs /app/tmp:rw,size=64m \
  myapp:latest
```

Contents of `/app/tmp` inside the container are in RAM and never touch disk.
Use for sensitive temporary files.

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

---

## Next step

→ [Podman Secrets](secrets.md)
