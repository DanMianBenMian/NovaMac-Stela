#!/bin/bash
set -e
export CARGO_HOME=$HOME/.cargo
export RUSTUP_HOME=/opt/rustup
export PATH="/opt/rustup/toolchains/1.99.1-x86_64-unknown-linux-gnu/bin:/usr/lib/llvm-21/bin:$PATH"
BASE="/mnt/c/Users/单面本面/WorkBuddy/Claw/.tmp_stela/work/DanMianBenMian-Stela-b2594f3"
DST="$HOME/srcrepo"

cp "$BASE/crates/stela-drivers/src/input/ps2.rs"            "$DST/crates/stela-drivers/src/input/ps2.rs"
cp "$BASE/crates/stela-drivers/src/input/ps2/elantech.rs"   "$DST/crates/stela-drivers/src/input/ps2/elantech.rs"
cp "$BASE/crates/stela-drivers/src/input/device.rs"         "$DST/crates/stela-drivers/src/input/device.rs"
cp "$BASE/crates/stela-drivers/src/probe/platform.rs"       "$DST/crates/stela-drivers/src/probe/platform.rs"
cp "$BASE/crates/stela-drivers/src/probe/services.rs"       "$DST/crates/stela-drivers/src/probe/services.rs"
cp "$BASE/crates/stela-boot/src/engine/input.rs"            "$DST/crates/stela-boot/src/engine/input.rs"
cp "$BASE/crates/stela-boot/src/engine/network.rs"          "$DST/crates/stela-boot/src/engine/network.rs"
cp "$BASE/crates/stela-driver-net/src/realtek.rs"           "$DST/crates/stela-driver-net/src/realtek.rs"
cp "$BASE/crates/stela-boot/src/engine.rs"                   "$DST/crates/stela-boot/src/engine.rs"
cp "$BASE/crates/stela-boot-core/src/screen.rs"             "$DST/crates/stela-boot-core/src/screen.rs"
cp "$BASE/crates/stela-boot-core/src/stop_record.rs"        "$DST/crates/stela-boot-core/src/stop_record.rs"
cp "$BASE/crates/stela-boot-core/src/bundle_repair.rs"      "$DST/crates/stela-boot-core/src/bundle_repair.rs"
cp "$BASE/crates/stela-boot-core/src/dmroot_logo_64.rgb"    "$DST/crates/stela-boot-core/src/dmroot_logo_64.rgb"
cp "$BASE/crates/stela-boot/src/ui.rs"                       "$DST/crates/stela-boot/src/ui.rs"
cp "$BASE/crates/stela-boot/src/console/font.rs"             "$DST/crates/stela-boot/src/console/font.rs"
cp "$BASE/crates/stela-boot/src/console/hanzi.rs"            "$DST/crates/stela-boot/src/console/hanzi.rs"
cp "$BASE/crates/stela-boot/src/console/hanzi16.bin"         "$DST/crates/stela-boot/src/console/hanzi16.bin"
cp "$BASE/crates/stela-boot/src/console.rs"                   "$DST/crates/stela-boot/src/console.rs"
cp "$BASE/crates/stela-boot/src/wifi_prompt.rs"               "$DST/crates/stela-boot/src/wifi_prompt.rs"
cp "$BASE/crates/stela-boot/src/status.rs"                   "$DST/crates/stela-boot/src/status.rs"
cp "$BASE/crates/stela-boot/src/output.rs"                   "$DST/crates/stela-boot/src/output.rs"
echo "synced"

cd "$DST"
case "$1" in
  test)
    cargo test -p stela-boot-core screen::tests -- --nocapture
    ;;
  testall)
    cargo test -p stela-boot-core
    ;;
  check)
    cd "$DST/crates/stela-boot"
    cargo check --target x86_64-unknown-uefi --release
    ;;
  build)
    STELA_RELEASE=1 cargo xtask boot build --release
    ;;
  *)
    echo "usage: $0 test|check|build" >&2
    exit 2
    ;;
esac
