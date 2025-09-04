# CLI: Summary/Ergonomie-Verbesserungen

## Ziel
- Kompaktere Ausgaben und mehr Komfort.

## Aufgaben
- `win set-default-* --summary`: kurze Erfolgsmeldung statt JSON.
- `win list --show-defaults`: Default in der Ausgabe markieren (★).
- `win volume --get`: aktuelle Lautstärke ausgeben.

## Akzeptanzkriterien
- Befehle liefern klare, kurze Ergebnisse.
- Rückgabecodes bleiben korrekt (0 Erfolg, !=0 Fehler).
