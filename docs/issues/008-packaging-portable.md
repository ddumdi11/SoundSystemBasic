# Packaging/Portabilität: PyInstaller Spec + Doku

## Ziel
- Portable EXE bauen; Build-Doku und optionales Einbetten von Tools.

## Aufgaben
- `.spec` anlegen (pyinstaller), Flags testen (`--onefile --noconsole`).
- README: Abschnitt "Build & Portable" konkretisieren.
- Optional: `tools/SoundVolumeView.exe` einbetten (Lizenzhinweis beachten).

## Akzeptanzkriterien
- Reproduzierbarer Build (Dokumentation vorhanden).
- App läuft ohne Python-Installation; Konfig/Profiles portabel neben EXE.
