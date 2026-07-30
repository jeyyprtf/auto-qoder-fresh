"""
Qoder machine identity spoof / reset.
Ported from itandelin/qoder-free + bunnysayzz/qoder-reset (file-level only).

Resets desktop data dir + CLI ~/.qoder so trial claim sees a "new" machine.
"""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import uuid
from pathlib import Path
from typing import Any

from ..utils.logger import log, log_ok

# Chromium/Electron residue that fingerprints the install
_CACHE_DIRS = (
    "Cache",
    "blob_storage",
    "Code Cache",
    "GPUCache",
    "DawnGraphiteCache",
    "DawnWebGPUCache",
    "ShaderCache",
    "DawnCache",
    "Dictionaries",
    "CachedData",
    "CachedProfilesData",
    "CachedExtensions",
    "IndexedDB",
    "CacheStorage",
    "WebSQL",
    "MediaCache",
)

_IDENTITY_NAMES = (
    "Network Persistent State",
    "TransportSecurity",
    "Trust Tokens",
    "Trust Tokens-journal",
    "SharedStorage",
    "SharedStorage-wal",
    "Local Storage",
    "Session Storage",
    "WebStorage",
    "Shared Dictionary",
    "Cookies",
    "Cookies-journal",
    "Login Credentials",
    "Login Data",
    "Login Data-journal",
    "Preferences",
    "Secure Preferences",
    "Local State",
    "DeviceMetadata",
    "HardwareInfo",
    "SystemInfo",
    "QuotaManager",
    "QuotaManager-journal",
    "Network Action Predictor",
    "AutofillStrikeDatabase",
    "AutofillStrikeDatabase-journal",
    "Feature Engagement Tracker",
    "Platform Notifications",
    "VideoDecodeStats",
    "OriginTrials",
    "BrowserMetrics",
    "SafeBrowsing",
    "Visited Links",
    "History",
    "History-journal",
    "cert_transparency_reporter_state.json",
    "NetworkDataMigrated",
)

_ID_FILES = (
    "deviceid",
    "hardware_uuid",
    "system_uuid",
    "platform_id",
    "installation_id",
    "cpu_id",
    "gpu_id",
    "memory_id",
    "board_serial",
    "bios_uuid",
)

_LOGIN_KEY_FRAGMENTS = (
    "login",
    "auth",
    "token",
    "credential",
    "session",
    "nonce",
    "challenge",
    "account",
)


def qoder_data_dir() -> Path:
    """Desktop/Electron app data directory (platform-aware)."""
    home = Path.home()
    system = platform.system()
    if system == "Windows":
        return home / "AppData" / "Roaming" / "Qoder"
    if system == "Darwin":
        return home / "Library" / "Application Support" / "Qoder"
    # Linux (+ common Electron fallbacks)
    for p in (home / ".config" / "Qoder", home / ".qoder-desktop"):
        if p.exists():
            return p
    return home / ".config" / "Qoder"


def qoder_cli_dir(config_dir: Path | str | None = None) -> Path:
    """CLI config home (~/.qoder or isolated override)."""
    if config_dir:
        return Path(config_dir).expanduser()
    return Path.home() / ".qoder"


def is_qoder_running() -> list[int]:
    """Return PIDs of running Qoder / qodercli processes (best-effort)."""
    import subprocess

    pids: list[int] = []
    try:
        out = subprocess.check_output(["ps", "ax", "-o", "pid=,comm=,args="], text=True)
    except (OSError, subprocess.CalledProcessError):
        return pids
    for line in out.splitlines():
        low = line.lower()
        if "qoder" not in low:
            continue
        # skip our own tooling
        if "qoder-autopilot" in low or "qoder_autopilot" in low:
            continue
        parts = line.split(None, 1)
        try:
            pids.append(int(parts[0]))
        except (ValueError, IndexError):
            continue
    return pids


def _rm(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _new_ids() -> dict[str, str]:
    mid = str(uuid.uuid4())
    return {
        "machine_id": mid,
        "machine_id_hash": _sha256(mid),
        "dev_device_id": str(uuid.uuid4()),
        "sqm_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "installation_id": str(uuid.uuid4()),
        "client_id": str(uuid.uuid4()),
        "anonymous_id": str(uuid.uuid4()),
        "hardware_id": str(uuid.uuid4()),
        "platform_id": str(uuid.uuid4()),
    }


def _write_machine_files(root: Path, ids: dict[str, str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "machineid").write_text(ids["machine_id"])
    for name in _ID_FILES:
        (root / name).write_text(str(uuid.uuid4()))


def _patch_storage_json(root: Path, ids: dict[str, str], clear_login: bool) -> None:
    storage = root / "User" / "globalStorage" / "storage.json"
    storage.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {}
    if storage.exists():
        try:
            data = json.loads(storage.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}

    data.update(
        {
            "telemetry.machineId": ids["machine_id_hash"],
            "telemetry.devDeviceId": ids["dev_device_id"],
            "telemetry.sqmId": ids["sqm_id"],
            "telemetry.sessionId": ids["session_id"],
            "telemetry.installationId": ids["installation_id"],
            "telemetry.clientId": ids["client_id"],
            "telemetry.anonymousId": ids["anonymous_id"],
            "machineId": ids["machine_id_hash"],
            "deviceId": ids["dev_device_id"],
            "installationId": ids["installation_id"],
            "hardwareId": ids["hardware_id"],
            "platformId": ids["platform_id"],
        }
    )

    if clear_login:
        for key in list(data):
            low = key.lower()
            if any(f in low for f in _LOGIN_KEY_FRAGMENTS):
                del data[key]

    storage.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def _clean_caches(root: Path) -> int:
    n = 0
    for name in _CACHE_DIRS:
        if _rm(root / name):
            n += 1
    shared = root / "SharedClientCache"
    if shared.exists():
        for name in (".info", ".lock", "mcp.json", "server.json", "auth.json"):
            if _rm(shared / name):
                n += 1
        for p in shared.glob("tmp*"):
            if _rm(p):
                n += 1
        if _rm(shared / "cache"):
            n += 1
    return n


def _clean_identity(root: Path) -> int:
    n = 0
    for name in _IDENTITY_NAMES:
        if _rm(root / name):
            n += 1
    return n


def _fake_hardware(root: Path) -> None:
    """Write decoy hardware JSON (best-effort anti-fingerprint)."""
    system = platform.system()
    if system == "Darwin":
        hw = {
            "cpu": {"name": "Apple M3 Pro", "cores": 12, "threads": 12},
            "gpu": {"name": "Apple M3 Pro GPU", "memory": "24GB"},
            "memory": {"total": "32GB", "type": "LPDDR5"},
        }
    elif system == "Windows":
        hw = {
            "cpu": {"name": "Intel Core i7-13700K", "cores": 16, "threads": 24},
            "gpu": {"name": "NVIDIA GeForce RTX 4070", "memory": "12GB"},
            "memory": {"total": "32GB", "type": "DDR5"},
        }
    else:
        # Prefer bare-metal looking profile on Linux/VPS
        hw = {
            "cpu": {"name": "AMD Ryzen 7 7700X", "cores": 8, "threads": 16},
            "gpu": {"name": "NVIDIA GeForce RTX 4060", "memory": "8GB"},
            "memory": {"total": "32GB", "type": "DDR5"},
        }
    (root / "hardware_detection.json").write_text(json.dumps(hw, indent=2))
    (root / "device_capabilities.json").write_text(
        json.dumps({"capabilities": ["gpu_acceleration", "webgl2"]})
    )
    (root / "system_features.json").write_text(
        json.dumps({"features": ["avx2", "sse4", "aes_ni"]})
    )


def _spoof_cli_home(cli_dir: Path, ids: dict[str, str]) -> None:
    """Reset CLI auth/state under ~/.qoder (or isolated dir)."""
    cli_dir.mkdir(parents=True, exist_ok=True)
    # wipe auth-ish files; keep skills/memory optional dirs empty-safe
    for name in (
        "auth.json",
        "credentials.json",
        "token.json",
        "session.json",
        "device.json",
        "machineid",
        "machine_id",
    ):
        _rm(cli_dir / name)
    # common nested storage
    for sub in ("auth", "session", "cache", "tokens"):
        _rm(cli_dir / sub)
    (cli_dir / "machineid").write_text(ids["machine_id"])
    device = {
        "machineId": ids["machine_id"],
        "telemetryMachineId": ids["machine_id_hash"],
        "devDeviceId": ids["dev_device_id"],
    }
    (cli_dir / "device.json").write_text(json.dumps(device, indent=2))


def spoof_machine(
    *,
    data_dir: Path | str | None = None,
    cli_dir: Path | str | None = None,
    clear_login: bool = True,
    require_stopped: bool = True,
    include_cli: bool = True,
    include_desktop: bool = True,
) -> dict[str, Any]:
    """Full identity reset. Returns new id map.

    Raises RuntimeError if Qoder is running and require_stopped=True.
    """
    pids = is_qoder_running()
    if pids and require_stopped:
        raise RuntimeError(f"Qoder still running (PIDs: {pids}) — close it first")

    ids = _new_ids()
    result: dict[str, Any] = {"ids": ids, "desktop": None, "cli": None}

    if include_desktop:
        root = Path(data_dir).expanduser() if data_dir else qoder_data_dir()
        root.mkdir(parents=True, exist_ok=True)
        log(f"🖥️  Desktop data: {root}")
        _write_machine_files(root, ids)
        _patch_storage_json(root, ids, clear_login=clear_login)
        n_cache = _clean_caches(root)
        n_id = _clean_identity(root)
        _fake_hardware(root)
        result["desktop"] = {
            "path": str(root),
            "caches_cleaned": n_cache,
            "identity_cleaned": n_id,
        }
        log_ok(f"Desktop spoofed — machineid={ids['machine_id']}")

    if include_cli:
        cdir = qoder_cli_dir(cli_dir)
        log(f"💻 CLI config: {cdir}")
        _spoof_cli_home(cdir, ids)
        result["cli"] = {"path": str(cdir)}
        log_ok(f"CLI spoofed — machineid={ids['machine_id']}")

    return result


def read_machine_id(data_dir: Path | str | None = None) -> str | None:
    root = Path(data_dir).expanduser() if data_dir else qoder_data_dir()
    f = root / "machineid"
    if f.exists():
        return f.read_text().strip() or None
    return None
