# NovaMac (Stela) 项目交接文档

> 交接时间：2026-11-27 20:00（北京时间）
> 交接原因：Claw 工作区不跑长任务；后续构建/部署/真机验证由接手 Agent 在独立工作区执行。
> 状态：**能启动到 macOS 桌面；图形能力与设备模型是主要短板；多个性能与输入问题待查。**

---

## 1. 项目与资产位置

| 资产 | 位置 |
|---|---|
| 源码工作树（构建用） | `C:\Users\单面本面\WorkBuddy\Claw\.tmp_stela\work\DanMianBenMian-Stela-b2594f3` |
| WSL 构建树 | `~/srcrepo`（WSL `Ubuntu-24.04`） |
| GitHub 源码仓库 | https://github.com/DanMianBenMian/NovaMac-Stela （`main`） |
| 托管主页 | https://danmianbenmian.github.io/ ，NovaMac 页 https://danmianbenmian.github.io/novamac.html |
| Pages 仓库 | `DanMianBenMian/DanMianBenMian.github.io`（旧小写 URL 会重定向） |
| 部署目标 | `F:\EFI\BOOT\BOOTX64.EFI`，配置 `F:\EFI\stela\stela.cfg`、`choices.cfg`、`setup.json` |
| 构建/部署脚本 | `.tmp_stela/build_novamac.sh`、`.tmp_stela/deploy_novamac.py` |
| 品牌资源 | 桌面 `DM-ROOT.svg|png|ico`；仓库根 `assets/` |
| 历史日志 | `.tmp_stela/b29.log`（11-24 旧日志）、`.tmp_stela/b30.log`/`b31.log`（11-27 新日志） |

**当前部署状态**
- EFI SHA256：`6d53128bf8578eb48094ff50108f47c19ce68f673fb45de4e964ddb5a18012f9`
- `setup.json.stela_version` = `6d53128bf8578eb4`
- `stela.cfg` 与 `choices.cfg` 两条启动项均带 `--no-bluetooth`（见第 5 节的覆盖坑）
- 备份：`C:\Users\单面本面\WorkBuddy\Claw\.tmp_stela\efi_backup\BOOTX64.pre-novamac-20261127-192230`（同名 `.cfg` / `.version`）
- 更早备份：`BOOTX64.pre-novamac-20261125-180213`（上个 NovaMac）、`BOOTX64.pre-novamac-20261125-172557`（原始 Stela，hash `2adfcf…`）

---

## 2. 已完成的改动（不要重复做）

### 2.1 品牌与启动页
- 名称 `Stela` → `NovaMac`，EFI 内置 logo 换成 DM-ROOT 64×64 位图（`dmroot_logo_64.rgb`）。
- 安静启动页：导航只显示阶段 `n/5` + 当前步骤；完整日志仍写 UART 和 `boot.log`，出错才展开屏幕。
- 真像素进度条（灰底蓝条，`console.rs::bar()`），前期来回滚动，文件复制阶段按真实字节数填充。
- 中文菜单字形（`hanzi.rs` + `hanzi16.bin`）。

### 2.2 WiFi 默认开启
- `Options::default()` 中 `guest_network` / `wifi_prompt` 设为 `true`（仅仓库副本；工作树保持原值，靠 cfg 显式开关）。
- 配置模板 `config/stela.cfg.example` 带 `--wifi-prompt --guest-network`。

### 2.3 性能第一刀：`--no-bluetooth`
- 新增启动选项（`options.rs` / `options/parse.rs` / 序列化 / `options/tests.rs` 往返测试），默认 `false`。
- `start.rs` 中该开关打开时不建模蓝牙控制器，日志写 `GUEST BLUETOOTH off: --no-bluetooth`。
- 动机：b29 日志有 `HOST SERVICE SLOW part=bluetooth us=203913` 一次 204ms 卡顿。
- 仓库提交 `9ecee0e`；`choices.cfg` 修复提交 `e80912b5d62f`。

### 2.4 网站与仓库文档
- 新建 https://danmianbenmian.github.io/novamac.html ，复用 `html-app-build.html` 的完整 head（design skin + 毛玻璃 + DM-ROOT favicon），最小补丁并入主页三卡布局。
- 仓库根 README 顶部放 DM-ROOT logo；两个子树 README 从上游原文重写为 NovaMac 版。

---

## 3. 硬结论与证据（避免重复踩坑）

### 3.1 翻译不是当前瓶颈
b29（11-24 完整启动）日志：
```
PES SHARE ... all:39/35/2/0/22   (idle/guest/translate/sync/other %)
PES SHARE ... all:52/26/3/0/19
CODE CACHE again=30-43%
TRANSLATIONS ahead queued=8.8M dropped=5.9M merge_read_mb=4205
```
`stela-boot-core/src/load_lines.rs:29` 定义 `other` = 引擎中不在 guest/translate/sync/idle 的时间（退出、设备模型、宿主服务）。translate 仅 2–5%，**不要在 JIT 里继续抠**，收益上限 1–2%。

### 3.2 `BEAT COST` 不能当引擎耗时
`stela-boot/src/engine/run.rs:1705` 的 `BeatCost` 是**打统计报告自身花的微秒数**（`processors=300us` 等），不是引擎工作时间。

### 3.3 上一刀没生效的真实原因（已修）
`choice.rs:608` 使用**启动选择条目的 options** 覆盖 `stela.cfg`。`choices.cfg` 的 `macOS` / `Install macOS` 两条各带完整 options 串，只改 `stela.cfg` 无效。现已把 `--no-bluetooth` 追加到两处 choices（ESP + 仓库）。**以后改启动参数必须同时改 `stela.cfg` 和 `choices.cfg`。**

### 3.4 Apple8 GPU family 不能"补支持"
`crates/stela-driver-gpu/src/metal/capabilities.rs` 头部明确：能力必须同时由 Vulkan 驱动、AIR 编译器、Metal 层三者提供；Apple1–Apple7 + Metal3 是有依据认领的；**Apple8 以后和 Metal4 依赖 Apple 架构，是显式 gap**（`self.gap("Apple GPU families from Apple8", Cause::AppleArchitecture)`，1711 行；测试 207 行断言 `!supports_family(Apple8)`）。这里没有可补齐的特性表，强行返回 true 等于谎报架构能力，会带来未实现指令/格式的执行路径。

⚠️ **修正上一条口头结论**：日志里的 `GPU REFUSED ... Apple8 ... this device does not claim it` 是能力查询的**正常否定回答并被记录**，不能据此断言"设置卡是因为 Apple8 被拒"。这个因果未经证实，接手时不要沿用它。

### 3.5 DCP 卡顿的真实读数怎么解释
b31（11-27 新 EFI，但当时 `--no-bluetooth` 被覆盖未生效）：
```
DCP PACING presented=36/10s  burst_fps=36.7  gaps=1:19/2:11/3:1/4-7:2/8+:2
          turnaround max=3654.2 ms  gpu_ms=7.05/33.11  composed=gpu:36/cpu:0
          fence_waits=31  ahead_of_gpu=0
```
- `stela-soc/src/dcp/iomfb.rs:315`：`turnaround` = guest AP 收到 swap 完成回答后，**过多久才提交下一帧**。最长 3.65s 说明瓶颈在 guest 侧出帧节奏，不在 Stela 的单帧合成（GPU 只要 7ms）。
- `gaps=8+:2` 是两次 ≥8 个刷新周期的长时间空档；静止画面本来帧少，但"打开设置/切页卡"对应这些空档。
- 该日志窗口结束时 guest 还在 installer 环境（`GUEST SESSION clients=[WindowServer, Installer Progress, MenuBarAgent]`），没有覆盖用户实际操作 Settings 的时间段。**必须重抓一段"打开设置→切页"期间的日志**才能定论。

---

## 4. 未解决问题与建议路径

### 4.1 设置应用打开/切页卡顿（优先级最高）
**已知**：不是翻译（2%），不是单帧 GPU（7ms），是 guest 提交帧的空档 / turnaround 最长 3.65s。
**待验证假设**（按优先级）：
1. guest 侧合成线程在等锁/等输入/等 GPU 完成回答 → 需要操作期间的 `PES SHARE`、`HOST SERVICE`、`DCP PACING` 同窗口对照。
2. swap 完成回答到 AP 的唤醒路径有延迟 → 检查 `iomfb.rs` 中 `completion_answered` / `D588` vsync 通知的发送条件。
3. `--display-size 1920x1200`（当前 2560×1600）可少 44% 像素，作为低风险对照实验；语法 `options.rs:40`，但**同样要写进 choices.cfg**。

**不要做**：不要为了消除 `GPU REFUSED` 去 claim Apple8/Metal4（见 3.4）。

### 4.2 系统密码输入被拒
用户报告：锁屏密码正确，进系统改设置时输入被拒。
**已排除**：`keyboard.rs` 的 Set1→Set2→Linux keycode→HID usage 映射正确（数字 1/0 → `0x1e`/`0x27`）；`INPUT TIMES ... dropped=0`；无 `loginwindow` 认证失败行。
**判据实验**：让用户在任意文本框输入同一串数字，看显示是否正确。
- 显示正确 → 不是输入链路，查 macOS 账户/FileVault/管理员密码语义。
- 显示错误/多/少 → 查 USB 2.4G 接收器与 i8042 是否双路上报同一次按键（`start.rs` 同时建两个输入设备）。
⚠️ 用户密码值不得写入任何文档/日志/记忆。

### 4.3 WiFi（AX211 / `8086:51f0`）
`Refused("setup")` 精确位置：`link.rs:766` → `boot/ax200.rs:113` 的 `begin_ax200_setup` 要求 `Family::Ax200`。AX211 在 `identity.rs:174` 被识别为 `Family::Ax210`，`attach.rs:202` 走 `start_ax210` 的 context-v2 启动，但**后面没有 AX210 的 RX 队列配置状态机**。绕开门禁 = 猜固件命令，不做。需要 AX210 队列配置规范或真机日志闭环。

### 4.4 磁盘 staged 等待
b29 出现过 `HOST DISK STAGED owed=303/1299525/901951`（1.3s 等待、单次 902ms）与 `HOST DISK IO ... discard=617/102193100KiB`（102GB TRIM）。机制在 `stela-boot-core/src/staged_disk.rs:427` `step_due()` 和 `stela-boot/src/engine/storage.rs:1233` `FALLBACK_MILLIS=1`。需要新日志确认是否复现。

---

## 5. 构建 / 部署 / 回滚（长任务请在独立工作区执行）

**环境坑**
- WSL 非登录 shell 没有 cargo/clang：`build_novamac.sh` 内已显式设置 `RUSTUP_HOME=/opt/rustup`、`PATH=/opt/rustup/toolchains/1.99.1-…/bin:/usr/lib/llvm-21/bin`。
- Git Bash 调 WSL 的 `/mnt/c/...` 必须加 `MSYS_NO_PATHCONV=1`。
- Windows Git 默认拒绝超长路径（Stela 深层测试目录）：`git config core.longpaths true`；`core.autocrlf false` 避免上万条换行警告。
- GitHub git push 有时被代理拦、有时可用；失败两次后改走 REST Contents API，不要在 Claw 里反复重试。

**命令**
```bash
# 同步工作树 → WSL 构建树并做检查/构建
MSYS_NO_PATHCONV=1 wsl -d Ubuntu-24.04 -- bash \
  "/mnt/c/Users/单面本面/WorkBuddy/Claw/.tmp_stela/build_novamac.sh" check
MSYS_NO_PATHCONV=1 wsl -d Ubuntu-24.04 -- bash \
  "/mnt/c/Users/单面本面/WorkBuddy/Claw/.tmp_stela/build_novamac.sh" build

# 单测（快）
... build_novamac.sh testall        # 1096 passed / 2 doc tests 是基线

# 部署（自动备份 EFI + cfg + version）
cd C:/Users/单面本面/WorkBuddy/Claw/.tmp_stela
py -3 deploy_novamac.py --dry <new.efi>
py -3 deploy_novamac.py --apply <new.efi>

# 回滚一步（包含 cfg）；回到原始 Stela 需指定旧备份名
py -3 deploy_novamac.py --rollback --force
py -3 deploy_novamac.py --rollback BOOTX64.pre-novamac-20261125-172557 --force
```

**红线**
- 任何改 EFI / 分区 / NVRAM 前先确认备份存在；回滚命令给在手边。
- RyConsole 源码修改权归 Ryan 本人，不得私自改；需要改就走内部论坛 `E:/root/analysis/tools/_forum_post.py`。
- 不在 Claw 工作区跑 6 分钟级构建/长任务；接手 Agent 用独立工作区。
- 不谎报 GPU 能力、不猜固件命令绕过门禁、不把用户密码写进任何持久文件。

---

## 6. 接手后的第一步（建议）

1. 让用户重启一次并抓取**操作 Settings 期间**的 `F:\EFI\stela\boot.log`，确认 `GUEST BLUETOOTH off` 是否出现、DCP turnaround 是否仍 3.65s。
2. 做文本框数字判别实验，定位密码问题是不是输入链路。
3. 若确认 turnaround 是 guest 侧出帧慢，先试 `--display-size 1920x1200`（写进 `choices.cfg` 两条），用同一组指标做 A/B；不要先动 GPU family 声明。
4. 所有改动走"改源码 → 单测 → check → build → 备份 → 部署 → 新日志验证"闭环，任何一步失败就回滚。
