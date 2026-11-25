<p align="center">
  <img src="assets/DM-ROOT.png" alt="DM-ROOT" width="96"><br>
  <b>NovaMac (Stela)</b>
</p>

# NovaMac (Stela)

在普通 x86-64 PC 上启动 Apple Silicon macOS 的实验性翻译层。本项目是 [Stela](https://github.com/tylertms/Stela) 的续作与品牌化分支；上游作者已于 2026-11-22 清空代码并将仓库归档，本项目保留并继续维护其 GPL-2.0 代码。

> ⚠️ 实验性软件。仅供自有设备研究使用。请自行备份数据，不承诺任何设备可启动，也不承诺 WiFi / 蓝牙 / GPU 可用。详见 [DISCLAIMER.md](DISCLAIMER.md)。

## 目录结构

| 路径 | 内容 |
| --- | --- |
| `NovaMac/` | **通用源码**。只含通用补丁：DM-ROOT 品牌、安静启动页、图形进度条、中文菜单、触摸/网络通用修复。不含任何机器序列号、ECID 或磁盘 GUID。**默认开启 WiFi**（源码默认值 + `config/stela.cfg.example` 均带 `--wifi-prompt --guest-network`）。 |
| `NovaMac-Colorful_Hidden_Star_P16/` | **隐星 P16 专属源码**。在通用源码基础上附带本机 `config/stela.cfg`、`choices.cfg`、`setup.json` 与构建/部署脚本，ECID、磁盘 GUID、`--guest-pes 8` 均为该机实测值。同样默认开启 WiFi。 |
| `assets/` | DM-ROOT Logo（SVG / PNG / ICO）。 |
| `LICENSE` | 上游许可证原文（GPL-2.0-or-later / GPL-2.0-only / BSD-2-Clause 组合）。 |
| `DISCLAIMER.md` | 免责声明与上游关系说明。 |

两个目录都是**完整可构建的源码树**，不是补丁文件集合。构建产物（`target/`）未收录。

## 默认开启 WiFi

`crates/stela-boot-core/src/options.rs` 中 `Options::default()` 的 `guest_network` 与 `wifi_prompt` 已设为 `true`；配置模板也直接带这两个开关：

```text
--system --input --guest-pes <SOURCE_PES> --wifi-prompt --guest-network
```

- `--wifi-prompt`：启动时列出无线网卡供选择。
- `--guest-network`：把宿主可用网卡桥接为 guest 的 USB CDC-ECM/NCM 网卡，macOS 用原生 USB 以太网驱动。

**现实说明**：这两个开关只负责"启用与提示"，不代表所有网卡都能被驱动。AX211 / CNVio2（`8086:51f0`）在本版本中仍会被 `begin_ax200_setup()` 的 `Family::Ax200` 门禁拒绝；`--guest-network` 是目前真正可用的联网路径。无可用网卡时 Stela 会记录原因并让 macOS 无网络启动，不会因此 FATAL。

## 通用补丁清单

- `screen.rs`：内置 logo 改为 DM-ROOT 位图（64×64，生成脚本见 P16 目录 `tools/gen_dmroot_logo.py`）。
- `ui.rs` / `status.rs` / `console.rs`：品牌名 NovaMac；启动默认静默页（阶段 `n/5` + 当前步骤），真实像素进度条（灰底蓝条，前期来回滚动、文件复制阶段按字节数填充），出错才展开日志尾部。
- `output.rs` / `stop_record.rs` / `bundle_repair.rs` / `engine.rs`：用户可见文案统一为 NovaMac；机器解析用的 `STELA FATAL` / `STELA STOPPED` token 和 `stela log` 命令保持不变。
- 中文菜单字形表（`console/hanzi.rs` + `hanzi16.bin`）与 WiFi 启用默认值。
- 通用输入/网络/磁盘驱动修复：触摸板识别、网卡 link 等待缩短、r8169 步骤诊断等。

## 隐星 P16 专属内容

机型：Colorful Hidden Star P16（i7-12650H / RTX 4060 / 32 GB），客户机 macOS 26B123 / Mac14,3。

- `config/stela.cfg`：该机实测参数，包含 ECID `0x18c771abd9975026`、磁盘 GUID、`--guest-pes 8`、WiFi 开关。
- `config/setup.json`、`config/choices.cfg`：该机安装记录与启动选择。
- `tools/`：本机的 EFI 构建、部署、回滚与图标生成脚本。

⚠️ P16 目录含**设备标识**，公开发布/分享前请自行评估是否要脱敏。

## 构建

在 WSL Ubuntu 24.04 中（需要 Rust 1.99.1、clang、libclang）：

```bash
cd NovaMac                       # 或 NovaMac-Colorful_Hidden_Star_P16
export RUSTUP_HOME=/opt/rustup
export PATH="/opt/rustup/toolchains/1.99.1-x86_64-unknown-linux-gnu/bin:/usr/lib/llvm-21/bin:$PATH"
STELA_RELEASE=1 cargo xtask boot build --release
```

产物：`target/boot/x86_64-unknown-uefi/release/stela-deploy.efi`。

注意：本机 git smart-HTTP 可能被代理拦截，仓库内容通过 GitHub REST API 推送；这不影响源码本身构建。

## 致谢与许可

基于 Tyler Muszynski 的 Stela（GPL-2.0-or-later）。上游已归档，作者声明不认可 fork/续作；本项目尊重其声明，仅陈述事实：代码在 GPL 许可下继续维护，不构成对上游的背书。完整许可证见 `LICENSE` 与各 `LICENSES/`、`NOTICE` 文件。
