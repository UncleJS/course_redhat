# SELinux Troubleshooting — AVCs
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

An **AVC (Access Vector Cache) denial** is what SELinux logs when it blocks
an action. Learning to read and correctly respond to AVCs is the key skill.

---
<a name="toc"></a>

## Table of contents

- [Where AVC denials are logged](#where-avc-denials-are-logged)
- [Reading an AVC denial](#reading-an-avc-denial)
- [`audit2why` — plain-language explanation](#audit2why-plain-language-explanation)
- [`sealert` — richer analysis](#sealert-richer-analysis)
- [The fix taxonomy (choose the right fix)](#the-fix-taxonomy-choose-the-right-fix)
- [Common AVC scenarios and fixes](#common-avc-scenarios-and-fixes)
  - [Web content in wrong location](#web-content-in-wrong-location)
  - [Service on non-default port](#service-on-non-default-port)
- [Confirm SELinux mode before assuming it's a permission problem](#confirm-selinux-mode-before-assuming-its-a-permission-problem)
- [Quick AVC search with `ausearch`](#quick-avc-search-with-ausearch)


## Where AVC denials are logged

```bash
# Primary audit log
sudo tail -f /var/log/audit/audit.log | grep AVC

# Journal (syslog copy)
sudo journalctl -f | grep avc
```


[↑ Back to TOC](#toc)

---

## Reading an AVC denial

Example AVC from `/var/log/audit/audit.log`:

```
type=AVC msg=audit(1708692000.123:456): avc:  denied  { read } for
pid=1234 comm="httpd" name="index.html"
scontext=system_u:system_r:httpd_t:s0
tcontext=user_u:object_r:user_home_t:s0
tclass=file permissive=0
```

| Field | Meaning |
|---|---|
| `denied { read }` | httpd tried to **read** a file and was blocked |
| `comm="httpd"` | The process was httpd |
| `name="index.html"` | The target file |
| `scontext=...httpd_t...` | Source context (httpd process) |
| `tcontext=...user_home_t...` | Target context (file has wrong type) |
| `tclass=file` | The object class being accessed |

**The fix here:** the file has `user_home_t` context but httpd needs
`httpd_sys_content_t`. Fix = `restorecon`, not `chmod 777`.


[↑ Back to TOC](#toc)

---

## `audit2why` — plain-language explanation

```bash
sudo audit2why < /var/log/audit/audit.log
```

This reads the audit log and explains each denial in plain language,
including a suggested fix.

> **⚠️ audit2why is a diagnostic tool, not a fix generator**
> audit2why may suggest generating a custom policy module with `audit2allow`.
> Only do this as a last resort after ruling out a label fix, boolean, or
> port fix. Custom modules can silently permit unintended access.
>


[↑ Back to TOC](#toc)

---

## `sealert` — richer analysis

```bash
# Analyse the audit log
sudo sealert -a /var/log/audit/audit.log

# If setroubleshootd is running, check its log
sudo journalctl -u setroubleshootd
```

`sealert` provides:
- A human-readable description of the denial
- Probability-ranked suggested fixes
- The correct `semanage` or `setsebool` command to run


[↑ Back to TOC](#toc)

---

## The fix taxonomy (choose the right fix)

When you see an AVC, work through this order:

```
1. Wrong file label?  → restorecon -Rv <path>
2. Non-default path?  → semanage fcontext + restorecon
3. Boolean covers it? → setsebool -P <boolean> on
4. Non-default port?  → semanage port -a -t <type> -p tcp <port>
5. None of the above? → audit2allow (last resort, with caution)
```

This taxonomy is enough to solve the vast majority of day-to-day AVC denials.
When you reach the RHCA track, the [SELinux Deep Dive](../05-rhca/selinux/01-fix-taxonomy.md)
chapter expands each fix type with edge cases and `semanage` details — but you
don't need it yet.


[↑ Back to TOC](#toc)

---

## Common AVC scenarios and fixes

### Web content in wrong location

**Symptom:** httpd returns 403, audit log shows `denied { read }` for your content file.

```bash
ls -Z /var/www/html/        # should show httpd_sys_content_t
ls -Z /home/rhel/myapp/     # shows user_home_t — wrong location for web content
```

**Fix — option A:** move content to `/var/www/html/` (preferred):

```bash
sudo cp -r /home/rhel/myapp/* /var/www/html/
sudo restorecon -Rv /var/www/html/
```

**Fix — option B:** if the path must stay non-standard, use `semanage`:

```bash
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/myapp(/.*)?"
sudo restorecon -Rv /srv/myapp/
```

### Service on non-default port

**Symptom:** httpd fails to start on port 8080, AVC shows `name_bind denied`.

```bash
sudo semanage port -l | grep http
# Add the port
sudo semanage port -a -t http_port_t -p tcp 8080
# Restart service
sudo systemctl restart httpd
```


[↑ Back to TOC](#toc)

---

## Confirm SELinux mode before assuming it's a permission problem

Many admins blame SELinux when the actual problem is a missing firewall rule
or a standard Unix permission. Always check in this order:

1. `systemctl status <service>` — is it even running?
2. Standard file permissions (`ls -l`)
3. SELinux context (`ls -Z`)
4. AVC in audit log (`sudo ausearch -m avc -ts recent`)
5. Firewall (`sudo firewall-cmd --list-all`)


[↑ Back to TOC](#toc)

---

## Quick AVC search with `ausearch`

```bash
# Recent AVC denials
sudo ausearch -m avc -ts recent

# Today's AVCs
sudo ausearch -m avc -ts today

# AVCs for a specific process
sudo ausearch -m avc -c httpd
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`audit2allow` man page](https://man7.org/linux/man-pages/man1/audit2allow.1.html) | Generate policy modules from AVC denials |
| [`audit2why` man page](https://man7.org/linux/man-pages/man1/audit2why.1.html) | Explain why a denial occurred in human language |
| [`sealert` man page](https://linux.die.net/man/8/sealert) | SELinux alert browser — part of `setroubleshoot-server` |
| [RHEL 10 — Troubleshooting SELinux](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/using_selinux/troubleshooting-problems-related-to-selinux_using-selinux) | Official AVC troubleshooting workflows |

---

## Next step

→ [Lab: Fix a SELinux Label Issue](labs/04-selinux-label-fix.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
