# 🔊 Sound System Basic

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-green.svg)](https://www.microsoft.com/windows/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/Status-Work%20in%20Progress-orange.svg)]()

**Leichtgewichtige Windows-App (Python) zum Steuern der Audio-Standardgeräte und Systemlautstärke. Optional: VoiceMeeter-Integration (Stufe 2) und Profile (Stufe 3).**

Eine moderne, benutzerfreundliche Lösung mit sowohl CLI- als auch GUI-Unterstützung.

## 🎯 Projektübersicht

Sound System Basic ist eine speziell entwickelte Anwendung, die eine einfache und intuitive Lösung bietet. Das Projekt kombiniert moderne Python-Technologien mit einer durchdachten Benutzeroberfläche.

### ✨ Hauptfunktionen

- 🎵 **Testton ausgeben**
- 🎵 **Systemlautstärke und Mute steuern**
- 🎵 **Standardgeräte setzen (robuste COM-Methode, alle Rollen)**
- 🎵 **Einfache Tkinter-UI mit Default-Markierung (★)**
- 🎵 **Geräte trennen nach Wiedergabe (Render) und Aufnahme (Capture)**

## 🚀 Entwicklungs-Roadmap

### Stage 1: ✅ Abgeschlossen
- Stufe 1 (fertig): Windows-Standardgeräte, Lautstärke, Testton, UI/CLI

### Stage 2: 🔄 In Entwicklung
- Stufe 2 (geplant): VoiceMeeter Banana (pyVoicemeeter), Presets, Status
- Stufe 3 (geplant): Profile, Hotkeys, Validierung, Packaging (PyInstaller)

### Stage 3: 📋 Geplant
- Entwürfe.
- `python -m app.cli /doctor`
- Prüft Python‑Version, Rechte, COM‑Zugriff, VoiceMeeter‑Erreichbarkeit, listet Geräte

## 🛠️ Installation & Setup

### Systemanforderungen
- **Betriebssystem**: Windows 10/11
- **Python**: Version 3.11+ (empfohlen)
- **Speicherplatz**: ~10 MB

### Schnellstart

```bash
# Repository klonen
git clone https://github.com/ddumdi11/SoundSystemBasic.git
cd Sound System Basic

# Virtuelle Umgebung erstellen und aktivieren
python -m venv venv
venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
python app/main.py
```

### Projektstruktur
```
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
```

## 🤝 Mitwirkung & Entwicklung

### Entwicklungsrichtlinien
- **Regel**: Python 3.11 empfohlen
- **Regel**: Abhängigkeiten in `.venv` (nicht global)
- **Anforderungen**: `requirements.txt`
- **Fallback-Tools (optional)**: `tools/SoundVolumeView.exe` für SetDefault per Tool
- **Branches**: arbeite auf `dev` oder Feature-Branches (`feat/<kurz>`, `fix/<kurz>`), nicht direkt auf `main`.

## 📊 Features für LinkedIn-Präsentation

### 🎯 Geschäftswert
- **Produktivitätssteigerung**: Optimierte Workflows
- **Benutzerfreundlichkeit**: Intuitive Bedienung
- **Skalierbarkeit**: Modulare Architektur für zukünftige Erweiterungen

### 💼 Technische Highlights
- **Modern Development**: Python mit modernsten Standards
- **Professional Design**: Benutzerfreundliche Oberfläche
- **Enterprise Ready**: CLI-Support für Automatisierung

### 📈 Projektmetriken
- **Sprache**: Python (100% moderne Entwicklung)
- **Architektur**: Modulare, erweiterbare Struktur
- **Testing**: Umfassende Qualitätssicherung
- **Documentation**: Vollständige Entwicklerdokumentation

## 👥 Projektteam

Dieses Projekt wurde durch die Zusammenarbeit von drei innovativen Entwicklungspartnern realisiert:

- **Thorsten Diederichs** - *Projektleitung & Konzeption* - [LinkedIn](https://linkedin.com/in/thorsten-diederichs)
- **Claude Code** - *KI-Entwicklungsassistent* - [Anthropic](https://claude.ai/code)
- **Codex** - *KI-Code-Generator* - *Unterstützung bei der Implementierung*

## 📜 Lizenz

Dieses Projekt steht unter der [MIT License](LICENSE) - siehe LICENSE-Datei für Details.

## 🔗 Links & Ressourcen

- **Repository**: [GitHub - Sound System Basic](https://github.com/ddumdi11/SoundSystemBasic)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/ddumdi11/SoundSystemBasic/issues)
- **Documentation**: [Wiki](https://github.com/ddumdi11/SoundSystemBasic/wiki)

---

**Status**: 🚧 Work in Progress - Kontinuierliche Weiterentwicklung

*Erstellt mit modernsten Entwicklungstools für maximale Professionalität und Benutzerfreundlichkeit.*
