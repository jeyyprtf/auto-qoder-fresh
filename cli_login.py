"""
Qoder CLI login / status helpers (no desktop app).

Auth modes (official):
  1. Interactive: `qodercli login` (may open browser / print URL)
  2. Headless:    QODER_PERSONAL_ACCESS_TOKEN=<pat> qodercli ...

Claim trial flow (friend):
  spoof machine → qodercli login on fresh machine id → trial attaches → mint PAT
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..utils.logger import log, log_err, log_ok, log_warn

# Common binary names (global npm + cn variant)
_CLI_NAMES = ("qodercli", "qoderclicn", "qoder")


def find_qodercli() -> str | None:
    for name in _CLI_NAMES:
        path = shutil.which(name)
        if path:
            return path
    return None


def _run(
    args: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: str | None = None,
    timeout: int = 120,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=timeout,
        input=input_text,
        check=False,
    )


def cli_env(
    *,
    pat: str | None = None,
    config_dir: Path | str | None = None,
    extra: dict[str, str] | None = None,
) -> dict[str, str]:
    env = os.environ.copy()
    if pat:
        env["QODER_PERSONAL_ACCESS_TOKEN"] = pat
    if config_dir:
        # OmniRoute / community convention for isolated sessions
        cdir = str(Path(config_dir).expanduser())
        env["QODER_CLI_CONFIG_DIR"] = cdir
        env["QODER_CONFIG_DIR"] = cdir
        Path(cdir).mkdir(parents=True, exist_ok=True)
    if extra:
        env.update(extra)
    return env


def cli_status(
    *,
    pat: str | None = None,
    config_dir: Path | str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    """Run `qodercli status` (or /status via -p fallback)."""
    binary = find_qodercli()
    if not binary:
        return {"ok": False, "error": "qodercli not found — npm i -g @qoder-ai/qodercli"}

    env = cli_env(pat=pat, config_dir=config_dir)
    # try subcommand first, then non-interactive prompt
    for args in (
        [binary, "status"],
        [binary, "--print", "status"],
        [binary, "-p", "/status"],
    ):
        try:
            proc = _run(args, env=env, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "status timed out"}
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode == 0 or "plan" in out.lower() or "email" in out.lower():
            return {
                "ok": proc.returncode == 0,
                "code": proc.returncode,
                "output": out.strip(),
                "cmd": args,
            }
    return {
        "ok": False,
        "code": proc.returncode,
        "output": out.strip(),
        "error": "status failed",
    }


def cli_login(
    *,
    config_dir: Path | str | None = None,
    timeout: int = 300,
    open_browser: bool = True,
) -> dict[str, Any]:
    """Start `qodercli login`.

    On headless hosts this usually prints a URL — user completes auth in any browser.
    No Qoder desktop required.
    """
    binary = find_qodercli()
    if not binary:
        return {"ok": False, "error": "qodercli not found — npm i -g @qoder-ai/qodercli"}

    env = cli_env(config_dir=config_dir)
    if not open_browser:
        env.setdefault("BROWSER", "echo")  # ponytail: prevent xdg-open hang on VPS
        env.setdefault("NO_BROWSER", "1")

    log(f"🔑 Running: {binary} login")
    try:
        # inherit stdio so user sees device URL / prompts
        proc = subprocess.run(
            [binary, "login"],
            env=env,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"login timed out after {timeout}s"}
    except FileNotFoundError:
        return {"ok": False, "error": f"binary missing: {binary}"}

    ok = proc.returncode == 0
    if ok:
        log_ok("qodercli login finished (exit 0)")
    else:
        log_err(f"qodercli login exit={proc.returncode}")
    return {"ok": ok, "code": proc.returncode}


def cli_usage(
    *,
    pat: str | None = None,
    config_dir: Path | str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    binary = find_qodercli()
    if not binary:
        return {"ok": False, "error": "qodercli not found"}
    env = cli_env(pat=pat, config_dir=config_dir)
    try:
        proc = _run([binary, "-p", "/usage"], env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "usage timed out"}
    out = (proc.stdout or "") + (proc.stderr or "")
    return {"ok": proc.returncode == 0, "code": proc.returncode, "output": out.strip()}


def claim_with_cli(
    *,
    config_dir: Path | str | None = None,
    spoof: bool = True,
    open_browser: bool = True,
    login_timeout: int = 300,
) -> dict[str, Any]:
    """Spoof (optional) → qodercli login → status check.

    PAT minting is still manual at qoder.com → Integrations (seller model).
    """
    from ..infra.anti_vm import check_vm, format_vm_report
    from ..infra.machine_spoof import spoof_machine

    result: dict[str, Any] = {"vm": check_vm()}
    if result["vm"]["is_vm"]:
        log_warn(format_vm_report(result["vm"]))
        log_warn("Trial may freeze on obvious VMs — bare metal / good spoof helps")

    if spoof:
        try:
            result["spoof"] = spoof_machine(
                cli_dir=config_dir,
                include_cli=True,
                include_desktop=True,
            )
        except RuntimeError as e:
            log_err(str(e))
            result["ok"] = False
            result["error"] = str(e)
            return result

    login = cli_login(
        config_dir=config_dir,
        timeout=login_timeout,
        open_browser=open_browser,
    )
    result["login"] = login
    if not login.get("ok"):
        result["ok"] = False
        result["error"] = login.get("error") or "login failed"
        return result

    status = cli_status(config_dir=config_dir)
    result["status"] = status
    result["ok"] = bool(status.get("ok") or login.get("ok"))
    if result["ok"]:
        log_ok("Claim path done — mint PAT at qoder.com → Account → Integrations")
        log("   Buyer uses: export QODER_PERSONAL_ACCESS_TOKEN=<pat>")
    return result
