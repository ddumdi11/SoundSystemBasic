# UI: Auto-Select/Scroll zu Standard + externe Änderungen erkennen

## Ziel
- Beim Start/Refresh zum aktuellen Standard scrollen und selektieren.
- Externe Änderungen (außerhalb der App) erkennen und UI aktualisieren.

## Aufgaben
- Beim Refresh: `see(index)` auf Default, Auswahl setzen.
- Optionales Polling (z. B. alle 3 s) oder manueller Refresh-Hotkey (F5).
- Deduplizieren, um Flackern zu vermeiden (nur aktualisieren, wenn sich etwas ändert).

## Akzeptanzkriterien
- Stern (★) sitzt nach Start/Refresh sichtbar auf dem Default.
- Externer Wechsel wird innerhalb ~3 s reflektiert (falls Polling aktiv).
- Kein merkliches UI-Flackern.

## Hinweise
- Polling deaktivierbar/konfigurierbar machen; CPU-Last gering halten.
