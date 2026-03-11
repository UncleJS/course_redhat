
[↑ Back to TOC](#toc)

# Install a RHEL 10 Lab VM
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

## What you need

| Item | Minimum | Recommended |
|---|---|---|
| vCPUs | 1 | 2 |
| RAM | 1.5 GB | 2–4 GB |
| Disk | 20 GB | 40 GB |
| Network | NAT (internet access) | NAT + Host-only adapter |


[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [What you need](#what-you-need)
- [Step 1 — Get a RHEL 10 ISO](#step-1-get-a-rhel-10-iso)
- [Step 2 — Create the VM](#step-2-create-the-vm)
- [Step 3 — RHEL 10 installer (Anaconda)](#step-3-rhel-10-installer-anaconda)
- [Step 4 — First login](#step-4-first-login)
- [Step 5 — Register with Red Hat](#step-5-register-with-red-hat)


## Step 1 — Get a RHEL 10 ISO

1. Create a free account at [Red Hat Developer Portal](https://developers.redhat.com).
2. Navigate to **Downloads → Red Hat Enterprise Linux**.
3. Select **RHEL 10** and download the **Boot ISO** (smaller) or **DVD ISO** (larger, works offline).

> **💡 Developer subscription**
> A Red Hat Developer subscription gives you access to RHEL for personal use
> at no cost. It includes the full package repository — the same as a paid
> subscription.
>


[↑ Back to TOC](#toc)

---

## Step 2 — Create the VM

**virt-manager (KVM)**
1. Open virt-manager → **File → New Virtual Machine**
2. Choose **Local install media** → select the ISO
3. Set RAM, CPUs, and disk to recommended values above
4. Name it `rhel10-lab`, check **Customize configuration before install**
5. Click **Finish**


**VirtualBox**
1. **Machine → New** → name `rhel10-lab`, type **Linux**, version **Red Hat (64-bit)**
2. Assign RAM and disk (use VDI, dynamically allocated)
3. In VM settings → **Storage**, attach the ISO to the optical drive
4. In **Network**, set Adapter 1 to **NAT**


**GNOME Boxes**
1. Click **+** → **Create a Virtual Machine**
2. Select the ISO file
3. Boxes auto-suggests resources — accept or raise them
4. Click **Create**



[↑ Back to TOC](#toc)

---

## Step 3 — RHEL 10 installer (Anaconda)

1. Select **Install Red Hat Enterprise Linux 10**
2. Choose your language
3. In the **Installation Summary** screen, configure:

   - **Installation Destination** → select your virtual disk → **Automatic** partitioning
   - **Software Selection** → choose **Minimal Install** (recommended for learning)
   - **Network & Host Name** → enable the network adapter; set hostname to `rhel10-lab`
   - **Root Password** → set a strong password (you will rarely use it directly)
   - **User Creation** → create a regular user, check **Make this user administrator**

4. Click **Begin Installation**

> **📝 Why Minimal Install?**
> Minimal gives you only what you need. You install additional packages
> deliberately, which teaches you the package manager and keeps the system clean.
>


[↑ Back to TOC](#toc)

---

## Step 4 — First login

After reboot, log in with your regular user account (not root).

```bash
$ whoami
```

Expected: your username (not `root`)


[↑ Back to TOC](#toc)

---

## Step 5 — Register with Red Hat

```bash
sudo subscription-manager register --username <your-redhat-username>
sudo subscription-manager attach --auto
```

> **✅ Verify**
> ```bash
> sudo subscription-manager status
> ```
> Look for a line containing: `Overall Status: Current`
>

Once registered, your system has access to all RHEL 10 repositories.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Installation Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/interactively_installing_rhel_from_installation_media/index) | Official step-by-step installation reference |
| [Red Hat Developer — Free RHEL](https://developers.redhat.com/products/rhel/download) | Download RHEL 10 for free with a Developer account |
| [RHEL 10 — Configuring and managing virtualization](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_virtualization/index) | KVM/QEMU host setup and VM management |
| [virt-install man page](https://linux.die.net/man/1/virt-install) | Full CLI reference for VM creation |

---


[↑ Back to TOC](#toc)

## Next step

→ [First Boot Checklist](02-first-boot.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
