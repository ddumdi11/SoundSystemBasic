# VoiceMeeter (Stufe 2): Connect/Status/Presets + UI-Tab

## Ziel
- VoiceMeeter Banana anbinden (pyVoicemeeter): verbinden, Status lesen, Presets laden.

## Aufgaben
- Abhängigkeit optional aufnehmen (requirements: kommentiert/optional).
- `audio/voicemeeter.py`: `connect()`, `disconnect()`, `get_status()`, `load_preset(path)`.
- UI-Tab "VoiceMeeter": Verbindungsstatus, Preset-Dropdown (aus `profiles/`), 2–3 Regler (Strip1 Gain/Mute).
- /doctor: Edition/Version/API-Status anzeigen.

## Akzeptanzkriterien
- Verbindung erfolgreich erkannt/angezeigt; Presets laden sichtbar.
- Stufe 1 bleibt funktionsfähig ohne VoiceMeeter.
