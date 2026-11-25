#!/usr/bin/env python3
"""Turn on the guest-network bridge for one supervised test boot.

Starts from the frozen baseline (never from whatever is on the ESP now), so
running this twice gives the same bytes, and `baseline.py --restore` undoes it.

What it adds, and why each word:

  --wifi-prompt     the picker runs before the engine, so the passphrase in
                    wifi.key is the one typed now -- not a leftover of unknown
                    provenance -- and is remembered in wifi.list.
  --guest-network   Stela bridges the host adapter to the guest as a USB
                    CDC-ECM adapter, which macOS drives with its own driver.

Run:  py -3 enable_guest_net.py --dry
      py -3 enable_guest_net.py --apply
      py -3 enable_guest_net.py --revert     (same as baseline.py --restore)
"""
import json
import sys

ESP = "F:/EFI/stela/"
HERE = "C:/Users/单面本面/WorkBuddy/Claw/.tmp_stela/"
BASE = HERE + "baseline/"

FILES = {
    "stela.cfg": ESP + "stela.cfg",
    "choices.cfg": ESP + "choices.cfg",
    "setup.json": ESP + "setup.json",
}

ANCHOR = b"--guest-pes 8"
ADD = b" --wifi-prompt --guest-network"


def read(path):
    with open(path, "rb") as f:
        return f.read()


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)


def add_words(data: bytes, only_prefix: bytes = None) -> bytes:
    lines = data.split(b"\r\n") if b"\r\n" in data else data.split(b"\n")
    sep = b"\r\n" if b"\r\n" in data else b"\n"
    for i, line in enumerate(lines):
        if only_prefix is not None and not line.startswith(only_prefix):
            continue
        if ANCHOR in line and ADD.strip() not in line:
            lines[i] = line.replace(ANCHOR, ANCHOR + ADD, 1)
    return sep.join(lines)


def main(argv):
    if "--revert" in argv:
        from subprocess import run

        return run([sys.executable, HERE + "baseline.py", "--restore"]).returncode

    out = {}
    for name in FILES:
        base = read(BASE + name)
        if name == "choices.cfg":
            new = add_words(base, only_prefix=b"macOS\t")
        else:
            new = add_words(base)
        if name == "setup.json":
            new = new.replace(b'"wifi_prompt": false', b'"wifi_prompt": true')
            a = json.loads(base.decode("utf-8"))
            b = json.loads(new.decode("utf-8"))
            assert {k for k in a if a[k] != b.get(k)} <= {"options", "wifi_prompt"}
            assert b["wifi_prompt"] is True
            assert "--wifi-prompt" in b["options"] and "--guest-network" in b["options"]
            print("options:", b["options"].strip()[-90:])
        out[name] = new
        print(f"{name}: {len(base)} -> {len(new)}")

    for name in FILES:
        assert b"--guest-network" in out[name], name
    print("assert: both words present in every file")

    if "--apply" not in argv:
        print("(dry run)")
        return 0
    for name, dst in FILES.items():
        write(dst, out[name])
    print("written -- revert with:  py -3 baseline.py --restore")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
