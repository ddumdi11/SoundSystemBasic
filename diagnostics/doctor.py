from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


def _is_venv() -> bool:
    return (hasattr(sys, "real_prefix") or (getattr(sys, "base_prefix", sys.prefix) != sys.prefix) or ("VIRTUAL_ENV" in os.environ))


def _check_os() -> dict[str, Any]:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "arch": platform.machine(),
        "python_arch": platform.architecture()[0],
    }


def _check_tools(project_root: Path) -> dict[str, Any]:
    tools = project_root / "tools"
    svv = tools / "SoundVolumeView.exe"
    nircmd = tools / "nircmd.exe"
    return {
        "tools_dir": str(tools),
        "soundvolumeview": svv.exists(),
        "nircmd": nircmd.exists(),
    }


def _list_devices_with_pycaw() -> dict[str, Any]:
    try:
        from pycaw.pycaw import AudioUtilities  # type: ignore

        names: list[str] = []
        for dev in AudioUtilities.GetAllDevices():  # type: ignore[attr-defined]
            try:
                names.append(str(dev.FriendlyName))
            except Exception:
                continue
        return {"available": True, "count": len(names), "sample": names[:8]}
    except Exception as e:
        return {"available": False, "error": type(e).__name__}


def _check_voicemeeter_presence() -> dict[str, Any]:
    available = False
    try:
        import pyVoicemeeter  # type: ignore

        available = True
    except Exception:
        available = False

    running = False
    try:
        if platform.system() == "Windows":
            proc = subprocess.run(["tasklist"], capture_output=True, text=True, check=False)
            out = (proc.stdout or "") + (proc.stderr or "")
            running = ("voicemeeter" in out.lower()) or ("vb-audio" in out.lower())
    except Exception:
        running = False
    return {"module": available, "process_running": running}


def run_basic_checks(project_root: Path | None = None) -> dict[str, Any]:
    project_root = project_root or Path(__file__).resolve().parents[1]
    results: dict[str, Any] = {}
    results["python_executable"] = sys.executable
    results["python_version"] = sys.version.split()[0]
    results["venv_active"] = _is_venv()
    results["os"] = _check_os()
    results["pycaw_devices"] = _list_devices_with_pycaw()
    results["voicemeeter"] = _check_voicemeeter_presence()
    results["tools"] = _check_tools(project_root)
    return results


def format_checks_for_cli(results: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"Python: {results.get('python_version')} @ {results.get('python_executable')}")
    lines.append(f"Virtualenv active: {results.get('venv_active')}")
    osinfo = results.get("os", {})
    lines.append(
        f"OS: {osinfo.get('system')} {osinfo.get('release')} ({osinfo.get('arch')}, py-arch {osinfo.get('python_arch')})"
    )
    pycaw = results.get("pycaw_devices", {})
    if pycaw.get("available"):
        lines.append(f"pycaw: available, devices={pycaw.get('count')}, sample={pycaw.get('sample')}")
    else:
        lines.append(f"pycaw: missing or error={pycaw.get('error')}")
    vm = results.get("voicemeeter", {})
    lines.append(
        f"pyVoicemeeter: {'available' if vm.get('module') else 'missing'}, process_running={vm.get('process_running')}"
    )
    tools = results.get("tools", {})
    lines.append(
        f"tools: dir={tools.get('tools_dir')}, SoundVolumeView={'yes' if tools.get('soundvolumeview') else 'no'}, NirCmd={'yes' if tools.get('nircmd') else 'no'}"
    )
    lines.append("Raw JSON below (for debugging):")
    lines.append(json.dumps(results, indent=2))
    return "\n".join(lines)

