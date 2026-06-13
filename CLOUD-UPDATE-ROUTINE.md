# Cloud-Routine: automatische Tipp-Updates (PC darf aus sein)

Diese Routine läuft auf Anthropics Cloud-Servern (unabhängig vom PC) und
aktualisiert mehrmals täglich die Tipps im GitHub-Repo. GitHub Pages
veröffentlicht die Änderung automatisch → das Handy sieht frische Tipps.

## Einrichtung (einmalig, im Browser)

1. Öffne **https://claude.ai/code/routines** → **„New routine"**.
2. **Repository:** dein Repo (z. B. `wm-tipps`) auswählen und verbinden
   (GitHub-OAuth durchlaufen, falls noch nicht verbunden).
3. Beim Repo **„Allow unrestricted branch pushes"** aktivieren
   (sonst darf die Routine nicht nach `main` pushen).
4. **Trigger → Schedule**, Cron (UTC):
   ```
   0 9,14,17,19,21 * * *
   ```
   Das entspricht **ca. 11, 16, 19, 21, 23 Uhr deutscher Zeit** (MESZ) = 5×/Tag
   (= Limit im Pro-Plan; der letzte Lauf liegt vor den Abendspielen).
5. **Network access:** „Full" oder „Trusted" + erlaubte Domains für die Recherche
   (z. B. kicker.de, espn.com, fifa.com, wikipedia.org, sportschau.de).
6. **Prompt:** den gesamten Text unter „PROMPT" (unten) einfügen.
7. **Create** → danach einmal **„Run now"** zum Testen.

## PROMPT (komplett einfügen)

```
Du pflegst die Datenbasis einer WM-2026-Fussball-Tipp-App in DIESEM GitHub-Repo.
Im Repo-Root liegen index.html (App) und data.js (Daten). Die App wird per GitHub
Pages gehostet; nach einem Push ist die Aenderung in ~1 Minute live.

ZIEL: Die KI-Prognosen aktuell halten – mit den neuesten Fakten (Ergebnisse,
Verletzungen, Sperren, Aufstellungen, Form, Quoten) bis kurz vor Anpfiff – und
die Aenderungen ins Repo pushen.

ABLAUF:

1) Aktuelle Zeit bestimmen. Die Cloud laeuft in UTC; rechne in Europe/Berlin um
   (im Juni/Juli = MESZ = UTC+2). Alle kickoffBerlin-Werte sind ISO-8601 mit +02:00.

2) data.js lesen. Inhalt ist `window.WM_DATA = { ... };`. Den JSON-Teil zwischen
   erster `{` und letzter `}` parsen. Struktur: meta + matches[] (Felder: matchNo,
   stage "group"/"knockout", roundCode, group, matchday, home/away/homeCode/awayCode,
   homePlaceholder/awayPlaceholder, kickoffBerlin, venue, city, feedsInto,
   loserFeedsInto, status, teamsKnown, prediction{scoreHome,scoreAway,winnerCode,
   outcome,confidence,reasons[],updatedAt,changed,changeNote}, history[], result,
   evaluation, countsForStats, finalCheckBerlin).

3) RELEVANTE SPIELE waehlen:
   a) status != "gespielt" und kickoffBerlin innerhalb der naechsten ~30 Std -> Tipp pruefen/aktualisieren.
   b) status != "gespielt" und kickoffBerlin mehr als ~2,5 Std in der Vergangenheit -> Endergebnis recherchieren und eintragen.

4) RECHERCHE (WebSearch/WebFetch; kicker.de, ESPN, fifa.com, sportschau.de, Wettquoten):
   pro relevantem Spiel die prognoserelevanten Fakten holen: Endergebnis (falls gespielt),
   Verletzungen/Sperren/Aufstellungen, Form, Quoten, Tabellen-/Aufstiegssituation.

5) PROGNOSEN AKTUALISIEREN (nur bei konkretem sachlichem Grund aendern – kein Rauschen!):
   - Neue Prognose: scoreHome, scoreAway, winnerCode (Sieger-Code oder "X"),
     outcome ("1"/"X"/"2"), confidence (niedrig/mittel/hoch), 2-4 deutsche reasons.
   - Wenn sich scoreHome/scoreAway/winnerCode aendern -> AENDERUNG:
       prediction.changed=true; prediction.changeNote="<kurz warum, z.B. 'Hakimi verletzt raus -> Tipp 2:1 auf 1:1'>";
       neuen Snapshot an history anhaengen {scoreHome,scoreAway,winnerCode,confidence,reasons,at:<jetzt ISO+02:00>,changeNote};
       prediction.updatedAt=jetzt.
   - Unveraendert: reasons ggf. auffrischen, prediction.updatedAt=jetzt, changed NICHT neu true setzen.
   - Jedes Spiel, dessen kickoffBerlin bereits vergangen ist: prediction.changed=false.

6) GESPIELTE SPIELE eintragen (Endergebnis gefunden):
   result={home,away,notes:"<1 Satz Verlauf/Torschuetzen>",at:<jetzt>}; status="gespielt";
   evaluation={tendency:<1X2 korrekt?>,exact:<genau korrekt?>} bezogen auf prediction;
   prediction.changed=false. countsForStats unveraendert (Spiele 1-4 bleiben false).

7) K.-O.-BAUM FORTSCHREIBEN:
   - Sind alle 3 Spieltage einer Gruppe gespielt: Abschlusstabelle berechnen (Punkte,
     dann Tordifferenz, dann erzielte Tore). Gruppensieger/-zweiter bestimmen; fuer die
     besten Gruppendritten die offizielle FIFA-Zuteilungstabelle der WM 2026 nachschlagen.
     Damit Platzhalter der Sechzehntelfinals (roundCode "R32") aufloesen:
     home/away/homeCode/awayCode setzen, teamsKnown=true.
   - Ist ein K.-o.-Spiel gespielt: Sieger ins via feedsInto referenzierte Folgespiel
     eintragen (niedrigere feeder-Spielnummer = Heim-Slot); bei Halbfinals zusaetzlich
     Verlierer ins via loserFeedsInto referenzierte Spiel um Platz 3.
   - Sobald beide echten Teams feststehen und keine prediction existiert: prediction
     erstellen (mit reasons) und Anfangs-Snapshot in history.

8) meta.lastUpdate = jetzt (ISO+02:00). meta.generatedAt unveraendert lassen.

9) data.js zurueckschreiben: exakt `window.WM_DATA = ` + huebsch eingeruecktes JSON
   (indent 1) + `;` + Zeilenumbruch. NICHTS loeschen – history/Tipps/Ergebnisse sind
   append-only und muessen vollstaendig erhalten bleiben.

10) Aenderungen committen und pushen:
    git add data.js
    git commit -m "Tipp-Update <Berlin-Datum/Zeit>"
    git push
    (Wenn es nichts zu aendern gab, KEIN leerer Commit – dann nichts pushen.)

WICHTIG:
- Niemals gespeicherte Tipps/Ergebnisse loeschen oder verfaelschen – nur fortschreiben.
- Tipp-Aenderungen nur mit nachvollziehbarem, faktischem Grund. Die Markierung
  (changed + changeNote) ist essenziell, damit der Nutzer seinen eigenen Tippschein anpassen kann.
- Antworte am Ende mit kurzer deutscher Zusammenfassung: aktualisierte/eingetragene Spiele,
  geaenderte Tipps (mit Grund), naechster relevanter Anpfiff.
```

## Verwaltung

- Alle Routinen ansehen/bearbeiten: https://claude.ai/code/routines
- Sofort testen: in der Routine **„Run now"**.
- Limit: Pro = 5 Läufe/Tag, Max = 15/Tag. „Run now"-Tests zählen separat.
