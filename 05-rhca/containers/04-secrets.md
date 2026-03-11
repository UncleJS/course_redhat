
[↑ Back to TOC](#toc)

# Podman Secrets — Create, Use, Rotate
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Podman secrets let you inject sensitive data (passwords, API keys, TLS
certs) into containers at runtime without:

- Hardcoding values in `podman run` commands
- Storing credentials in environment variables (visible via `podman inspect`)
- Committing secrets to image layers

---
<a name="toc"></a>

## Table of contents

- [How secrets work](#how-secrets-work)
- [Create secrets](#create-secrets)
- [List and inspect secrets](#list-and-inspect-secrets)
- [Use a secret in a container](#use-a-secret-in-a-container)
  - [Mount with a custom path or name](#mount-with-a-custom-path-or-name)
- [Multiple secrets](#multiple-secrets)
- [Secret rotation pattern](#secret-rotation-pattern)
- [Secrets with systemd-managed containers](#secrets-with-systemd-managed-containers)
- [Rootless secret storage location](#rootless-secret-storage-location)
- [Security considerations](#security-considerations)


## How secrets work

A secret is stored in Podman's secret store and mounted into the container
as a file at `/run/secrets/<name>`. The application reads it from disk.

```
host secret store → container /run/secrets/db_password (read-only file)
```


[↑ Back to TOC](#toc)

---

## Create secrets

```bash
# From stdin (recommended — doesn't leave secret in shell history)
printf 'supersecretpassword' | podman secret create db_password -

# From a file
podman secret create db_password /path/to/password.txt

# From an environment variable (use carefully — may appear in process list)
echo "${DB_PASSWORD}" | podman secret create db_password -
```


[↑ Back to TOC](#toc)

---

## List and inspect secrets

```bash
# List secrets (metadata only — values are never shown)
podman secret ls

# Inspect (metadata only)
podman secret inspect db_password
```

The secret value is **never** returned by `podman secret inspect`.


[↑ Back to TOC](#toc)

---

## Use a secret in a container

```bash
podman run -d \
  --name myapp \
  --secret db_password \
  myapp:latest
```

Inside the container, the secret is available as:

```
/run/secrets/db_password
```

Read it in your application:

```bash
# Shell example
DB_PASS=$(cat /run/secrets/db_password)

# Python
with open('/run/secrets/db_password') as f:
    db_pass = f.read().strip()
```

### Mount with a custom path or name

```bash
podman run -d \
  --name myapp \
  --secret db_password,target=/etc/myapp/db.passwd,mode=0400 \
  myapp:latest
```


[↑ Back to TOC](#toc)

---

## Multiple secrets

```bash
printf 'mydbpassword' | podman secret create db_password -
printf 'myapikey12345' | podman secret create api_key -

podman run -d \
  --name myapp \
  --secret db_password \
  --secret api_key \
  myapp:latest
```


[↑ Back to TOC](#toc)

---

## Secret rotation pattern

Podman does not support updating a secret in-place. The correct pattern:

```bash
# 1. Create the new version
printf 'newsecretpassword' | podman secret create db_password_v2 -

# 2. Stop and remove the old container
podman stop myapp
podman rm myapp

# 3. Start a new container with the new secret
podman run -d \
  --name myapp \
  --secret db_password_v2,target=db_password \
  myapp:latest

# 4. Verify the app is working with the new secret
curl http://localhost:8080/health

# 5. Remove the old secret
podman secret rm db_password
```

> **💡 Rotation with zero-downtime**
> For zero-downtime rotation, start the new container first (different name
> or port), verify it works, switch traffic (e.g., update firewall redirect),
> then stop the old container.
>


[↑ Back to TOC](#toc)

---

## Secrets with systemd-managed containers

Never put secrets in systemd unit environment variables — they appear in
`systemctl show` and `ps -e`.

Instead, mount the secret in the container unit:

```ini
[Service]
ExecStart=podman run \
  --name myapp \
  --secret db_password \
  --replace \
  myapp:latest
```

The secret value stays inside Podman's store, never in the unit file.


[↑ Back to TOC](#toc)

---

## Rootless secret storage location

```bash
# Rootless: secrets stored per-user
ls ~/.local/share/containers/storage/secrets/
```

The secret data is stored on disk (not in memory). File permissions restrict
access to your UID. On a shared host, each user's secrets are isolated.


[↑ Back to TOC](#toc)

---

## Security considerations

| Practice | Why |
|---|---|
| Never use `--env` for passwords | Visible in `podman inspect` and `ps -e` |
| Use `mode=0400` on secret mounts | Application should only read, not write |
| Rotate secrets regularly | Limits exposure window if compromised |
| Use `printf` not `echo` for creating secrets | `echo` adds a trailing newline |
| Remove old secrets after rotation | No stale credentials in the store |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`podman-secret` man page](https://docs.podman.io/en/latest/markdown/podman-secret.1.html) | Full secrets management command reference |
| [RHEL 10 — Using secrets in containers](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/building_running_and_managing_containers/index) | Official secrets usage guide |
| [HashiCorp Vault](https://www.vaultproject.io/) | Enterprise-grade secrets manager — common in production environments alongside Podman |

---


[↑ Back to TOC](#toc)

## Next step

→ [systemd-Managed Containers](05-systemd-integration.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
