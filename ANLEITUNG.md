# ⚽ WM 2026 – KI-Tipps · Anleitung (Handy / Cloud)

Eine einfache App mit KI-Ergebnisprognosen für **alle Spiele der WM 2026** –
Turnierbaum, Begründungen, Tipp-Historie, Trefferbilanz. Sie läuft **auf dem
Android-Handy ohne dass dein PC an sein muss**: gehostet auf GitHub Pages,
automatisch aktualisiert durch eine Cloud-Routine.

---

## So läuft es (Architektur in einem Satz)

Eine **Cloud-Routine** (auf Anthropics Servern, PC aus) recherchiert 5×/Tag,
aktualisiert `data.js` und pusht ins **GitHub-Repo** → **GitHub Pages** veröffentlicht
es → dein **Handy** zeigt die frischen Tipps.

## Auf dem Handy nutzen

1. Im Handy-Browser (Chrome) die Adresse öffnen:
   **`https://mintberry1628.github.io/wm-tipps/`**
   (funktioniert, sobald GitHub Pages aktiviert ist – siehe Einrichtung unten).
2. **„Zum Startbildschirm hinzufügen"** → die App bekommt ein Icon und öffnet sich
   wie eine echte App (Vollbild). Der PC muss dafür nicht laufen.
3. Beim Öffnen werden automatisch die neuesten Tipps geladen (Cache-Bust eingebaut).

## Die vier Bereiche

- **🔜 Bald** – kommende Spiele chronologisch, mit KI-Tipp, Begründung, Countdown und
  „Letzter Tipp-Check"-Zeit. **Startansicht.**
- **📋 Gruppen** – pro Gruppe die vorhergesagte Abschlusstabelle + alle Spiele.
- **🏆 K.-o.-Baum** – Turnierbaum vom Sechzehntel- bis zum Finale (seitlich scrollen).
  Teams/Tipps erscheinen automatisch, sobald sie feststehen.
- **📊 Bilanz** – Trefferquote (Tendenz & exakt), Liste **geänderter Tipps**, richtig/falsch.

## Tipp-Updates (automatisch, PC aus)

- Die Cloud-Routine aktualisiert die Prognosen **ca. 5× pro Tag** (gegen 11, 16, 19, 21,
  23 Uhr deutscher Zeit), letzter Lauf vor den Abendspielen. Neueste Fakten fließen ein:
  Ergebnisse, Verletzungen, Sperren, Aufstellungen, Form, Quoten.
- Einrichtung der Routine: siehe **`CLOUD-UPDATE-ROUTINE.md`** (einmalig, im Browser unter
  claude.ai/code/routines).

### Geänderte Tipps (wichtig für deinen Tippschein!)

Ändert die KI einen Tipp (z. B. wegen Verletzung), wird die Spielkarte **orange**
markiert mit „⚠ Tipp geändert" inkl. **vorher → jetzt** und **Grund**. So weißt du
sofort, welchen eigenen Tipp du anpassen solltest. Gesammelt auch unter **📊 Bilanz**.

## Erinnerung 1 Stunde vor jedem Spiel (Kalender)

Kalender-Erinnerungen mit Alarm **1 Std. vor Anpfiff** („App öffnen & Tipp prüfen"):

- **Fertige Datei** `wm2026-erinnerungen.ics` einmal am Handy öffnen → in den Kalender
  übernehmen (alle 104 Spiele; die Anstoßzeiten ändern sich nie).
- **Oder in der App:** Button „🔔 Alle Erinnerungen (.ics) laden" bzw. „🔔 Erinnerung"
  je Spiel. Die Anstoß- und Check-Zeiten stehen auch auf jeder Karte.

## Historie & Bilanz

Alle Tipps und echten Ergebnisse bleiben dauerhaft gespeichert (Verlauf je Spiel).
In **📊 Bilanz** siehst du jederzeit, wo die KI richtig/falsch lag.

---

## Optional: lokal am PC testen

Nicht nötig für den Handy-Betrieb, aber praktisch zum Ausprobieren:
Doppelklick **`START-Windows.bat`** → `http://localhost:8026`.

## Hinweise

- **Flaggen:** Auf Android erscheinen echte Länderflaggen; unter Windows zeigt der
  Browser stattdessen 2-Buchstaben-Codes (z. B. „BR"). Windows-Eigenheit, kein Fehler.
- Die 4 vor App-Start gespielten Spiele zählen nicht in die Trefferbilanz (kein
  Vorab-Live-Tipp), ihre Ergebnisse sind aber sichtbar.

## Dateien

| Datei | Zweck |
|---|---|
| `index.html` | die App |
| `data.js` | alle Spiele, Tipps, Historie, Ergebnisse (Cloud-Routine pflegt sie) |
| `manifest.webmanifest`, `icon.svg` | App-Icon / „Zum Startbildschirm hinzufügen" |
| `wm2026-erinnerungen.ics` | Kalender-Erinnerungen (1 Std. vor jedem Spiel) |
| `CLOUD-UPDATE-ROUTINE.md` | Einrichtung der automatischen Cloud-Aktualisierung |
| `gen_ics.py` | erzeugt die .ics neu (optional) |
| `serve.py`, `START-Windows.bat` | optionaler lokaler Test am PC |
| `build_data.py` | einmaliger Erst-Aufbau (intern) |
