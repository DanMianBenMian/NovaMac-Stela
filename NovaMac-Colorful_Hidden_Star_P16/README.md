<p align="center">
  <img src="../assets/DM-ROOT.png" alt="DM-ROOT" width="96"><br>
  <b>NovaMac — Colorful Hidden Star P16</b>
</p>

This is the machine-specific NovaMac tree for a **Colorful Hidden Star P16**
(i7-12650H / RTX 4060 / 32 GB). It is the same source as `../NovaMac/` plus the
configuration and helper scripts actually used on this PC. WiFi switches are
on by default here too.

> [!WARNING]
> Experimental. This directory contains **device identifiers** (ECID, disk
> GUIDs, `--guest-pes 8`) in `config/`. Consider redacting them before sharing.
> Back up data before changing partitions or NVRAM. See `../DISCLAIMER.md`.

## What is different from the generic tree

| Path | Purpose |
|---|---|
| `config/stela.cfg` | Boot options used on this machine: ECID `0x18c771abd9975026`, disk GUIDs, `--guest-pes 8`, `--wifi-prompt --guest-network`. |
| `config/choices.cfg` | Startup choice records. |
| `config/setup.json` | Installation record written by `stela setup`. |
| `tools/build_novamac.sh` | Sync the edited files into the WSL build tree and build the EFI. |
| `tools/deploy_novamac.py` | Deploy the EFI with backup + version sync; `--rollback` restores it. |
| `tools/gen_dmroot_logo.py` | Render `DM-ROOT.png` into the 64×64 RGB bitmap embedded in the EFI. |
| `tools/baseline.py`, `tools/enable_guest_net.py`, `tools/deploy_net.py` | The baseline/config workflow used during development. |

## Core technology

Same as the generic tree: a UEFI boot program with an arm64e → x86-64
translator, a Metal driver for NVIDIA GPUs, and a model of an M2 Mac mini
(Mac14,3). Quiet boot page with a real pixel progress bar; full logs still go
to the UART and `EFI/stela/boot.log`.

## WiFi reality on this machine

The adapter is AX211 / CNVio2 (`8086:51f0`). It is still refused by Stela's
`Family::Ax200` setup gate, so the default-on `--wifi-prompt` does not make
this card work. The usable network path is `--guest-network`, which bridges a
host adapter into the guest as a USB CDC-ECM/NCM Ethernet device. Bluetooth and
GPU acceleration are not guaranteed.

## Build

In WSL Ubuntu 24.04 (Rust 1.99.1, LLVM 21 with Clang/libclang):

```bash
export RUSTUP_HOME=/opt/rustup
export PATH="/opt/rustup/toolchains/1.99.1-x86_64-unknown-linux-gnu/bin:/usr/lib/llvm-21/bin:$PATH"
STELA_RELEASE=1 cargo xtask boot build --release
```

Or run `bash tools/build_novamac.sh build` from the repository root using the
included helper. The output is
`target/boot/x86_64-unknown-uefi/release/stela-deploy.efi`.

## Legal

Independent fork of Stela under GPL-2.0-or-later. No Apple software included.
See `../LICENSE`, `../NOTICE` and `../DISCLAIMER.md`.
