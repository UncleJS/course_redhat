
[↑ Back to TOC](#toc)

# Automation Mindset — Idempotence
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Before writing a single line of Bash or Ansible, you need to think differently
about how you manage systems.

---
<a name="toc"></a>

## Table of contents

- [The manual administration trap](#the-manual-administration-trap)
- [Automation thinking](#automation-thinking)
  - [Imperative vs Declarative](#imperative-vs-declarative)
- [Idempotence](#idempotence)
- [Why idempotence matters](#why-idempotence-matters)
- [The "set -euo pipefail" habit for Bash](#the-set-euo-pipefail-habit-for-bash)
- [Infrastructure as Code (IaC) principles](#infrastructure-as-code-iac-principles)
- [The 4-stage automation workflow](#the-4-stage-automation-workflow)


## The manual administration trap

When you configure a server by hand:

- Steps are only in your head or a runbook
- You can't repeat the exact steps reliably
- Drift occurs (the server changes over time, documentation doesn't)
- Scaling to 10, 100, or 1000 servers is impossible


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

---

## Why idempotence matters

- **Safe to re-run**: apply the playbook on a new server OR re-apply it on an
  existing server to bring it into compliance.
- **Self-documenting**: the playbook is the source of truth for system state.
- **Auditable**: run the playbook in check mode to see what would change.
- **Drift detection**: if a playbook reports changes on a server that should
  be stable, something changed outside of automation.


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

---

## Infrastructure as Code (IaC) principles

1. **Version control everything**: store playbooks, roles, and configs in Git.
2. **Review before apply**: treat automation changes like code changes — PR/review.
3. **Test in a lab first**: never run untested automation on production.
4. **Minimal privilege**: automation accounts should have only the access they need.
5. **No secrets in code**: use Ansible Vault, environment variables, or a secrets manager.


[↑ Back to TOC](#toc)

---

## The 4-stage automation workflow

```
Write → Test (lab) → Review → Apply (prod)
   ↑                                    |
   └────────────────────────────────────┘
              (iterate)
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [The Twelve-Factor App](https://12factor.net/) | Software methodology that embeds idempotent, reproducible thinking |
| [Ansible — Getting started](https://docs.ansible.com/ansible/latest/getting_started/index.html) | Official intro to the Ansible automation philosophy |
| [Infrastructure as Code (Martin Fowler)](https://martinfowler.com/bliki/InfrastructureAsCode.html) | Conceptual overview of IaC and idempotence |

---


[↑ Back to TOC](#toc)

## Next step

→ [Bash Scripting Fundamentals](02-bash-fundamentals.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
