# Audit Workflow — ausearch, sealert, audit2why

The audit subsystem logs all SELinux denials and security-relevant events.
A systematic audit workflow lets you diagnose and fix issues quickly and
correctly.

---

## The audit subsystem

| Component | Role |
|---|---|
| `auditd` | Audit daemon — writes events to `/var/log/audit/audit.log` |
| `ausearch` | Query and filter audit events |
| `aureport` | Generate summary reports from audit log |
| `audit2why` | Explain AVC denials in plain language |
| `audit2allow` | Generate policy from denials (last resort) |
| `sealert` | Rich analysis with ranked fix suggestions |

```bash
# Ensure auditd is running
sudo systemctl status auditd
```

---

## ausearch — targeted queries

```bash
# Recent AVC denials (last 10 minutes)
sudo ausearch -m avc -ts recent

# Today's AVC denials
sudo ausearch -m avc -ts today

# AVC denials for a specific process
sudo ausearch -m avc -c httpd

# AVC denials for a specific user
sudo ausearch -m avc -ui alice

# AVC denials for a specific object (filename)
sudo ausearch -m avc -f index.html

# Between two timestamps
sudo ausearch -m avc -ts "02/23/2026 08:00:00" -te "02/23/2026 09:00:00"

# Raw output (for piping to audit2why)
sudo ausearch -m avc -ts today --raw
```

---

## Read an AVC record

```
type=AVC msg=audit(1708692000.123:456): avc:  denied  { read } for
  pid=1234 comm="httpd" name="index.html"
  dev="vda3" ino=1234567
  scontext=system_u:system_r:httpd_t:s0
  tcontext=user_u:object_r:user_home_t:s0
  tclass=file permissive=0
```

| Field | Value | Meaning |
|---|---|---|
| `denied { read }` | read | The permission being denied |
| `comm` | httpd | The process name |
| `name` | index.html | The target file |
| `scontext` | `httpd_t` | Source (process) SELinux type |
| `tcontext` | `user_home_t` | Target (file) SELinux type |
| `tclass` | file | Object class |
| `permissive` | 0 | 0=enforcing (was blocked), 1=permissive (was allowed but logged) |

---

## audit2why — explain denials

```bash
# Explain all recent denials
sudo ausearch -m avc -ts recent | sudo audit2why

# Explain denials for one process
sudo ausearch -m avc -c httpd | sudo audit2why
```

`audit2why` will tell you:
- What the denial means in plain language
- Whether a boolean fix exists
- Whether the target needs a different label

---

## aureport — summary statistics

```bash
# Summary of all events
sudo aureport

# AVC denial summary
sudo aureport --avc

# Failed access summary
sudo aureport --failed

# Authentication events
sudo aureport --auth

# Summary for today
sudo aureport --start today --end now
```

---

## sealert — rich analysis

Requires `setroubleshoot-server` installed:

```bash
sudo dnf install -y setroubleshoot-server

# Analyse the audit log
sudo sealert -a /var/log/audit/audit.log
```

`sealert` output shows:
- Description of the denial
- Probability-ranked list of fixes
- The exact command to run for each fix
- Whether it is a known policy bug

---

## The systematic workflow

```
1. Reproduce the problem
2. ausearch -m avc -ts recent  → identify the AVC
3. audit2why                   → understand the denial
4. Apply fix taxonomy (label/boolean/port/policy)
5. Re-test
6. ausearch -m avc -ts recent  → confirm no new denials
7. Document the fix
```

---

## Logging permissive denials (don't miss them)

Even in permissive mode, denials are logged with `permissive=1`.
This lets you audit what *would* be denied before switching to enforcing:

```bash
sudo setenforce 0            # permissive (temporary)
# reproduce the problem
sudo ausearch -m avc -ts recent   # see permissive denials
sudo setenforce 1            # back to enforcing
```

---

## Next step

→ [Lab: Non-Default Port](labs/nondefault-port.md)
