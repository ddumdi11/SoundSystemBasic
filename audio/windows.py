"""Windows audio control primitives for Stufe 1.

- Lists playback/recording devices (heuristic split via names when using pycaw)
- Sets master volume / mute via CoreAudio (pycaw)
- Plays a simple test tone via winsound
- Sets default devices using SoundVolumeView.exe if available (fallback)

Note: A pure COM solution for setting default endpoints (IPolicyConfig) will be
added next. This module currently prefers the lightweight/fallback approach.
"""

from __future__ import annotations

from ctypes import HRESULT, c_int, c_void_p, c_ulong
from pathlib import Path
from typing import Any
from comtypes import GUID

# Local constants (avoid pycaw.constants for compatibility across versions)
# EDataFlow
E_RENDER = 0
E_CAPTURE = 1
E_ALL = 2

# ERole
E_CONSOLE = 0
E_MULTIMEDIA = 1
E_COMMUNICATIONS = 2

# Device state flags
DEVICE_STATE_ACTIVE = 0x00000001

# CLSID for MMDeviceEnumerator
CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")


def _safe_import_pycaw():
    try:
        from comtypes import CLSCTX_ALL  # type: ignore
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore

        return CLSCTX_ALL, AudioUtilities, IAudioEndpointVolume
    except Exception:  # pragma: no cover - optional dependency path
        return None, None, None


def _soundvolumeview_path() -> Path | None:
    # Prefer local tools folder
    candidate = Path("tools") / "SoundVolumeView.exe"
    if candidate.exists():
        return candidate
    # As a fallback, rely on PATH (not resolved here); caller will attempt run
    return None


def _split_devices_by_flow(all_devices: list[Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split devices into playback (Render) and recording (Capture) by checking endpoint IDs."""
    render_ids = _ids_for_flow(E_RENDER)
    capture_ids = _ids_for_flow(E_CAPTURE)
    playback: list[dict[str, Any]] = []
    recording: list[dict[str, Any]] = []
    for dev in all_devices:
        try:
            name = str(dev.FriendlyName) if getattr(dev, "FriendlyName", None) is not None else "(Unbenannt)"
            id_ = str(dev.id)
            entry = {"id": id_, "name": name}
            if id_ in render_ids:
                playback.append(entry)
            elif id_ in capture_ids:
                recording.append(entry)
            else:
                # Fallback heuristic if ID wasn't found in either set
                lname = name.lower()
                if any(k in lname for k in ("microphone", "mikro", "aufnah", "record", "line-in", "line in", "eingang", "stereo mix", "output")):
                    recording.append(entry)
                else:
                    playback.append(entry)
        except Exception:
            continue
    # Consistent sort by name (case-insensitive)
    playback.sort(key=lambda d: (d.get("name") or "").casefold())
    recording.sort(key=lambda d: (d.get("name") or "").casefold())
    return playback, recording


def list_playback_devices() -> list[dict[str, Any]]:
    _, AudioUtilities, _ = _safe_import_pycaw()
    if AudioUtilities is None:
        return []
    all_devices = AudioUtilities.GetAllDevices()  # type: ignore[attr-defined]
    playback, _ = _split_devices_by_flow(all_devices)
    return playback


def list_recording_devices() -> list[dict[str, Any]]:
    _, AudioUtilities, _ = _safe_import_pycaw()
    if AudioUtilities is None:
        return []
    all_devices = AudioUtilities.GetAllDevices()  # type: ignore[attr-defined]
    _, recording = _split_devices_by_flow(all_devices)
    return recording


def _resolve_device_id(identifier: str) -> str | None:
    """Try to resolve a user-supplied identifier (id or name) to an endpoint id."""
    _, AudioUtilities, _ = _safe_import_pycaw()
    if AudioUtilities is None:
        return None
    try:
        all_devices = AudioUtilities.GetAllDevices()  # type: ignore[attr-defined]
    except Exception:
        return None
    ident_lower = identifier.lower()
    exact_id = None
    by_name = None
    for dev in all_devices:
        try:
            dev_id = str(dev.id)
            dev_name = str(dev.FriendlyName)
            if identifier == dev_id:
                exact_id = dev_id
                break
            if by_name is None and (ident_lower == dev_name.lower() or ident_lower in dev_name.lower()):
                by_name = dev_id
        except Exception:
            continue
    return exact_id or by_name


def _get_default_id(flow: int) -> str | None:
    try:
        import comtypes.client as cc
        from pycaw.pycaw import IMMDeviceEnumerator  # type: ignore

        enum = cc.CreateObject(CLSID_MMDeviceEnumerator, interface=IMMDeviceEnumerator)
        # Try Multimedia, then Console, then Communications
        for role in (E_MULTIMEDIA, E_CONSOLE, E_COMMUNICATIONS):
            try:
                endpoint = enum.GetDefaultAudioEndpoint(flow, role)
                try:
                    return str(endpoint.GetId())
                except Exception:
                    for attr in ("id", "Id"):
                        if hasattr(endpoint, attr):
                            try:
                                return str(getattr(endpoint, attr))
                            except Exception:
                                pass
            except Exception:
                continue
    except Exception:
        return None
    return None


def get_default_playback_id() -> str | None:
    return _get_default_id(E_RENDER)


def get_default_recording_id() -> str | None:
    return _get_default_id(E_CAPTURE)


def _set_default_with_svv(device_name_or_id: str, flow: str) -> bool:
    """Try to set default device via SoundVolumeView.exe.

    flow: 'render' (playback) or 'capture' (recording)
    Uses Multimedia role by default.
    """
    from subprocess import run

    exe = _soundvolumeview_path()
    cmd = None
    if exe is not None:
        # SoundVolumeView supports /SetDefault <Name> <Role> [Render/Capture]
        # Role: 0=Console, 1=Multimedia, 2=Communications
        role = 1
        flow_arg = "Render" if flow == "render" else "Capture"
        cmd = [str(exe), "/SetDefault", device_name_or_id, str(role), flow_arg]
    else:
        # Attempt relying on PATH if user placed it there
        cmd = ["SoundVolumeView.exe", "/SetDefault", device_name_or_id, "1", "Render" if flow == "render" else "Capture"]
    try:
        proc = run(cmd, capture_output=True, text=True)
        return proc.returncode == 0
    except Exception:
        return False


def set_default_playback(device_identifier: str) -> bool:
    """Set default playback device by name or id using SVV fallback.

    Returns False if the operation could not be performed.
    """
    resolved = _resolve_device_id(device_identifier) or device_identifier
    rep = _debug_try_set_default(resolved)
    if rep.get("success"):
        return True
    return _set_default_with_svv(device_identifier, flow="render")


def set_default_recording(device_identifier: str) -> bool:
    """Set default recording device by name or id using SVV fallback.

    Returns False if the operation could not be performed.
    """
    resolved = _resolve_device_id(device_identifier) or device_identifier
    rep = _debug_try_set_default(resolved)
    if rep.get("success"):
        return True
    return _set_default_with_svv(device_identifier, flow="capture")


def set_master_volume(percent: int) -> bool:
    """Set endpoint master volume (0-100) for default playback device."""
    CLSCTX_ALL, AudioUtilities, IAudioEndpointVolume = _safe_import_pycaw()
    if not all((CLSCTX_ALL, AudioUtilities, IAudioEndpointVolume)):
        return False
    try:
        speakers = AudioUtilities.GetSpeakers()  # type: ignore[attr-defined]
        interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)  # type: ignore[attr-defined]
        volume = interface.QueryInterface(IAudioEndpointVolume)
        vol = max(0.0, min(1.0, percent / 100.0))
        volume.SetMasterVolumeLevelScalar(vol, None)
        return True
    except Exception:
        return False


def mute_master(mute: bool) -> bool:
    """Mute/unmute the default playback device."""
    CLSCTX_ALL, AudioUtilities, IAudioEndpointVolume = _safe_import_pycaw()
    if not all((CLSCTX_ALL, AudioUtilities, IAudioEndpointVolume)):
        return False
    try:
        speakers = AudioUtilities.GetSpeakers()  # type: ignore[attr-defined]
        interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)  # type: ignore[attr-defined]
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMute(bool(mute), None)
        return True
    except Exception:
        return False


def play_test_tone(frequency: int = 880, duration_ms: int = 300) -> None:
    """Play a short test tone using winsound.Beep (Windows only)."""
    try:
        import winsound

        winsound.Beep(int(frequency), int(duration_ms))
    except Exception:
        pass


def _set_default_with_com(device_id: str) -> bool:
    """Set default endpoint using IPolicyConfig via comtypes.

    This sets all roles (Console, Multimedia, Communications) to the provided endpoint.
    The device_id must be an endpoint ID string (IMMDevice id), which pycaw exposes as `dev.id`.
    """
    try:
        import comtypes
        from comtypes import GUID
        from comtypes import COMMETHOD
        from ctypes.wintypes import LPCWSTR, BOOL
        import comtypes.client as cc

        class IPolicyConfig(comtypes.IUnknown):
            _iid_ = GUID("{F8679F50-850A-41CF-9C72-430F290290C8}")
            _methods_ = [
                COMMETHOD([], HRESULT, "SetDefaultEndpoint", ([], LPCWSTR, "wszDeviceId"), ([], c_int, "role")),
            ]

        # More complete Vista interface definition with correct vtable order
        class IPolicyConfigVista(comtypes.IUnknown):
            _iid_ = GUID("{568B9108-44BF-40B4-9006-86AFE5B5A620}")
            _methods_ = [
                COMMETHOD([], HRESULT, "GetMixFormat", ([], LPCWSTR, "dev"), ([], c_void_p, "ppFormat")),
                COMMETHOD([], HRESULT, "GetDeviceFormat", ([], LPCWSTR, "dev"), ([], c_int, "bDefault"), ([], c_void_p, "ppFormat")),
                COMMETHOD([], HRESULT, "SetDeviceFormat", ([], LPCWSTR, "dev"), ([], c_void_p, "pEndpointFormat"), ([], c_void_p, "pMixFormat")),
                COMMETHOD([], HRESULT, "GetProcessingPeriod", ([], LPCWSTR, "dev"), ([], c_int, "bDefault"), ([], c_void_p, "pmftDefaultPeriod"), ([], c_void_p, "pmftMinimumPeriod")),
                COMMETHOD([], HRESULT, "SetProcessingPeriod", ([], LPCWSTR, "dev"), ([], c_void_p, "pmftPeriod")),
                COMMETHOD([], HRESULT, "GetShareMode", ([], LPCWSTR, "dev"), ([], c_void_p, "pMode")),
                COMMETHOD([], HRESULT, "SetShareMode", ([], LPCWSTR, "dev"), ([], c_void_p, "pMode")),
                COMMETHOD([], HRESULT, "GetPropertyValue", ([], LPCWSTR, "dev"), ([], c_void_p, "key"), ([], c_void_p, "pv")),
                COMMETHOD([], HRESULT, "SetPropertyValue", ([], LPCWSTR, "dev"), ([], c_void_p, "key"), ([], c_void_p, "pv")),
                COMMETHOD([], HRESULT, "SetDefaultEndpoint", ([], LPCWSTR, "wszDeviceId"), ([], c_int, "role")),
                COMMETHOD([], HRESULT, "SetEndpointVisibility", ([], LPCWSTR, "dev"), ([], BOOL, "bVisible")),
            ]

        CLSID_candidates = [
            GUID("{870AF99C-171D-4F9E-AF0D-E63DF40C2BC9}"),  # PolicyConfigClient
            GUID("{294935CE-F637-4E7C-A41B-AB255460B862}"),  # CPolicyConfigVistaClient
        ]

        # Create COM object and obtain interface (try candidates for compatibility)
        obj = None
        last_exc: Exception | None = None
        for clsid in CLSID_candidates:
            try:
                # Try Vista interface first
                try:
                    obj = cc.CreateObject(clsid, interface=IPolicyConfigVista)
                except Exception:
                    obj = cc.CreateObject(clsid, interface=IPolicyConfig)
                if obj is not None:
                    break
            except Exception as e:  # pragma: no cover
                last_exc = e
                obj = None
        if obj is None:
            if last_exc:
                raise last_exc
            return False

        # ERole: 0=Console, 1=Multimedia, 2=Communications
        ok = True
        for role in (E_CONSOLE, E_MULTIMEDIA, E_COMMUNICATIONS):
            try:
                hr = obj.SetDefaultEndpoint(device_id, int(role))
                if isinstance(hr, int) and hr != 0:
                    ok = False
            except Exception:
                ok = False
        return ok
    except Exception:
        return False


def _debug_try_set_default(device_id: str) -> dict[str, Any]:
    """Attempt to set default endpoint via both PolicyConfig interfaces and report HRESULTs."""
    report: dict[str, Any] = {"device_id": device_id, "attempts": [], "success": False}
    try:
        import comtypes
        from comtypes import GUID
        from comtypes import COMMETHOD
        from ctypes.wintypes import LPCWSTR, BOOL
        import comtypes.client as cc

        class IPolicyConfig(comtypes.IUnknown):
            _iid_ = GUID("{F8679F50-850A-41CF-9C72-430F290290C8}")
            _methods_ = [
                COMMETHOD([], HRESULT, "SetDefaultEndpoint", ([], LPCWSTR, "wszDeviceId"), ([], c_int, "role")),
            ]

        class IPolicyConfigVista(comtypes.IUnknown):
            _iid_ = GUID("{568B9108-44BF-40B4-9006-86AFE5B5A620}")
            _methods_ = [
                COMMETHOD([], HRESULT, "GetMixFormat", ([], LPCWSTR, "dev"), ([], c_void_p, "ppFormat")),
                COMMETHOD([], HRESULT, "GetDeviceFormat", ([], LPCWSTR, "dev"), ([], c_int, "bDefault"), ([], c_void_p, "ppFormat")),
                COMMETHOD([], HRESULT, "SetDeviceFormat", ([], LPCWSTR, "dev"), ([], c_void_p, "pEndpointFormat"), ([], c_void_p, "pMixFormat")),
                COMMETHOD([], HRESULT, "GetProcessingPeriod", ([], LPCWSTR, "dev"), ([], c_int, "bDefault"), ([], c_void_p, "pmftDefaultPeriod"), ([], c_void_p, "pmftMinimumPeriod")),
                COMMETHOD([], HRESULT, "SetProcessingPeriod", ([], LPCWSTR, "dev"), ([], c_void_p, "pmftPeriod")),
                COMMETHOD([], HRESULT, "GetShareMode", ([], LPCWSTR, "dev"), ([], c_void_p, "pMode")),
                COMMETHOD([], HRESULT, "SetShareMode", ([], LPCWSTR, "dev"), ([], c_void_p, "pMode")),
                COMMETHOD([], HRESULT, "GetPropertyValue", ([], LPCWSTR, "dev"), ([], c_void_p, "key"), ([], c_void_p, "pv")),
                COMMETHOD([], HRESULT, "SetPropertyValue", ([], LPCWSTR, "dev"), ([], c_void_p, "key"), ([], c_void_p, "pv")),
                COMMETHOD([], HRESULT, "SetDefaultEndpoint", ([], LPCWSTR, "wszDeviceId"), ([], c_int, "role")),
                COMMETHOD([], HRESULT, "SetEndpointVisibility", ([], LPCWSTR, "dev"), ([], BOOL, "bVisible")),
            ]

        candidates = [
            (GUID("{870AF99C-171D-4F9E-AF0D-E63DF40C2BC9}"), IPolicyConfig, "PolicyConfigClient/IPolicyConfig"),
            (GUID("{294935CE-F637-4E7C-A41B-AB255460B862}"), IPolicyConfigVista, "CPolicyConfigVistaClient/IPolicyConfigVista"),
            (GUID("{294935CE-F637-4E7C-A41B-AB255460B862}"), IPolicyConfig, "CPolicyConfigVistaClient/IPolicyConfig (fallback)"),
        ]
        for clsid, iface, label in candidates:
            entry: dict[str, Any] = {"clsid": str(clsid), "iface": iface.__name__, "label": label, "roles": []}
            try:
                obj = cc.CreateObject(clsid, interface=iface)
            except Exception as e:
                entry["error"] = f"create_failed: {type(e).__name__}"
                report["attempts"].append(entry)
                continue
            ok_all = True
            ok_any = False
            ok_mm = False
            for role in (E_CONSOLE, E_MULTIMEDIA, E_COMMUNICATIONS):
                try:
                    hr = obj.SetDefaultEndpoint(device_id, int(role))
                    code = hr if isinstance(hr, int) else 0
                    entry["roles"].append({"role": role, "hr": code})
                    if code == 0:
                        ok_any = True
                        if role == E_MULTIMEDIA:
                            ok_mm = True
                    else:
                        ok_all = False
                except Exception as e:
                    entry["roles"].append({"role": role, "error": type(e).__name__})
                    ok_all = False
            entry["ok_all"] = ok_all
            entry["ok_any"] = ok_any
            entry["ok_multimedia"] = ok_mm
            report["attempts"].append(entry)
            # Treat success if Multimedia role succeeded, else any role success as fallback
            report["success"] = report.get("success", False) or ok_mm or ok_any
    except Exception as e:
        report["error"] = f"unexpected: {type(e).__name__}"
    return report


def debug_set_default_endpoint(device_identifier: str, flow: str) -> dict[str, Any]:
    """Debug helper to test SetDefaultEndpoint and inspect HRESULTs.

    flow: 'render' or 'capture' (used only for fallback message context)
    """
    resolved = _resolve_device_id(device_identifier) or device_identifier
    rep = _debug_try_set_default(resolved)
    if not rep.get("success"):
        rep["fallback"] = {"svv_attempted": False, "hint": "Place SoundVolumeView.exe in tools/ to enable fallback"}
    return rep


def _ids_for_flow(flow: int) -> set[str]:
    """Enumerate active endpoint IDs for given flow (eRender/eCapture)."""
    try:
        import comtypes.client as cc
        from pycaw.pycaw import IMMDeviceEnumerator  # type: ignore

        enum = cc.CreateObject(CLSID_MMDeviceEnumerator, interface=IMMDeviceEnumerator)
        coll = enum.EnumAudioEndpoints(flow, DEVICE_STATE_ACTIVE)
        count = coll.GetCount()
        ids: set[str] = set()
        for i in range(count):
            dev = coll.Item(i)
            try:
                ids.add(str(dev.GetId()))
            except Exception:
                continue
        return ids
    except Exception:
        return set()
