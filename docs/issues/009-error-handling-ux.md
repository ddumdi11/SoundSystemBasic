# Fehlerbehandlung: COM-HRESULT-Summary und UX-Feedback

## Ziel
- Besseres Feedback beim Setzen von Defaults (Teil-/Fehlschläge verständlich).

## Aufgaben
- CLI `--summary`: Rollen/HRESULTs komprimiert ausgeben.
- UI: Statusmeldungen bei Teilerfolg (z. B. Multimedia ok, Console/Comm fail) klar formulieren.
- Optional: Debug-Loglevel für detaillierte HRESULTs.

## Akzeptanzkriterien
- Nutzer versteht Erfolg/Teilerfolg/Fehlschlag ohne JSON.
- Keine überladene UI; Details nur bei Bedarf.
