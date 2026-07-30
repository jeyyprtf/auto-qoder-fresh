"""
Lightweight VM / hypervisor heuristics.

Friend flow: spoof machine → ensure not detected as VM → CLI login.
We only *detect* and report; spoofing DMI needs root and is host-specific.
"""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Any


_VM_DMI_MARKERS = (
    "vmware",
    "virtualbox",
    "vbox",
    "kvm",
    "qemu",
    "xen",
    "bochs",
    "hyper-v",
    "microsoft corporation",
    "parallels",
    "bhyve",
    "amazon ec2",
    "google compute",
    "digitalocean",
    "linode",
    "hetzner",
)

_VM_CPU_MARKERS = (
    "hypervisor",
    "qemu",
    "kvm",
    "vmware",
    "virtualbox",
)


def _read_text(path: str | Path, limit: int = 4096) -> str:
    try:
        return Path(path).read_text(errors="ignore")[:limit].lower()
    except OSError:
        return ""


def _dmi_blob() -> str:
    if platform.system() != "Linux":
        return ""
    parts: list[str] = []
    base = Path("/sys/class/dmi/id")
    for name in (
        "product_name",
        "sys_vendor",
        "board_vendor",
        "bios_vendor",
        "product_version",
        "chassis_vendor",
    ):
        parts.append(_read_text(base / name))
    return " ".join(parts)


def _cpuinfo() -> str:
    if platform.system() != "Linux":
        return ""
    return _read_text("/proc/cpuinfo")


def _systemd_virt() -> str:
    if platform.system() != "Linux":
        return ""
    import subprocess

    try:
        out = subprocess.check_output(
            ["systemd-detect-virt"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).strip()
        return out
    except (OSError, subprocess.SubprocessError):
        return ""


def check_vm() -> dict[str, Any]:
    """Return detection summary. is_vm=True means likely virtualized."""
    reasons: list[str] = []
    dmi = _dmi_blob()
    cpu = _cpuinfo()
    virt = _systemd_virt()

    if virt and virt not in ("none", ""):
        reasons.append(f"systemd-detect-virt={virt}")

    for m in _VM_DMI_MARKERS:
        if m in dmi:
            reasons.append(f"dmi contains '{m}'")
            break

    for m in _VM_CPU_MARKERS:
        if m in cpu:
            reasons.append(f"cpuinfo contains '{m}'")
            break

    # container signals
    if Path("/.dockerenv").exists():
        reasons.append("dockerenv present")
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        reasons.append("kubernetes env")
    if _read_text("/proc/1/cgroup").count("docker") or "containerd" in _read_text(
        "/proc/1/cgroup"
    ):
        reasons.append("cgroup container")

    return {
        "is_vm": bool(reasons),
        "reasons": reasons,
        "virt": virt or "unknown",
        "platform": platform.system(),
        "machine": platform.machine(),
    }


def format_vm_report(info: dict[str, Any] | None = None) -> str:
    info = info or check_vm()
    if not info["is_vm"]:
        return "looks like bare metal (no VM markers)"
    return "VM/container likely: " + "; ".join(info["reasons"])
