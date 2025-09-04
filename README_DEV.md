# README_DEV.md

Projekt: Windows-Audio steuern (optional mit VoiceMeeter Banana), Use‑Cases speichern und schnell umschalten — leichtgewichtig, portabel, erweiterbar.

## Ziel & Stufen
- Stufe 1: Kontrolle der Windows‑Systemeinstellungen für Sound
  - Geräte auflisten, Standardgeräte setzen (Wiedergabe/Eingabe), Systemlautstärke/Mute steuern, Testton ausgeben.
- Stufe 2: Kontrolle von VoiceMeeter Banana in Kombination mit Windows
  - Erkennen, Verbinden, Strips/Busse steuern, Presets laden, robustes Fallback ohne VoiceMeeter.
- Stufe 3: Feinjustagen, Optimierungen, Erweiterungen
  - Profile/Use‑Cases verwalten, Hotkeys, Logging/Diagnose, Konfig‑Validierung, sauberes Packaging.

Die App soll einfach zu bedienen, intuitiv, leichtgewichtig (Python + Tkinter) und portabel (ein einzelnes ausführbares File möglich) sein.

## Voraussetzungen
- Windows 10 oder 11
- Python 3.10+ (empfohlen 3.11+)
- Optional: VoiceMeeter Banana installiert (für Stufe 2)
- Optional Fallback‑Tools: NirSoft SoundVolumeView oder NirCmd (nur falls COM/WinAPI nicht greift)

## Lokale Umgebung (.venv)
- Warum: Isoliert Projekt‑Abhängigkeiten, kein „globales“ Installieren.
- Git: `/.venv/` in `.gitignore` aufnehmen.
- PowerShell (Windows):
```
py -3.11 -m venv .venv
.\.venv\Scripts\Activate
python -m pip install -U pip
# Wenn noch kein requirements.txt existiert, zunächst nichts installieren oder gezielt:
# pip install pycaw comtypes
# Später: 
# pip install -r requirements.txt
```
- Deaktivieren: `deactivate`

## Abhängigkeiten (nach Stufen)
- Stufe 1 (Windows Audio)
  - Python‑Pakete: `pycaw`, `comtypes` (CoreAudio/COM), optional `pywin32`
  - Fallback: `SoundVolumeView.exe` oder `nircmd.exe` in `./tools/`
- Stufe 2 (VoiceMeeter)
  - Python‑Paket: `pyVoicemeeter`
  - VoiceMeeter Banana + Remote API (standard bei Installation)
- Stufe 3 (Qualität/Komfort)
  - `pydantic` oder `jsonschema` (Config‑Validierung)
  - optional `keyboard` (Hotkeys)

Hinweis: Fallback‑Tools werden nur verwendet, wenn die native COM/Remote‑API nicht verfügbar ist oder zur Diagnose.

## Architekturvorschlag
- `audio/windows.py`: Windows‑Geräte auflisten, Standardgeräte setzen, Systemlautstärke/Mute, Testton
- `audio/voicemeeter.py`: Verbindung/Erkennung, Strips/Busse, Preset‑Laden
- `profiles/manager.py`: Profile lesen/schreiben (JSON/YAML), Migration, Validierung
- `app/ui_tk.py`: Tkinter‑UI (Standard)
- `app/cli.py`: CLI‑Befehle (`/doctor`, `/init`, `profile apply`)
- `diagnostics/doctor.py`: Umgebungschecks, Logging‑Infos
- `config/`: App‑Konfiguration, Schema
- `profiles/`: Beispiel‑Profile
- `tools/`: optionale Fallback‑Exe (NirSoft), Lizenzhinweis

Diese Struktur hält UI, Logik und Integrationen getrennt, erleichtert Tests und Packaging.

## UI (Tkinter, leichtgewichtig)
- Hauptfenster
  - Tab „Windows“ (Stufe 1):
    - Listen: Wiedergabegeräte, Aufnahmegeräte; Aktion „Als Standard setzen“
    - Slider „Systemlautstärke“, Buttons „Mute/Unmute“, „Testton“
    - „Refresh“ und Statusleiste (aktuelle Standardgeräte)
  - Tab „VoiceMeeter“ (Stufe 2):
    - Verbunden/Erkannt‑Status, Preset‑Dropdown (falls vorhanden), Basis‑Regler
  - Tab „Profile“ (Stufe 3):
    - Liste der Profile, Anzeigen/Anwenden, Neu/Duplizieren/Löschen

Optional: Später PyQt/Streamlit als alternative UI‑Frontends; Tkinter bleibt Referenz.

## Konfiguration
- `config/app.json`
  - `use_voicemeeter`: bool
  - `defaults.playback`: Geräte‑ID für Standard‑Wiedergabe
  - `defaults.recording`: Geräte‑ID für Standard‑Aufnahme
  - `volume.master`: Ziel‑Masterlautstärke (0–100)
- `profiles/*.json`
  - `name`, `playback` (Geräte‑ID), `recording` (Geräte‑ID), `voicemeeter` (optional Preset/Strip‑Settings)

Beispiel `config/app.json`:
```
{
  "use_voicemeeter": false,
  "defaults": {
    "playback": "{device-id-umc204hd-out}",
    "recording": "{device-id-bt-mic}"
  },
  "volume": { "master": 35 }
}
```

Beispiel `profiles/dictation.json`:
```
{
  "name": "Dictation",
  "playback": "{device-id-umc204hd-out}",
  "recording": "{device-id-bt-mic}",
  "voicemeeter": null
}
```

Gerätematching erfolgt idealerweise über stabile Geräte‑IDs (nicht nur Namen).

## CLI‑Befehle (geplant)
- `python -m app.cli /doctor`
  - Prüft Python‑Version, Rechte, COM‑Zugriff, VoiceMeeter‑Erreichbarkeit, listet Geräte
- `python -m app.cli /init [--venv] [--no-install]`
  - Scannt Geräte, erzeugt `config/app.json` mit Platzhaltern, optional Beispielprofile
  - `--venv`: legt `.venv` an und installiert Abhängigkeiten innerhalb des virtuellen Environments
  - `--no-install`: nur Dateien erzeugen, keine Installation durchführen
- `python -m app.cli profile list|apply "<Name>"`
  - Zeigt/aktiviert Profile
- `python -m app.ui_tk`
  - Startet die GUI

## Stufe 1: Windows‑Audio
Ziele:
- Wiedergabe/Recording‑Geräte auflisten
- Standardgeräte setzen (Kommunikation/Multimedia falls nötig)
- Systemlautstärke/Mute setzen
- Testton ausgeben

Akzeptanzkriterien:
- Geräte werden stabil erkannt (IDs), UI zeigt aktuellen Standard korrekt
- Setzen von Standardgeräten funktioniert ohne Neustart
- Volume/Mute funktioniert, Testton hörbar am Standardwiedergabegerät
- Robuste Fehlermeldungen, wenn Gerät fehlt/abgemeldet ist

Technik:
- bevorzugt via `pycaw`/CoreAudio (COM)
- Fallback via `SoundVolumeView.exe` in `./tools/`

## Stufe 2: VoiceMeeter‑Integration
Ziele:
- VoiceMeeter erkennen/verbinden (falls installiert)
- Strips/Busse auslesen/setzen (Basis)
- Presets laden (XML/VM State)
- Fallback ohne VoiceMeeter bleibt intakt

Akzeptanzkriterien:
- Wenn VoiceMeeter nicht installiert/gestartet: klare UI‑Hinweise, App bleibt nutzbar
- Preset laden wirkt (sichtbar in VM/Ohr)
- Keine Beeinflussung von Stufe‑1‑Funktionalität

Technik:
- `pyVoicemeeter` Remote API
- Optional: Preset‑Dateien im `profiles/` referenzieren

## Stufe 3: Profile, Qualität, Komfort
Ziele:
- Profile erstellen, speichern, anwenden (Windows + optional VM)
- Hotkeys (optional), Logging, Diagnosen
- Validierung (Schema), Migrationslogik bei Änderungen

Akzeptanzkriterien:
- Profil „Dictation“/„DAW“ anlegen und reproduzierbar anwenden
- Fehlende Geräte werden erkannt und sauber behandelt (Dialog/Guide)
- `/doctor` liefert verständliche Diagnose (z. B. Rechte/COM/VM Status)

Technik:
- JSON + Schema (pydantic oder jsonschema)
- `diagnostics/doctor.py` bündelt Checks und Troubleshooting‑Hinweise

## Troubleshooting
- Gerätegruppen/IDs: Namen können variieren; nach Möglichkeit mit Geräte‑ID arbeiten.
- Datenschutz/Privacy: Mikrofonnutzung in Windows Datenschutz zulassen.
- Abtastrate/Exclusive Mode: Knacken/Dropouts → Abtastraten vereinheitlichen; Exklusivmodus testen.
- Rechte/AV: Eingebettete Tools (NirSoft) ggf. von Virenscannern flagbar; Ablage in `./tools/`.
- VoiceMeeter nicht installiert: Stufe 1 bleibt voll funktionsfähig; UI zeigt Hinweis.

## Build & Portabilität
- Ein‑Datei‑Build: `pyinstaller --onefile --noconsole app\\main.py`
- Assets einbetten: `--add-data "tools\\SoundVolumeView.exe;tools"` (wenn genutzt)
- Keine Admin‑Rechte nötig; kein Installer zwingend
- Portable Konfiguration: `config/` und `profiles/` liegen neben der EXE

## Optionale Fallback‑Tools (DIY)
Batch/PowerShell/NirSoft sind nützlich als Diagnose oder Fallback, aber nicht Primärweg. Falls benötigt, werden sie aus `./tools/` aufgerufen und in der UI/CLI klar gekennzeichnet.

## Nächste Schritte
0) `.venv` anlegen (siehe Abschnitt „Lokale Umgebung (.venv)“) — alternativ via `/init --venv`.
1) `/init` definieren: Geräte scannen, Basis‑`config/app.json` erstellen, Beispielprofile optional.
2) Stufe‑1‑Funktionen in `audio/windows.py` implementieren.
3) Minimal‑UI (`app/ui_tk.py`) mit Geräte‑Listen + „Als Standard setzen“ + Volume.
4) `/doctor` für robuste Diagnose.

Sobald du den Patch bestätigst, wende ich ihn an und wir spezifizieren `/init`.
