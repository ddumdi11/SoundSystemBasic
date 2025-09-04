# /doctor erweitern (Pfade, Warnungen, Snapshot)

## Ziel
- Aussagekräftigere Diagnoseausgaben und optionaler Gerätesnapshot.

## Aufgaben
- Windows- und POSIX-Pfade parallel ausgeben (optisch klar).
- pycaw-Warnungen gesammelt als "Hinweis (unkritisch)" kennzeichnen.
- Optional: Snapshot `diagnostics/devices.json` mit IDs/Namen je Flow.

## Akzeptanzkriterien
- Klar strukturierte Ausgabe; keine Verwirrung durch Pfade.
- Snapshot-Datei erzeugt sich nur auf Wunsch/Flag.
