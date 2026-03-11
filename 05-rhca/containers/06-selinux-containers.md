
[↑ Back to TOC](#toc)

# Container SELinux Gotchas — Volumes and Labels
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

SELinux and containers interact in specific ways that trip up even experienced
admins. This chapter covers the common pitfalls and their correct fixes.

---
<a name="toc"></a>

## Table of contents

- [The core issue: volume mount labeling](#the-core-issue-volume-mount-labeling)
- [The `:Z` and `:z` volume options](#the-z-and-z-volume-options)
- [What `:Z` actually does](#what-z-actually-does)
- [Named volumes and SELinux](#named-volumes-and-selinux)
- [Port binding and SELinux](#port-binding-and-selinux)
- [Common AVC denials with containers](#common-avc-denials-with-containers)
  - ["Permission denied" on volume mount](#permission-denied-on-volume-mount)
  - ["Container can't listen on port"](#container-cant-listen-on-port)
- [Restoring labels after `:Z`](#restoring-labels-after-z)
- [Audit containers specifically](#audit-containers-specifically)


## The core issue: volume mount labeling

When you bind-mount a host directory into a container, the container process
needs the correct SELinux type to access it. By default, a host directory
has a type appropriate for the host — not for a container process.


[↑ Back to TOC](#toc)

---

## The `:Z` and `:z` volume options

| Option | Meaning | When to use |
|---|---|---|
| `:Z` | Relabel the directory for this container (private) | One container uses this directory |
| `:z` | Relabel as shared (multiple containers can access) | Multiple containers share the directory |
| *(none)* | No relabeling — usually causes permission denied | When the context is already correct |

```bash
# Private (one container)
podman run -d -v ~/myapp/data:/app/data:Z myapp:latest

# Shared (multiple containers)
podman run -d -v ~/shared/uploads:/uploads:z app1:latest
podman run -d -v ~/shared/uploads:/uploads:z app2:latest
```

> **⚠️ Never use :Z on home directories or system paths**
> Using `:Z` on `~` or `/etc` will relabel those paths to a container
> context, breaking host access. Always bind-mount subdirectories.
> ```bash
> # BAD — relabels entire home directory
> podman run -v ~:/home/user:Z myapp:latest
>
> # GOOD — relabels only the specific subdirectory
> podman run -v ~/myapp/data:/home/user/data:Z myapp:latest
> ```
>


[↑ Back to TOC](#toc)

---

## What `:Z` actually does

`:Z` runs `chcon -t container_file_t` on the host directory.

```bash
# Before :Z
ls -Z ~/myapp/data/
# user_u:object_r:user_home_t:s0

# Run with :Z
podman run --rm -v ~/myapp/data:/data:Z ubi9 ls /data

# After :Z
ls -Z ~/myapp/data/
# system_u:object_r:container_file_t:s0:c123,c456
```

The MCS categories (`c123,c456`) are unique per container — preventing
container-to-container access at the SELinux level.


[↑ Back to TOC](#toc)

---

## Named volumes and SELinux

Named volumes (managed by Podman) already have the correct SELinux context:

```bash
podman volume create mydata
podman volume inspect mydata | grep -i mountpoint

ls -Z $(podman volume inspect mydata --format '{{.Mountpoint}}')
# system_u:object_r:container_file_t:s0
```

No `:Z` needed for named volumes — they're already labeled correctly.


[↑ Back to TOC](#toc)

---

## Port binding and SELinux

Rootless container port binding above 1024 does not require SELinux policy
changes. For rootful containers on non-standard ports:

```bash
# Check what types are allowed for container port binding
sudo semanage port -l | grep container

# Add a port if needed (rootful containers)
sudo semanage port -a -t container_port_t -p tcp 9090
```


[↑ Back to TOC](#toc)

---

## Common AVC denials with containers

### "Permission denied" on volume mount

```bash
sudo ausearch -m avc -c "container" -ts recent
```

Look for: `denied { read }` or `denied { write }` with `scontext=container_t`
and `tcontext=user_home_t` (or similar non-container type).

**Fix:** Add `:Z` to the volume mount, or relabel manually:

```bash
sudo chcon -Rt container_file_t ~/myapp/data/
```

### "Container can't listen on port"

Rootless: not an SELinux issue — it's a kernel restriction. Use port > 1024.

Rootful with non-standard port:

```bash
sudo semanage port -a -t container_port_t -p tcp <port>
```


[↑ Back to TOC](#toc)

---

## Restoring labels after `:Z`

If `:Z` labeled a path incorrectly, restore the original context:

```bash
sudo restorecon -Rv ~/myapp/data/
```


[↑ Back to TOC](#toc)

---

## Audit containers specifically

```bash
# AVCs from container processes
sudo ausearch -m avc -c "container" -ts today

# Specific container by name (get PID first)
podman inspect myapp | grep Pid
sudo ausearch -m avc --pid <pid> -ts today
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Dan Walsh — Containers and SELinux](https://www.redhat.com/en/blog/container-permission-denied-errors) | Authoritative post on SELinux label errors in containers |
| [RHEL 10 — Using SELinux with containers](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/building_running_and_managing_containers/index) | Official guide on container SELinux integration |
| [`container_selinux` policy](https://github.com/containers/container-selinux) | Upstream source for the `container_t` policy |

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab: Run Rootless Web App + Persistent Data](labs/01-rootless-web.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
