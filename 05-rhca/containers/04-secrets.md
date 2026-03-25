
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

At RHCA level, secrets management is a security and operational discipline, not
just a convenience. Environment variables are the most common way credentials
leak: they appear in `podman inspect`, `ps -e` output, application crash dumps,
and container logs. The Podman secrets mechanism avoids all of these by mounting
the secret as a read-only file inside the container's `/run/secrets/`
directory — a `tmpfs` mount that exists only in the container's filesystem
namespace and is never visible on the host as a regular file.

The mental model: a secret is a named blob of bytes stored in Podman's secret
backend (a JSON file on disk, encrypted at rest, accessible only by the owning
UID for rootless). At container start, Podman mounts the secret value into the
container as a read-only file. The application reads it from disk, like a
config file. The value never appears on the command line, in environment
variables, or in any `ps` output.

Secret **rotation** in Podman requires creating a new secret with a new name
and restarting the container. Podman does not support updating a secret
in-place. Use the `target=` option to keep the in-container path constant
across rotations — the application sees the same path regardless of the
underlying Podman secret name. This is the production-grade pattern that
allows rotation without application code changes.

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
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## How secrets work

A secret is stored in Podman's secret store and mounted into the container
as a file at `/run/secrets/<name>`. The application reads it from disk.

```text
host secret store → container /run/secrets/db_password (read-only file)
```

The mount is a `tmpfs` inside the container's mount namespace — it exists in
memory only during the container's lifetime and is not stored in the container
layer or any persistent filesystem.


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

# Create with specific driver (default: file)
printf 'supersecretpassword' | podman secret create --driver file db_password -
```

> **Why `printf` not `echo`?** `echo` appends a trailing `\n`. That newline
> becomes part of the secret value and causes authentication failures with most
> databases and APIs. Always use `printf`.


[↑ Back to TOC](#toc)

---

## List and inspect secrets

```bash
# List secrets (metadata only — values are never shown)
podman secret ls

# Inspect (metadata only)
podman secret inspect db_password

# Inspect with custom format
podman secret inspect --format '{{.ID}} {{.Spec.Name}}' db_password
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

```text
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

Options on the `--secret` flag:

| Option | Meaning |
|---|---|
| `target=<path>` | Override the mount path inside the container |
| `mode=0400` | File permissions (default 0444) |
| `uid=<n>` | File owner UID inside the container |
| `gid=<n>` | File owner GID inside the container |


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

Each secret appears as a separate file under `/run/secrets/`:
```text
/run/secrets/db_password
/run/secrets/api_key
```

For Quadlet-managed containers:
```ini
[Container]
Secret=db_password
Secret=api_key
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
#    Use target= so the in-container path stays the same
podman run -d \
  --name myapp \
  --secret db_password_v2,target=/run/secrets/db_password \
  myapp:latest

# 4. Verify the app is working with the new secret
curl http://localhost:8080/health

# 5. Remove the old secret
podman secret rm db_password
```

> **Zero-downtime rotation:** For zero-downtime rotation, start the new
> container first (different name or port), verify it works, switch traffic
> (e.g., update firewall redirect), then stop the old container.

For Quadlet-managed services, update the `.container` file:
```ini
# Old:
Secret=db_password

# New (target= keeps in-container path constant):
Secret=db_password_v2,target=/run/secrets/db_password
```
Then: `systemctl --user daemon-reload && systemctl --user restart myapp`


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

For Quadlet files, the `Secret=` directive in `[Container]` handles this
cleanly:

```ini
# ~/.config/containers/systemd/myapp.container
[Container]
Image=myapp:latest
Secret=db_password
Secret=api_key,target=/run/secrets/api.key,mode=0400
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

```bash
# Inspect the secret store metadata (JSON, no values)
cat ~/.local/share/containers/storage/secrets/secrets.json
```

The actual secret values are stored in subdirectories named by secret ID.
The files are readable only by the owning UID.


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
| Never log secret values | Even a "first 4 characters" prefix is a security risk in production |
| Use `target=` on rotation | Keeps in-container path stable; app needs no change |


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** Deploy a MariaDB container that reads its root password from a
Podman secret, then rotate the password without changing the application image.

```bash
# 1. Create the initial secret
printf 'InitialRootP@ss1' | podman secret create mariadb_root -

# 2. Start MariaDB with the secret
podman run -d \
  --name mariadb \
  --secret mariadb_root,target=/run/secrets/mysql_root_password \
  -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/mysql_root_password \
  -v mariadb-data:/var/lib/mysql/data:Z \
  registry.access.redhat.com/rhel9/mariadb-105

# 3. Verify the secret is not in the environment
podman inspect mariadb --format '{{range .Config.Env}}{{.}}\n{{end}}'
# No password in output

# 4. Verify the database works
sleep 5
podman exec mariadb mysql -uroot \
  -p$(podman exec mariadb cat /run/secrets/mysql_root_password) \
  -e "SHOW DATABASES;"

# 5. Rotate: create the new secret
printf 'RotatedRootP@ss2' | podman secret create mariadb_root_v2 -

# 6. Update the DB password inside the running container (DB-level rotation)
podman exec mariadb mysql -uroot \
  -p"InitialRootP@ss1" \
  -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'RotatedRootP@ss2';"

# 7. Stop and recreate the container with the new secret
podman stop mariadb && podman rm mariadb

podman run -d \
  --name mariadb \
  --secret mariadb_root_v2,target=/run/secrets/mysql_root_password \
  -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/mysql_root_password \
  -v mariadb-data:/var/lib/mysql/data:Z \
  registry.access.redhat.com/rhel9/mariadb-105

# 8. Verify the new password works
sleep 5
podman exec mariadb mysql -uroot \
  -p$(podman exec mariadb cat /run/secrets/mysql_root_password) \
  -e "SELECT 'rotation successful';"

# 9. Remove the old secret
podman secret rm mariadb_root

# 10. Confirm only the new secret exists
podman secret ls
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

**1. Secret created with `echo` — trailing newline causes auth failures**

Symptom: application fails to authenticate despite the password looking correct;
`cat /run/secrets/db_password | xxd` shows `0a` byte at end.

Fix:
```bash
podman secret rm db_password
printf 'correct_password' | podman secret create db_password -
# printf never adds a trailing newline
```

---

**2. Secret value visible in `podman inspect`**

Symptom: audit finds passwords in container configuration.

Cause: credentials passed via `--env PASSWORD=value` instead of `--secret`.

Fix:
```bash
# Check for credentials in environment
podman inspect <container> --format '{{range .Config.Env}}{{.}}\n{{end}}'
# Migrate any found values to podman secret
```

---

**3. Container fails to start — secret not found**

Symptom: `Error: no secret with name or id "db_password"`.

Fix:
```bash
podman secret ls   # confirm the secret exists
# If not, create it before starting the container
```

---

**4. `podman secret rm` fails — secret in use**

Symptom: `Error: secret is in use by container <id>`.

Fix:
```bash
# Stop and remove the container first
podman stop myapp && podman rm myapp
podman secret rm db_password
```

---

**5. After rotation, app still uses old password**

Symptom: container restarted but old credential is still in use.

Cause: `systemctl --user daemon-reload` not run after changing the Quadlet
file, or the container was not actually recreated.

Fix:
```bash
systemctl --user daemon-reload
systemctl --user restart myapp
# Verify inside container
podman exec systemd-myapp cat /run/secrets/db_password
```

---

**6. Secret path inside container is wrong**

Symptom: app reads an empty file or `/run/secrets/<name>` is not present.

Fix:
```bash
# Check what path the secret was mounted at
podman exec myapp ls -la /run/secrets/
# If target= was used, the filename matches target, not the secret name
```


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
