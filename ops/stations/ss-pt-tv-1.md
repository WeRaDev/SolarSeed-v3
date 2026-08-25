# SolarSeed Station "ss-pt-tv-1" (TRL5 Field Machine)

Station Call Sign: **ss-pt-tv-1**  
Role: City of Light TRL5 field machine (solar/edge profile, Nextcloud AIO + Odoo stack)  
Hostname: `wera-ss-pt-tv-1`  
Tailscale FQDN: `wera-ss-pt-tv-1.tailfb390c.ts.net`  
Document status: Live verified snapshot **2026-08-25**

Related:
- `ops/CONFIG.md` — Configuration snapshot
- `ops/RUNBOOK.md` — Operational procedures and checklists
- `WARP.md` — Agent operational guide

---

## 1. Identity & Network Access

| Parameter | Specification / Value |
| :--- | :--- |
| **Station Name** | `ss-pt-tv-1` |
| **Deployment Stage** | **TRL5** (Field operational baseline) |
| **Hostname** | `wera-ss-pt-tv-1` |
| **Primary Operator User** | `wera-admin` (member of `docker`, `sudo`) |
| **Tailscale IPv4** | `100.82.252.18` |
| **Tailscale FQDN** | `wera-ss-pt-tv-1.tailfb390c.ts.net` |
| **Local WLAN IP** | `192.168.1.132/24` (interface `wlan0`) |
| **Primary Ethernet** | `eno1` (Realtek RTL8125 2.5GbE controller) |
| **Wireless NIC** | MediaTek MT7922 (RZ616) Wi-Fi 6E 160MHz PCIe |
| **SSH (Tailnet)** | `ssh wera-admin@wera-ss-pt-tv-1.tailfb390c.ts.net` |

### Tailnet Exposure (Tailscale Serve)

| Entrypoint / Port | Backend Target | Purpose |
| :--- | :--- | :--- |
| `https://wera-ss-pt-tv-1.tailfb390c.ts.net/` | `http://127.0.0.1:11000` | Nextcloud Apache front-door |
| `https://wera-ss-pt-tv-1.tailfb390c.ts.net:8069/` | `http://127.0.0.1:8069` | Filantropia Odoo ERP |

---

## 2. Hardware Specification

### 2.1 System & Motherboard
- **Manufacturer / Vendor**: GEEKOM
- **Product Family / Model**: A Series / **GEEKOM A6**
- **Form Factor**: Ultra-compact Mini PC
- **BIOS Vendor**: American Megatrends International, LLC.
- **BIOS Version**: `2.38` (Build Date: `12/17/2024`)

### 2.2 Processor (CPU)
- **Processor Model**: **AMD Ryzen 7 6800H with Radeon Graphics**
- **Microarchitecture**: AMD Zen 3+ (Rembrandt, 6nm TSMC process)
- **Core / Thread Count**: **8 physical cores / 16 threads** (SMT enabled)
- **Base Frequency**: 400 MHz (low-power power-saving state)
- **Max Boost Frequency**: **4.785 GHz**
- **Caches**:
  - L1d Cache: 256 KiB (8 x 32 KiB)
  - L1i Cache: 256 KiB (8 x 32 KiB)
  - L2 Cache: 4 MiB (8 x 512 KiB)
  - L3 Cache: **16 MiB** (1 x 16 MiB shared)
- **Virtualization**: AMD-V (`svm` hardware virtualization active)
- **Key Instruction Extensions**: AVX, AVX2, FMA3, BMI1, BMI2, AES-NI, SHA-NI, SSE4.1/4.2

### 2.3 Memory (RAM & Swap)
- **System Memory (Total)**: **~27 GiB** (`MemTotal: 28,477,784 kB` / ~28.4 GB reported)
- **Available Memory**: ~17.7 GiB free/available at standard idle
- **Swap Allocation**: **27.7 GiB** (`SwapTotal: 29,094,908 kB` on NVMe partition `/dev/nvme0n1p3`)

### 2.4 Graphics & AI Acceleration (GPU)
- **GPU Architecture**: **AMD Radeon 680M** (Integrated RDNA2, Rembrandt)
- **Device ID**: `[1002:1681]` (rev c7) / Subsystem `[1002:0123]`
- **Driver / Kernel Module**: `amdgpu`
- **VRAM Model**: Unified Memory Architecture (UMA shared system RAM)
- **AI Acceleration Engine**: Nextcloud AIO LocalAI container (`ghcr.io/docjyj/aio-local-ai-vulkan:v1`) utilizing Vulkan compute backend for local inference (Whisper STT & text models).

---

## 3. Storage Subsystem

### 3.1 Primary Solid-State Drive
- **Drive Model**: **KINGSTON OM8PGP41024N-A0**
- **Interface**: PCIe 4.0 x4 NVMe SSD
- **Capacity**: **953.9 GiB** (~1.0 TB)
- **Storage Type**: Non-rotational Solid State (`ROTA = 0`, `DISC-GRAN = 512B`)

### 3.2 Partition Table & Filesystems

```text
/dev/nvme0n1 (953.9 GiB NVMe SSD)
├── nvme0n1p1   976.0 MiB   vfat (FAT32)   UUID=6F0C-741E                         /boot/efi
├── nvme0n1p2   925.2 GiB   ext4           UUID=308e6ba2-5882-4217-a16f-124da9b071e6   / (root filesystem)
└── nvme0n1p3    27.7 GiB   swap           UUID=792ea8ea-9528-48b0-81f1-3fcf7f1e63a1   [SWAP]
```

### 3.3 Storage Usage & Mount Points
- **Root Filesystem (`/`)**: 910 GiB total capacity, ~151 GiB used, **~714 GiB free** (~18% utilization).
- **EFI System Partition (`/boot/efi`)**: 974 MiB total, ~6.1 MiB used.
- **Data Mount Note**: No secondary or LUKS-encrypted `/data` partitions are used; all container state, Docker layers, and Nextcloud datadir reside on the NVMe root filesystem (`/var/lib/docker`).

---

## 4. Operating System & Container Runtime

| Component | Version / Configuration |
| :--- | :--- |
| **Operating System** | **Debian GNU/Linux 13 (Trixie)** |
| **OS Version ID** | `13` (`DEBIAN_VERSION_FULL=13.2`) |
| **Kernel Release** | `6.12.57+deb13-amd64` (SMP PREEMPT_DYNAMIC) |
| **Architecture** | `x86_64` (64-bit) |
| **Cgroup Version** | Cgroups v2 (`systemd` driver) |
| **Docker Engine** | **29.1.2** (API 1.51) |
| **Containerd Engine** | `v2.2.0` |
| **Runc Version** | `1.3.4` |
| **Docker Storage Driver** | `overlayfs` (`/var/lib/docker/overlay2`) |
| **Docker Data-Root** | `/var/lib/docker` |

---

## 5. Software Stack Overview

### 5.1 Nextcloud AIO Stack
- Managed via Nextcloud AIO Mastercontainer (`ghcr.io/nextcloud-releases/all-in-one:latest`).
- **Nextcloud Server**: Version `33.0.7` running on PHP 8.3.
- **Database**: PostgreSQL (`nextcloud-aio-database`).
- **Cache & Locks**: Redis (`nextcloud-aio-redis`).
- **Web Server Front**: Apache (`nextcloud-aio-apache`) loopback-bound to `127.0.0.1:11000`.
- **Ancillary Microservices**:
  - `nextcloud-aio-talk` & `nextcloud-aio-talk-recording` (TURN/STUN on `:3478`)
  - `nextcloud-aio-collabora` (Office editing)
  - `nextcloud-aio-fulltextsearch` (Search indexer)
  - `nextcloud-aio-clamav` (Antivirus scanning)
  - `nextcloud-aio-imaginary` (Image preview processing)
  - `nextcloud-aio-whiteboard`
  - `nextcloud-aio-notify-push` (High-performance push daemon)
  - `nextcloud-aio-local-ai` (Vulkan-accelerated LocalAI on `:10078`)
  - `nextcloud-aio-fail2ban` & `nextcloud-aio-nextcloud-exporter` (`:9205`)
  - `nextcloud-aio-borgbackup-viewer` (`:5801`)

### 5.2 Odoo & Filantropia Services
- **Filantropia Odoo ERP**: Version `19.0` container (`filantropia-odoo`), mapped on `:8069`.
- **Database**: Dedicated PostgreSQL 16 instance (`filantropia-odoo-db`).
- **Outbound Email**: Proton Mail Bridge (`protonmail.service` on `127.0.0.1:1025`) proxied to Docker bridge gateways (`172.18.0.1:1025` and `172.19.0.1:1025`) via `protonmail-smtp-docker-proxy.service`.

---

## 6. Comparison with TRL4 Station "Frank"

| Feature | TRL5 (`ss-pt-tv-1`) | TRL4 ("Frank" / `ss-pt-sn-1`) |
| :--- | :--- | :--- |
| **Device Model** | GEEKOM A6 Mini PC | Custom Desktop Tower |
| **CPU Architecture** | AMD Ryzen 7 6800H (8C/16T, up to 4.78 GHz) | Intel Core i5-4440 (4C/4T, up to 3.10 GHz) |
| **System RAM** | **27 GiB DDR5** | **15.6 GiB DDR3** |
| **AI Acceleration** | AMD Radeon 680M iGPU (Vulkan) + CPU | NVIDIA GeForce GTX 1050 Ti (4GB dedicated VRAM, CUDA 12.4) |
| **Primary Storage** | 1 TB PCIe 4.0 NVMe SSD (single `/` ext4) | Dual SATA HDDs with LUKS encryption (`/data`, `/data-bulk`, `/mnt/nextcloud-data`) |
| **Power Profile** | Low TDP (~45W APU), field/solar ready | Desktop ATX PSU (~150-200W wall draw), grid required |
