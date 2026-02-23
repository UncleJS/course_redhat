# Install a RHEL 10 Lab VM

## What you need

| Item | Minimum | Recommended |
|---|---|---|
| vCPUs | 1 | 2 |
| RAM | 1.5 GB | 2–4 GB |
| Disk | 20 GB | 40 GB |
| Network | NAT (internet access) | NAT + Host-only adapter |

---

## Step 1 — Get a RHEL 10 ISO

1. Create a free account at [Red Hat Developer Portal](https://developers.redhat.com).
2. Navigate to **Downloads → Red Hat Enterprise Linux**.
3. Select **RHEL 10** and download the **Boot ISO** (smaller) or **DVD ISO** (larger, works offline).

!!! tip "Developer subscription"
    A Red Hat Developer subscription gives you access to RHEL for personal use
    at no cost. It includes the full package repository — the same as a paid
    subscription.

---

## Step 2 — Create the VM

=== "virt-manager (KVM)"
    1. Open virt-manager → **File → New Virtual Machine**
    2. Choose **Local install media** → select the ISO
    3. Set RAM, CPUs, and disk to recommended values above
    4. Name it `rhel10-lab`, check **Customize configuration before install**
    5. Click **Finish**

=== "VirtualBox"
    1. **Machine → New** → name `rhel10-lab`, type **Linux**, version **Red Hat (64-bit)**
    2. Assign RAM and disk (use VDI, dynamically allocated)
    3. In VM settings → **Storage**, attach the ISO to the optical drive
    4. In **Network**, set Adapter 1 to **NAT**

=== "GNOME Boxes"
    1. Click **+** → **Create a Virtual Machine**
    2. Select the ISO file
    3. Boxes auto-suggests resources — accept or raise them
    4. Click **Create**

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

!!! note "Why Minimal Install?"
    Minimal gives you only what you need. You install additional packages
    deliberately, which teaches you the package manager and keeps the system clean.

---

## Step 4 — First login

After reboot, log in with your regular user account (not root).

```bash
$ whoami
```

Expected: your username (not `root`)

---

## Step 5 — Register with Red Hat

```bash
sudo subscription-manager register --username <your-redhat-username>
sudo subscription-manager attach --auto
```

!!! success "Verify"
    ```bash
    sudo subscription-manager status
    ```
    Look for a line containing: `Overall Status: Current`

Once registered, your system has access to all RHEL 10 repositories.

---

## Next step

→ [First Boot Checklist](first-boot.md)
