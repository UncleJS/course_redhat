# Automation Mindset — Idempotence

Before writing a single line of Bash or Ansible, you need to think differently
about how you manage systems.

---

## The manual administration trap

When you configure a server by hand:

- Steps are only in your head or a runbook
- You can't repeat the exact steps reliably
- Drift occurs (the server changes over time, documentation doesn't)
- Scaling to 10, 100, or 1000 servers is impossible

---

## Automation thinking

Automation means describing **the desired state**, not the steps to get there.

### Imperative vs Declarative

| Approach | Style | Example |
|---|---|---|
| Imperative | "Do these steps" | `mkdir /etc/myapp; cp config /etc/myapp/; chmod 640` |
| Declarative | "Ensure this state" | "Directory `/etc/myapp` exists, file present, mode 640" |

Ansible (and most modern config management) is declarative: you describe what
you want, the tool figures out how to get there.

---

## Idempotence

> An operation is **idempotent** if running it multiple times produces the
> same result as running it once.

```bash
# Not idempotent — appends a line every time you run it
echo "server = db01" >> /etc/myapp.conf

# Idempotent — only adds the line if it's not already there
grep -qxF "server = db01" /etc/myapp.conf || echo "server = db01" >> /etc/myapp.conf
```

Ansible tasks are idempotent by design. The same playbook run ten times
produces the same final state.

---

## Why idempotence matters

- **Safe to re-run**: apply the playbook on a new server OR re-apply it on an
  existing server to bring it into compliance.
- **Self-documenting**: the playbook is the source of truth for system state.
- **Auditable**: run the playbook in check mode to see what would change.
- **Drift detection**: if a playbook reports changes on a server that should
  be stable, something changed outside of automation.

---

## The "set -euo pipefail" habit for Bash

Even in scripts, think idempotently and fail safely:

```bash
#!/usr/bin/env bash
set -euo pipefail

# -e  exit on any error
# -u  treat unset variables as errors
# -o pipefail  fail if any command in a pipe fails
```

Without `set -e`, a script silently continues after errors and can cause
hard-to-debug problems.

---

## Infrastructure as Code (IaC) principles

1. **Version control everything**: store playbooks, roles, and configs in Git.
2. **Review before apply**: treat automation changes like code changes — PR/review.
3. **Test in a lab first**: never run untested automation on production.
4. **Minimal privilege**: automation accounts should have only the access they need.
5. **No secrets in code**: use Ansible Vault, environment variables, or a secrets manager.

---

## The 4-stage automation workflow

```
Write → Test (lab) → Review → Apply (prod)
   ↑                                    |
   └────────────────────────────────────┘
              (iterate)
```

---

## Next step

→ [Bash Scripting Fundamentals](bash-fundamentals.md)
