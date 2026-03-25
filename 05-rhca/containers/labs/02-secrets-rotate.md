
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab - Podman Secrets Rotation
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

## Overview

Create a containerized application that reads a database password from a Podman secret, then perform a zero-downtime secret rotation: update the secret value, recreate the container, and verify the new credential is in use — all without ever writing the secret to disk or an environment variable that appears in `ps` output.

**Track:** D — RHCA-style  
**Estimated time:** 50 minutes  
**Difficulty:** Intermediate–Advanced


[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [Overview](#overview)
- [Background](#background)
- [Prerequisites](#prerequisites)
- [Success Criteria](#success-criteria)
- [Steps](#steps)
  - [1 — Create the initial secret](#1-create-the-initial-secret)
  - [2 — Build a minimal test image](#2-build-a-minimal-test-image)
  - [3 — Write the Quadlet `.container` file](#3-write-the-quadlet-container-file)
  - [4 — Start the service and verify the initial secret](#4-start-the-service-and-verify-the-initial-secret)
  - [5 — Verify the secret is NOT in the process list](#5-verify-the-secret-is-not-in-the-process-list)
  - [6 — Rotate the secret](#6-rotate-the-secret)
  - [7 — Remove the old secret](#7-remove-the-old-secret)
  - [8 — Simulate a second rotation (practice)](#8-simulate-a-second-rotation-practice)
- [Verify Checkpoints](#verify-checkpoints)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)
- [Production Notes](#production-notes)
- [Recap](#recap)


## Prerequisites

- RHEL 10 with Podman ≥ 4.9
- The `rootless-web` lab completed (or equivalent Quadlet familiarity)
- A non-root `student` user account

---


[↑ Back to TOC](#toc)

## Success Criteria

- [ ] Secret created via `podman secret create` (never written to a file)
- [ ] Container mounts the secret at a known path inside the container
- [ ] `podman exec` verifies the secret value is readable inside the container
- [ ] Secret rotated to a new value without downtime (old → new)
- [ ] Quadlet `.container` file drives the service lifecycle
- [ ] Old secret version confirmed absent after rotation

---


[↑ Back to TOC](#toc)

## Background

Podman secrets are stored in `$XDG_DATA_HOME/containers/storage/secrets/`
(rootless) or `/var/lib/containers/storage/secrets/` (root). They are injected
into the container as a read-only tmpfs mount at `/run/secrets/<name>` — never
exposed on the command line, in environment variables, or in image layers.

The key security property: `podman inspect <container>` never reveals the
secret value. Environment variables set via `--env` do appear in `podman
inspect` and in `ps -e` — this is why the Podman secrets mechanism exists.

**Rotation workflow:**

1. Create a new secret with a different name (e.g., `db-password-v2`)
2. Update the `.container` file to reference the new secret with the same
   `target=` path (so the application path inside the container stays constant)
3. `systemctl --user daemon-reload && systemctl --user restart` the service
4. Verify the application uses the new credential
5. Delete the old secret

The `target=` option is the key to zero-application-change rotation: the
in-container path `/run/secrets/db-password` stays the same regardless of
which Podman secret is currently providing the value. Only the Quadlet file
changes.


[↑ Back to TOC](#toc)

---

## Steps

### 1 — Create the initial secret

```bash
# Use printf to avoid a trailing newline in the secret value
$ printf 'S3cur3P@ssw0rd-v1' | podman secret create db-password -

# Verify the secret is registered (value is NOT shown)
$ podman secret ls
ID            NAME         DRIVER  CREATED        UPDATED
abc123def456  db-password  file    5 seconds ago  5 seconds ago
```

> **Hint:** `echo 'password' | podman secret create` adds a trailing `\n`
> to the secret value. This causes authentication failures with most databases.
> Always use `printf`.


[↑ Back to TOC](#toc)

---

### 2 — Build a minimal test image

We use a simple Alpine-based image that loops and prints the secret content to its log (for lab verification only — never do this in production).

```bash
$ mkdir -p ~/secret-lab

$ cat > ~/secret-lab/Containerfile <<'EOF'
FROM docker.io/library/alpine:latest
RUN apk add --no-cache bash
# Entrypoint reads the secret every 5 seconds and logs the first 4 chars
CMD ["bash", "-c", "while true; do \
  val=$(cat /run/secrets/db-password 2>/dev/null || echo 'SECRET_MISSING'); \
  echo \"[$(date -Iseconds)] password prefix: ${val:0:4}****\"; \
  sleep 5; \
done"]
EOF

$ podman build -t localhost/secret-demo:latest ~/secret-lab/
```

> **Hint:** The `${val:0:4}` substring logs only the first 4 characters.
> In a real application, never log any portion of a secret. This is for
> lab verification only.


[↑ Back to TOC](#toc)

---

### 3 — Write the Quadlet `.container` file

```bash
$ mkdir -p ~/.config/containers/systemd

$ cat > ~/.config/containers/systemd/secret-demo.container <<'EOF'
[Unit]
Description=Secret rotation demo (RHCA lab)
After=network-online.target

[Container]
Image=localhost/secret-demo:latest
Secret=db-password

[Service]
Restart=on-failure
TimeoutStartSec=30

[Install]
WantedBy=default.target
EOF
```

> **Hint:** The `Secret=db-password` directive mounts the secret at
> `/run/secrets/db-password` inside the container automatically. No volume
> directive needed — Podman handles the tmpfs mount.


[↑ Back to TOC](#toc)

---

### 4 — Start the service and verify the initial secret

```bash
$ systemctl --user daemon-reload
$ systemctl --user start secret-demo

# Watch the logs
$ journalctl --user -u secret-demo -f &
# Output should show: password prefix: S3cu****

# Exec in to verify directly
$ podman exec -it systemd-secret-demo cat /run/secrets/db-password
S3cur3P@ssw0rd-v1
```

> **Hint:** The Quadlet-generated container name is `systemd-<unit-base-name>`,
> so a unit file named `secret-demo.container` produces a container named
> `systemd-secret-demo`.


[↑ Back to TOC](#toc)

---

### 5 — Verify the secret is NOT in the process list

```bash
# The secret value must not appear in any process arguments
$ ps -ef | grep secret-demo
# You will see the bash loop command — no password visible

# Also check podman inspect (env vars)
$ podman inspect systemd-secret-demo --format '{{.Config.Env}}'
# No password in environment variables
```


[↑ Back to TOC](#toc)

---

### 6 — Rotate the secret

**Step 6a — Create the new secret version**

```bash
$ printf 'S3cur3P@ssw0rd-v2' | podman secret create db-password-v2 -

$ podman secret ls
ID            NAME             DRIVER  CREATED         UPDATED
abc123def456  db-password      file    3 minutes ago   3 minutes ago
def789abc012  db-password-v2   file    5 seconds ago   5 seconds ago
```

**Step 6b — Update the Quadlet file to use the new secret**

```bash
$ sed -i 's/Secret=db-password$/Secret=db-password-v2/' \
    ~/.config/containers/systemd/secret-demo.container

# Also update the mount path alias so the app path stays the same
# Replace the Secret line with a target path form:
$ cat > ~/.config/containers/systemd/secret-demo.container <<'EOF'
[Unit]
Description=Secret rotation demo (RHCA lab)
After=network-online.target

[Container]
Image=localhost/secret-demo:latest
Secret=db-password-v2,target=/run/secrets/db-password

[Service]
Restart=on-failure
TimeoutStartSec=30

[Install]
WantedBy=default.target
EOF
```

> **Hint:** Using `target=/run/secrets/db-password` means the application
> path inside the container stays constant. Only the Podman secret name
> changes. The app needs no code change.

**Step 6c — Restart the service**

```bash
$ systemctl --user daemon-reload
$ systemctl --user restart secret-demo

# Watch the transition in logs
$ journalctl --user -u secret-demo -n 20
# You should now see: password prefix: S3cu**** (same prefix, but v2 value inside)

# Confirm inside container
$ podman exec -it systemd-secret-demo cat /run/secrets/db-password
S3cur3P@ssw0rd-v2
```


[↑ Back to TOC](#toc)

---

### 7 — Remove the old secret

```bash
# Only safe to delete after confirming the new secret is working
$ podman secret rm db-password

# Verify it is gone
$ podman secret ls
ID            NAME             DRIVER  CREATED         UPDATED
def789abc012  db-password-v2   file    2 minutes ago   2 minutes ago
```


[↑ Back to TOC](#toc)

---

### 8 — Simulate a second rotation (practice)

Repeat the cycle to build muscle memory:

```bash
$ printf 'S3cur3P@ssw0rd-v3' | podman secret create db-password-v3 -

# Update Quadlet
$ sed -i 's/db-password-v2/db-password-v3/' \
    ~/.config/containers/systemd/secret-demo.container

$ systemctl --user daemon-reload
$ systemctl --user restart secret-demo

# Verify
$ podman exec -it systemd-secret-demo cat /run/secrets/db-password
S3cur3P@ssw0rd-v3

# Cleanup old
$ podman secret rm db-password-v2
```


[↑ Back to TOC](#toc)

---

## Verify Checkpoints

```bash
# 1. Secret exists and has no readable value via CLI
$ podman secret ls
$ podman secret inspect db-password-v3   # shows metadata, NOT the value

# 2. Container is running
$ systemctl --user status secret-demo
Active: active (running)

# 3. Secret mounted at correct path
$ podman exec systemd-secret-demo ls -la /run/secrets/
total 0
-r--------    1 root     root            17 ...  db-password

# 4. No secret in env or process args
$ podman inspect systemd-secret-demo --format '{{range .Config.Env}}{{.}}\n{{end}}'
# No password lines

# 5. Journal shows new prefix after rotation
$ journalctl --user -u secret-demo -n 5
```


[↑ Back to TOC](#toc)

---

## Troubleshooting guide

| Symptom | Likely Cause | Diagnostic | Fix |
|---|---|---|---|
| `Error: no secret with name or id "db-password"` on start | Secret not created before unit start | `podman secret ls` | Create the secret first, then `systemctl --user start` |
| Secret file is empty inside container | `echo` used instead of `printf` | `podman exec container xxd /run/secrets/db-password \| tail -1` (look for 0a byte) | `podman secret rm`; recreate with `printf` |
| App still reads old password after rotation | Daemon not reloaded or service not restarted | `systemctl --user show secret-demo \| grep ExecStart` (check secret name) | `systemctl --user daemon-reload && systemctl --user restart secret-demo` |
| `cat /run/secrets/db-password` returns `SECRET_MISSING` | Wrong `target=` path in Quadlet | `podman exec container ls /run/secrets/` (check actual filename) | Verify `Secret=...,target=/run/secrets/db-password` matches what the app reads |
| Secret value appears in `journalctl` output | Application logging full secret | Grep journal output for the password string | This is a lab-only behavior; in production, never log secret values |
| `podman secret rm` fails with "secret in use" | Container still running and using the secret | `podman ps \| grep secret-demo` | Stop the container first, then remove the old secret |
| After rotation, `podman exec` still shows old value | Container not restarted after `daemon-reload` | `journalctl --user -u secret-demo -n 5` (check last start time) | `systemctl --user restart secret-demo` (not just daemon-reload) |
| Unit shows as `generated` but fails to start | Syntax error in `.container` file | `systemd-analyze verify --user ~/.config/containers/systemd/secret-demo.container` | Fix the directive name or value causing the parse error |


[↑ Back to TOC](#toc)

---

## Extension tasks

### Extension 1 — Zero-downtime rotation with two containers

Practice a true zero-downtime rotation by running both containers simultaneously
and switching traffic between them.

```bash
# 1. Current container (v2 secret) is running on port 8000
#    Start a new container with v3 secret on port 8001

$ printf 'S3cur3P@ssw0rd-v3' | podman secret create db-password-v3 -

$ podman run -d \
  --name secret-demo-new \
  --secret db-password-v3,target=/run/secrets/db-password \
  -p 8001:8000 \
  localhost/secret-demo:latest

# 2. Verify new container uses correct secret
$ podman exec secret-demo-new cat /run/secrets/db-password
S3cur3P@ssw0rd-v3

# 3. Switch traffic (update firewall redirect) then stop old container
$ podman stop systemd-secret-demo

# 4. Clean up old secret
$ podman secret rm db-password-v2
$ podman rm secret-demo-new
```

---

### Extension 2 — Inject a TLS certificate as a secret

Podman secrets are not limited to passwords — they can hold any binary or
text data. Inject a self-signed TLS certificate as a secret.

```bash
# 1. Generate a self-signed cert
mkdir -p ~/tls-lab
openssl req -x509 -newkey rsa:2048 -keyout ~/tls-lab/key.pem \
  -out ~/tls-lab/cert.pem -days 30 -nodes \
  -subj '/CN=localhost'

# 2. Create secrets from the files
podman secret create tls_cert ~/tls-lab/cert.pem
podman secret create tls_key  ~/tls-lab/key.pem

# 3. Mount both in a container
podman run --rm \
  --secret tls_cert,target=/etc/nginx/certs/tls.crt,mode=0444 \
  --secret tls_key,target=/etc/nginx/certs/tls.key,mode=0400 \
  docker.io/library/nginx:stable-alpine \
  ls -la /etc/nginx/certs/

# 4. Clean up
podman secret rm tls_cert tls_key
rm -rf ~/tls-lab
```

---

### Extension 3 — Audit secret access with auditd

Configure auditd to log any process that reads a Podman secret file and
verify the audit trail.

```bash
# 1. Add an audit watch on the secrets directory
sudo auditctl -w ~/.local/share/containers/storage/secrets/ \
  -p rwxa -k podman_secrets

# 2. Access the secret (read event)
podman exec systemd-secret-demo cat /run/secrets/db-password

# 3. Check the audit log
sudo ausearch -k podman_secrets -ts recent

# 4. Remove the watch
sudo auditctl -W ~/.local/share/containers/storage/secrets/ \
  -p rwxa -k podman_secrets
```


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
$ systemctl --user stop secret-demo
$ systemctl --user disable secret-demo
$ rm ~/.config/containers/systemd/secret-demo.container
$ systemctl --user daemon-reload

# Remove all lab secrets
$ podman secret rm db-password-v3 2>/dev/null || true
$ podman secret rm db-password-v2 2>/dev/null || true
$ podman secret rm db-password   2>/dev/null || true

# Remove image and build context
$ podman rmi localhost/secret-demo:latest
$ rm -rf ~/secret-lab
```

---


[↑ Back to TOC](#toc)

## Common Failures

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Error: no secret with name or id "db-password"` on start | Secret not created before unit start | Create the secret first, then `systemctl --user start` |
| Secret file is empty inside container | `echo` used instead of `printf` | Delete and recreate: `podman secret rm`; use `printf` |
| App still reads old password after rotation | Daemon not reloaded or service not restarted | `systemctl --user daemon-reload && systemctl --user restart` |
| `cat /run/secrets/db-password` returns `SECRET_MISSING` | Wrong `target=` path in Quadlet | Check the `Secret=` line; path must match what the app reads |
| Secret value appears in `journalctl` output | Application logging full secret | This is a lab-only behavior; in production, never log secret values |
| `podman secret rm` fails with "secret in use" | Container still running and using the secret | Stop the container first, then remove the old secret |

---


[↑ Back to TOC](#toc)

## Production Notes

In real environments:

- **Never log secret values.** This lab logs a prefix for verification only.
- **Integrate with a secrets manager** (HashiCorp Vault, AWS Secrets Manager, RHEL IdM) using an init container or sidecar that populates Podman secrets on start.
- **Use a naming convention** for versioned secrets (`appname-secrettype-vN`) so rotation is auditable.
- **Automate rotation** with an Ansible playbook:
  1. Generate new credential in the target system (DB, API)
  2. `podman secret create` new version
  3. Update `.container` file via template
  4. `systemctl --user restart`
  5. Verify health check passes
  6. `podman secret rm` old version


[↑ Back to TOC](#toc)

---

## Why This Matters in Production

- Secrets in environment variables are readable by any process in the container and often leaked in logs. The `/run/secrets/` tmpfs mount is only readable by the container's root process.
- The rotation procedure requires **zero application code changes** — only the Podman secret name and the `.container` file change.
- The old secret remains available until you explicitly delete it, giving you a safe rollback window.
- This pattern is compatible with GitOps: the `.container` file is committed; only the secret value lives outside Git.

---


[↑ Back to TOC](#toc)

## Recap

You created a secret, injected it into a container via Quadlet, verified it was never exposed on the process list or in environment variables, rotated it to a new version with a constant in-container path, and cleaned up the old version. This complete lifecycle is the production-grade secret management pattern for Podman on RHEL 10.


[↑ Back to TOC](#toc)

---

## Next step

→ [Networking: L2 Concepts](../../networking/04-l2-concepts.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
