"""Tests for machine spoof + anti-vm (no real Qoder install required)."""

from __future__ import annotations

import json
from pathlib import Path

from qoder_autopilot.infra.anti_vm import check_vm, format_vm_report
from qoder_autopilot.infra.machine_spoof import (
    read_machine_id,
    spoof_machine,
)


def test_spoof_creates_machineid(tmp_path: Path):
    desktop = tmp_path / "Qoder"
    cli = tmp_path / "cli"
    result = spoof_machine(
        data_dir=desktop,
        cli_dir=cli,
        require_stopped=False,
    )
    mid = result["ids"]["machine_id"]
    assert (desktop / "machineid").read_text() == mid
    assert (cli / "machineid").read_text() == mid
    storage = json.loads((desktop / "User/globalStorage/storage.json").read_text())
    assert storage["telemetry.machineId"] == result["ids"]["machine_id_hash"]
    assert storage["telemetry.devDeviceId"] == result["ids"]["dev_device_id"]
    assert (desktop / "hardware_detection.json").exists()
    assert read_machine_id(desktop) == mid


def test_spoof_cli_only(tmp_path: Path):
    cli = tmp_path / "cli"
    result = spoof_machine(
        cli_dir=cli,
        include_desktop=False,
        require_stopped=False,
    )
    assert result["desktop"] is None
    assert (cli / "device.json").exists()


def test_spoof_clears_login_keys(tmp_path: Path):
    desktop = tmp_path / "Qoder"
    storage = desktop / "User/globalStorage/storage.json"
    storage.parent.mkdir(parents=True)
    storage.write_text(
        json.dumps(
            {
                "telemetry.machineId": "old",
                "auth.token": "secret",
                "login.session": "x",
                "keep.me": 1,
            }
        )
    )
    spoof_machine(data_dir=desktop, include_cli=False, require_stopped=False)
    data = json.loads(storage.read_text())
    assert "auth.token" not in data
    assert "login.session" not in data
    assert data["keep.me"] == 1
    assert data["telemetry.machineId"] != "old"


def test_anti_vm_returns_dict():
    info = check_vm()
    assert "is_vm" in info
    assert "reasons" in info
    assert isinstance(format_vm_report(info), str)
