
[↑ Back to TOC](#toc)

# Container SELinux Gotchas — Volumes and Labels
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

SELinux and containers interact in specific ways that trip up even experienced
admins. This chapter covers the common pitfalls and their correct fixes.

At RHCA level, diagnosing SELinux failures in containers requires understanding
two distinct layers of policy. The first is the type enforcement layer: the
container process runs as `container_t` (or a derived type), and SELinux policy
defines what file types `container_t` may access. Host directories have types
like `user_home_t` or `etc_t` that `container_t` cannot read. The fix is to
relabel the directory to `container_file_t` using `:Z` or `:z` mount options.

The second layer is MCS (Multi-Category Security), which is used to isolate
containers from each other. Even if two containers both run as `container_t`,
each is assigned a unique MCS category pair (e.g., `c100,c200`). A file
relabeled with `:Z` gets that container's specific MCS category — preventing
other containers (including ones with the same type) from accessing it. This is
why `:Z` provides *per-container* isolation and `:z` provides *shared* access.

When debugging a container SELinux denial, the workflow is:
1. Check `ausearch -m avc -ts recent` for the denial message.
2. Read the denial: note the `scontext` (what is trying to access) and
   `tcontext` (what is being accessed), and the `tclass` + `permissions`.
3. If `tcontext` has a non-container type, relabel the host path.
4. If `tcontext` has a correct type but wrong MCS category, you may have
   re-used a `:Z`-labeled path across two containers — use `:z` instead.
5. Never use `setenforce 0` as a fix. Diagnose and relabel.

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
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## The core issue: volume mount labeling

When you bind-mount a host directory into a container, the container process
needs the correct SELinux type to access it. By default, a host directory
has a type appropriate for the host — not for a container process.

The container process type (`container_t`) is only allowed to access files
labeled `container_file_t` (and a few other container-specific types).
Access to `user_home_t`, `etc_t`, `var_t`, or any other host-system type is
denied by policy — even if UNIX permissions would allow it.

This is a **design feature**, not a bug. It prevents a compromised container
from reading sensitive host files even if it runs as root inside the namespace.


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

> **Never use :Z on home directories or system paths**
> Using `:Z` on `~` or `/etc` will relabel those paths to a container
> context, breaking host access. Always bind-mount subdirectories.
> ```bash
> # BAD — relabels entire home directory
> podman run -v ~:/home/user:Z myapp:latest
>
> # GOOD — relabels only the specific subdirectory
> podman run -v ~/myapp/data:/home/user/data:Z myapp:latest
> ```

> **Exam tip:** The `:z` flag relabels with a shared label
> (`svirt_sandbox_file_t`); multiple containers can access the directory.
> The `:Z` flag uses a private MCS-labeled context — only one container. Use
> `:Z` for single-container mounts to achieve per-container isolation.


[↑ Back to TOC](#toc)

---

## What `:Z` actually does

`:Z` runs `chcon -t container_file_t` on the host directory, and adds a
unique MCS category pair derived from the container's MCS label.

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

The `:z` option (lowercase) relabels to `container_file_t` without adding
unique MCS categories, making the directory accessible to any container:

```bash
ls -Z ~/shared/uploads/
# system_u:object_r:container_file_t:s0
# (no MCS categories — shared access)
```


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

However, if you populate a named volume from the host (e.g., by copying files
into the mountpoint path), those files will have host-derived SELinux types.
Always populate named volumes through a container, not directly:

```bash
# CORRECT: populate via container
podman run --rm \
  -v mydata:/data:Z \
  -v ~/source:/source:ro,Z \
  ubi9 cp -r /source/. /data/

# INCORRECT: direct copy bypasses SELinux labeling
cp ~/source/. ~/.local/share/containers/storage/volumes/mydata/_data/
```


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

# Verify the port was added
sudo semanage port -l | grep 9090
```

For rootless containers, port binding below 1024 is a kernel restriction
(`CAP_NET_BIND_SERVICE`), not an SELinux policy issue. Use `firewall-cmd
--add-forward-port` to redirect from port 80 to 8080.


[↑ Back to TOC](#toc)

---

## Common AVC denials with containers

### "Permission denied" on volume mount

```bash
sudo ausearch -m avc -c "container" -ts recent
```

Look for: `denied { read }` or `denied { write }` with `scontext=container_t`
and `tcontext=user_home_t` (or similar non-container type).

Read the denial:
```text
type=AVC msg=audit(...): avc:  denied  { write } for  pid=12345
  comm="app" name="data" dev="dm-0" ino=123456
  scontext=system_u:system_r:container_t:s0:c100,c200
  tcontext=unconfined_u:object_r:user_home_t:s0
  tclass=dir permissive=0
```

The `tcontext=user_home_t` tells you the host directory has not been relabeled.

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

`restorecon` reads the SELinux file context database and reapplies the
default context for the path. For home directory paths, this typically
restores `user_home_t`.

To see what the default context would be without applying it:

```bash
sudo restorecon -nv ~/myapp/data/
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

# Continuous monitoring
sudo ausearch -m avc -ts recent -i | tail -20

# Generate a human-readable allow rule suggestion
sudo audit2allow -a -M mycontainer < /var/log/audit/audit.log
cat mycontainer.te
```

`audit2allow` generates a policy module that would allow the denied action.
Use it to understand the denial, not to blindly apply the module.


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** A container that writes log files to a bind-mounted host
directory fails with "permission denied". Diagnose and fix using only
correct SELinux relabeling — not `setenforce 0`.

```bash
# 1. Create a host directory without :Z
mkdir -p ~/app/logs

# 2. Run the container — it will fail to write
podman run -d \
  --name logwriter \
  -v ~/app/logs:/app/logs \
  docker.io/library/alpine \
  sh -c "while true; do echo 'log entry' >> /app/logs/app.log; sleep 2; done"

# 3. Observe the failure
podman logs logwriter
# sh: can't create /app/logs/app.log: Permission denied

# 4. Check the current SELinux context
ls -Z ~/app/logs
# unconfined_u:object_r:user_home_t:s0

# 5. Check the AVC denial
sudo ausearch -m avc -ts recent | grep logwriter
# denied { write } ... tcontext=user_home_t ...

# 6. Fix: stop, remove, and re-run with :Z
podman stop logwriter && podman rm logwriter

podman run -d \
  --name logwriter \
  -v ~/app/logs:/app/logs:Z \
  docker.io/library/alpine \
  sh -c "while true; do echo 'log entry' >> /app/logs/app.log; sleep 2; done"

# 7. Verify the write succeeds
sleep 3
podman logs logwriter
# log entry
# log entry

# 8. Verify the relabeled context
ls -Z ~/app/logs
# system_u:object_r:container_file_t:s0:c<n>,c<m>

# 9. Verify no new AVC denials
sudo ausearch -m avc -ts recent

# 10. Cleanup and restore context
podman stop logwriter && podman rm logwriter
sudo restorecon -Rv ~/app/logs
ls -Z ~/app/logs
# unconfined_u:object_r:user_home_t:s0  (restored)
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

**1. Using `setenforce 0` to "fix" container SELinux issues**

Symptom: everything works after `setenforce 0` — admin assumes SELinux was
the problem and leaves it disabled.

Fix: This disables SELinux system-wide and removes a critical security layer.
Diagnose the actual denial and relabel the specific path:
```bash
sudo ausearch -m avc -ts recent   # find the denial
# Apply :Z, chcon, or semanage port — not setenforce 0
```

---

**2. `:Z` applied to a path used by two containers**

Symptom: first container works; second container gets "permission denied"
on the same directory.

Cause: `:Z` assigned the MCS category of the first container to the directory.
The second container has a different MCS category and cannot access it.

Fix:
```bash
# Use :z (lowercase) for shared access
podman run -d -v ~/shared:/data:z container1
podman run -d -v ~/shared:/data:z container2
```

---

**3. Named volume populated directly on host — wrong context**

Symptom: container cannot read files copied into the volume mountpoint.

Fix:
```bash
# Check context of files in volume
ls -Z $(podman volume inspect mydata --format '{{.Mountpoint}}')
# If not container_file_t:
sudo chcon -Rt container_file_t \
  $(podman volume inspect mydata --format '{{.Mountpoint}}')
```

---

**4. `restorecon` undoes a needed `:Z` label**

Symptom: container access breaks after running `restorecon`.

Fix: `restorecon` restores *default* context from the policy database.
For bind-mounted paths, run with `:Z` on each container start, or set the
default context permanently:
```bash
sudo semanage fcontext -a -t container_file_t "/home/student/myapp/data(/.*)?"
sudo restorecon -Rv ~/myapp/data
```

---

**5. Port denied for rootful container**

Symptom: rootful container cannot bind to a port even though the process
would have permission via capabilities.

Fix:
```bash
sudo semanage port -l | grep <port>   # check if port has a type
sudo semanage port -a -t container_port_t -p tcp <port>
```

---

**6. AVC denial for `container_t` reading `etc_t` file**

Symptom: container cannot read a config file bind-mounted from `/etc`.

Fix: never bind-mount system paths directly. Copy config to a dedicated
directory first:
```bash
mkdir -p ~/myapp/conf
cp /etc/myapp/app.conf ~/myapp/conf/
podman run -v ~/myapp/conf:/etc/myapp:ro,Z myapp:latest
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
