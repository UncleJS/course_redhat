# About This Guide

> **Note:** This guide does not promise exam coverage. It teaches the real-world
> skills that those certifications measure.

## Purpose

This guide exists to give Linux newcomers and experienced admins alike a single,
structured path through Red Hat Enterprise Linux 10 — from opening a terminal
for the first time to designing resilient infrastructure.

## What makes it different

- **Beginner-safe language**: every concept is explained before it is used.
- **Lab-driven**: you learn by doing, not just reading.
- **Honest about "don't do this"**: common mistakes (disabling SELinux, opening
  all firewall ports, running everything as root) are called out explicitly, with
  the correct alternative shown.
- **RHCA-aligned depth**: the advanced chapters cover the reasoning and design
  thinking expected at architect level — not just "run this command".

## Scope

| In scope | Out of scope |
|---|---|
| RHEL 10 (minimal/server install) | RHEL 6, 7, or 8 specifics |
| Single-host and small-lab scenarios | Large-scale fleet management |
| Podman (rootless containers) | Kubernetes / OpenShift |
| Ansible fundamentals | Advanced Ansible Tower/AAP |
| Core RHEL networking | SDN / OVN |

## Versions and testing

Commands in this guide were tested on:

- **RHEL 10.0** (minimal install, 2 vCPU, 2 GB RAM, 20 GB disk)
- Each lab page lists the exact package versions used.

## Contributing

Found an error or want to add a lab? Open an issue or pull request in the
repository. All contributions must follow the [Conventions](conventions.md)
style guide and include a working `Verify` section.

## License

This guide is published under the [Creative Commons Attribution 4.0 International
License](https://creativecommons.org/licenses/by/4.0/).

---

## Next step

→ [Lab Workflow (Snapshots, Safety)](labs.md)
