import argparse
import json
import os
import sys
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _print(msg: str) -> None:
    print(msg, flush=True)


def _ensure_dirs(*dirs: Path, dry_run: bool = False) -> None:
    for d in dirs:
        if dry_run:
            _print(f"[dry-run] mkdir {d}")
        else:
            d.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, data: dict, force: bool = False, dry_run: bool = False) -> None:
    if path.exists() and not force:
        _print(f"[skip] {path} exists (use --force to overwrite)")
        return
    if dry_run:
        _print(f"[dry-run] write {path} -> {json.dumps(data, indent=2)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    _print(f"[ok] wrote {path}")


def _venv_paths(venv_dir: Path) -> dict:
    if os.name == "nt":
        python = venv_dir / "Scripts" / "python.exe"
        pip = venv_dir / "Scripts" / "pip.exe"
        activate = venv_dir / "Scripts" / "Activate"
    else:
        python = venv_dir / "bin" / "python"
        pip = venv_dir / "bin" / "pip"
        activate = venv_dir / "bin" / "activate"
    return {"python": python, "pip": pip, "activate": activate}


def _create_venv(venv_dir: Path, dry_run: bool = False) -> None:
    if venv_dir.exists():
        _print(f"[info] venv exists at {venv_dir}")
        return
    if dry_run:
        _print(f"[dry-run] create venv at {venv_dir}")
        return
    # Use Python's built-in venv module
    import venv

    _print(f"[run] creating venv at {venv_dir}")
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(str(venv_dir))
    _print("[ok] venv created")


def _pip_install(pip_path: Path, packages: list[str], dry_run: bool = False) -> int:
    if dry_run:
        _print(f"[dry-run] {pip_path} install {' '.join(packages)}")
        return 0
    if not pip_path.exists():
        _print(f"[warn] pip not found at {pip_path}; skip install")
        return 1
    cmd = [str(pip_path), "install", "-U", "pip"]
    _print(f"[run] {' '.join(cmd)}")
    subprocess.run(cmd, check=False)
    if packages:
        cmd = [str(pip_path), "install", *packages]
        _print(f"[run] {' '.join(cmd)}")
        proc = subprocess.run(cmd, check=False)
        return proc.returncode
    return 0


def _scan_devices() -> dict:
    """Attempt a basic device scan. Falls back to placeholders if deps are missing."""
    devices = {"playback": [], "recording": []}
    default_playback = None
    default_recording = None
    try:
        # Lazy import; if not available, we fallback
        from pycaw.pycaw import AudioUtilities
        # pycaw does not separate flow directly; we approximate
        all_devices = AudioUtilities.GetAllDevices()  # type: ignore[attr-defined]
        for dev in all_devices:
            try:
                name = str(dev.FriendlyName)
                id_ = str(dev.id)
                # Heuristic split based on name; accurate split would use IMMDevice properties
                entry = {"id": id_, "name": name}
                lname = name.lower()
                if any(k in lname for k in ("microphone", "mic", "aufnah", "record")):
                    devices["recording"].append(entry)
                else:
                    devices["playback"].append(entry)
            except Exception:
                continue
    except Exception:
        # Fallback placeholders
        devices = {
            "playback": [
                {"id": "{device-id-umc204hd-out}", "name": "UMC204HD (Wiedergabe)"}
            ],
            "recording": [
                {"id": "{device-id-bt-mic}", "name": "Bluetooth Mikrofon (Aufnahme)"}
            ],
        }
        default_playback = devices["playback"][0]["id"]
        default_recording = devices["recording"][0]["id"]
    return {
        "devices": devices,
        "defaults": {"playback": default_playback, "recording": default_recording},
    }


def cmd_init(args: argparse.Namespace) -> int:
    dry = args.dry_run
    force = args.force

    config_dir = PROJECT_ROOT / "config"
    profiles_dir = PROJECT_ROOT / "profiles"
    tools_dir = PROJECT_ROOT / "tools"
    venv_dir = PROJECT_ROOT / ".venv"
    _ensure_dirs(config_dir, profiles_dir, tools_dir, dry_run=dry)

    scan = _scan_devices()
    cfg = {
        "use_voicemeeter": False,
        "defaults": {
            "playback": scan["defaults"]["playback"] or "<set-after-scan>",
            "recording": scan["defaults"]["recording"] or "<set-after-scan>",
        },
        "volume": {"master": 35},
    }
    _write_json(config_dir / "app.json", cfg, force=force, dry_run=dry)

    if args.profiles == "default":
        example = {
            "name": "Dictation",
            "playback": cfg["defaults"]["playback"],
            "recording": cfg["defaults"]["recording"],
            "voicemeeter": None,
        }
        _write_json(profiles_dir / "dictation.json", example, force=force, dry_run=dry)

    if args.tools == "auto":
        readme = tools_dir / "README.txt"
        if dry:
            _print(f"[dry-run] write {readme}")
        else:
            readme.write_text(
                "Place optional fallback tools here (SoundVolumeView.exe, nircmd.exe).\n",
                encoding="utf-8",
            )
            _print(f"[ok] wrote {readme}")

    if args.venv:
        _create_venv(venv_dir, dry_run=dry)
        paths = _venv_paths(venv_dir)
        _print(
            f"[info] activate venv: {paths['activate']} (then run installs inside the venv)"
        )
        if not args.no_install:
            rc = _pip_install(paths["pip"], ["pycaw", "comtypes"], dry_run=dry)
            if rc != 0:
                _print("[warn] dependency installation reported a non-zero exit code")

    _print("[done] init complete")
    return 0


def cmd_doctor(_args: argparse.Namespace) -> int:
    from diagnostics.doctor import run_basic_checks, format_checks_for_cli

    results = run_basic_checks(PROJECT_ROOT)
    _print(format_checks_for_cli(results))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="app.cli", add_help=True)
    sub = p.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("/init", help="Initialize project structure and config")
    p_init.add_argument("--venv", action="store_true", help="Create .venv and install deps")
    p_init.add_argument("--no-install", action="store_true", help="Skip dependency installation")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing files")
    p_init.add_argument("--dry-run", action="store_true", help="Show actions without changing files")
    p_init.add_argument(
        "--profiles",
        choices=["default", "none"],
        default="default",
        help="Create example profiles",
    )
    p_init.add_argument(
        "--tools",
        choices=["auto", "none"],
        default="auto",
        help="Prepare tools folder",
    )
    p_init.set_defaults(func=cmd_init)

    p_doc = sub.add_parser("/doctor", help="Run environment checks")
    p_doc.set_defaults(func=cmd_doctor)

    # Windows audio helper commands (Stufe 1 testing)
    def _win_list(args: argparse.Namespace) -> int:
        from audio import windows as win

        play = win.list_playback_devices()
        rec = win.list_recording_devices()
        _print("Playback devices:")
        for d in play:
            _print(f"- {d.get('id')} :: {d.get('name')}")
        _print("Recording devices:")
        for d in rec:
            _print(f"- {d.get('id')} :: {d.get('name')}")
        return 0

    def _win_set_def_pb(args: argparse.Namespace) -> int:
        from audio import windows as win

        if getattr(args, "debug", False):
            rep = win.debug_set_default_endpoint(args.identifier, "render")
            _print(json.dumps(rep, indent=2))
            return 0 if rep.get("success") else 1
        ok = win.set_default_playback(args.identifier)
        _print("ok" if ok else "failed (try placing SoundVolumeView.exe in tools/)")
        return 0 if ok else 1

    def _win_set_def_rec(args: argparse.Namespace) -> int:
        from audio import windows as win

        if getattr(args, "debug", False):
            rep = win.debug_set_default_endpoint(args.identifier, "capture")
            _print(json.dumps(rep, indent=2))
            return 0 if rep.get("success") else 1
        ok = win.set_default_recording(args.identifier)
        _print("ok" if ok else "failed (try placing SoundVolumeView.exe in tools/)")
        return 0 if ok else 1

    def _win_volume(args: argparse.Namespace) -> int:
        from audio import windows as win

        ok = win.set_master_volume(args.percent)
        _print("ok" if ok else "failed")
        return 0 if ok else 1

    def _win_mute(args: argparse.Namespace) -> int:
        from audio import windows as win

        ok = win.mute_master(args.state == "on")
        _print("ok" if ok else "failed")
        return 0 if ok else 1

    def _win_tone(args: argparse.Namespace) -> int:
        from audio import windows as win

        win.play_test_tone(args.freq, args.ms)
        _print("tone")
        return 0

    p_win = sub.add_parser("win", help="Windows audio helpers")
    win_sub = p_win.add_subparsers(dest="win_cmd", required=True)

    p_win_list = win_sub.add_parser("list", help="List playback/recording devices")
    p_win_list.set_defaults(func=_win_list)

    p_win_setpb = win_sub.add_parser("set-default-playback", help="Set default playback by name or id")
    p_win_setpb.add_argument("identifier", help="Device name or id")
    p_win_setpb.add_argument("--debug", action="store_true", help="Show COM attempts and HRESULTs")
    p_win_setpb.set_defaults(func=_win_set_def_pb)

    p_win_setrec = win_sub.add_parser("set-default-recording", help="Set default recording by name or id")
    p_win_setrec.add_argument("identifier", help="Device name or id")
    p_win_setrec.add_argument("--debug", action="store_true", help="Show COM attempts and HRESULTs")
    p_win_setrec.set_defaults(func=_win_set_def_rec)

    p_win_vol = win_sub.add_parser("volume", help="Set master volume (0-100)")
    p_win_vol.add_argument("percent", type=int)
    p_win_vol.set_defaults(func=_win_volume)

    p_win_mute = win_sub.add_parser("mute", help="Mute on/off")
    p_win_mute.add_argument("state", choices=["on", "off"])
    p_win_mute.set_defaults(func=_win_mute)

    p_win_tone = win_sub.add_parser("test-tone", help="Play a test tone")
    p_win_tone.add_argument("freq", type=int, nargs="?", default=880)
    p_win_tone.add_argument("ms", type=int, nargs="?", default=300)
    p_win_tone.set_defaults(func=_win_tone)

    return p


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
