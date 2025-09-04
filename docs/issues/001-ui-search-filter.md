# UI: Suche/Filter in Geräte-Listen

## Ziel
- Suchfeld je Liste (Playback/Recording), Filter nach Name und ID (case-insensitive), Live-Update.

## Aufgaben
- Suchfeld (Entry) pro Pane einfügen; KeyUp-Handler zum Filtern.
- Filter auf Name+ID anwenden; Clear-Button (X) hinzufügen.
- Auswahl und "Standard:"-Anzeige beibehalten/aktualisieren.

## Akzeptanzkriterien
- Tippen filtert die Liste live; Clear setzt volle Liste zurück.
- Stern (★) und "Standard:" bleiben korrekt sichtbar.
- Performance: kein UI-Stottern bei langen Listen.

## Hinweise
- Optional: Enter selektiert ersten Treffer; ESC leert Suche.
