# Sound System Basic

Leichtgewichtige Windows-App (Python) zum Steuern der Audio-Standardgeräte und Systemlautstärke. Optional: VoiceMeeter-Integration (Stufe 2) und Profile (Stufe 3).

## Features (Stufe 1)
- Geräte trennen nach Wiedergabe (Render) und Aufnahme (Capture)
- Standardgeräte setzen (robuste COM-Methode, alle Rollen)
- Systemlautstärke und Mute steuern
- Testton ausgeben
- Einfache Tkinter-UI mit Default-Markierung (★)

## Quickstart
1) Virtuelle Umgebung anlegen (PowerShell):
```
py -3.11 -m venv .venv
.\.venv\Scripts\Activate
python -m pip install -U pip
pip install -r requirements.txt
```

2) Diagnose und Initialisierung:
```
python -m app.cli /doctor
python -m app.cli /init --no-install
```

3) Start UI (Stufe 1):
```
python -m app.ui_tk
```

4) CLI-Shortcuts (optional):
```
# Geräte anzeigen
python -m app.cli win list

# Standard setzen (ID aus "win list" oder UI übernehmen)
python -m app.cli win set-default-playback "<ID>"
python -m app.cli win set-default-recording "<ID>"

# Lautstärke/Mute/Testton
python -m app.cli win volume 35
python -m app.cli win mute off
python -m app.cli win test-tone
```

Hinweis: Die UI aktualisiert nach dem Setzen des Standardgeräts automatisch (leichte Verzögerung), markiert das aktuelle Gerät mit ★ und zeigt es unterhalb der Liste als „Standard: …“ an.

## Stufen & Roadmap
- Stufe 1 (fertig): Windows-Standardgeräte, Lautstärke, Testton, UI/CLI
- Stufe 2 (geplant): VoiceMeeter Banana (pyVoicemeeter), Presets, Status
- Stufe 3 (geplant): Profile, Hotkeys, Validierung, Packaging (PyInstaller)

## Entwicklung
- Python 3.11 empfohlen
- Abhängigkeiten in `.venv` (nicht global)
- Anforderungen: `requirements.txt`
- Fallback-Tools (optional): `tools/SoundVolumeView.exe` für SetDefault per Tool

## Status
Work in progress (WIP). Stufe 1 ist funktional stabil; Stufe 2/3 folgen.

## Contributing
- Branches: arbeite auf `dev` oder Feature-Branches (`feat/<kurz>`, `fix/<kurz>`), nicht direkt auf `main`.
- Commits: nutze kurze, präzise Messages; gern im Stil von Conventional Commits (`feat: …`, `fix: …`).
- Umgebung: immer `.venv` verwenden; installiere Abhängigkeiten mit `pip install -r requirements.txt`.
- Checks: `python -m app.cli /doctor` vor PRs, UI-Test mit `python -m app.ui_tk`.
- Scope: fokussiere Änderungen (kleine PRs sind leichter zu reviewen). 
- Issues/PRs: beschreibe das Ziel, die Schritte zur Reproduktion (falls Bug) und Screenshots, wenn UI betroffen.
