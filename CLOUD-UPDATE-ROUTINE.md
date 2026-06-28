# Automatische Tipp-Updates über GitHub Actions (läuft ohne PC, kostenlos)

Die Aktualisierung läuft als **GitHub Action** in der Cloud — unabhängig von deinem
PC und vom Claude-Abo/-Limit. Der Roboter (`update_bot.py`) nutzt die **Google-Gemini-API
(Gratis-Kontingent)** mit Google-Suche: er trägt Ergebnisse ein, erstellt/aktualisiert Tipps
und schreibt die K.-o.-Runde fort; die Action committet die Änderung, GitHub Pages
veröffentlicht sie aufs Handy.

## Einmalige Einrichtung

**1. Kostenlosen Gemini-API-Schlüssel holen** (keine Kreditkarte nötig):
   - https://aistudio.google.com/apikey → mit Google-Konto anmelden.
   - **Create API key** → Schlüssel kopieren (beginnt mit `AIza…`).

**2. Schlüssel als GitHub-Secret hinterlegen:**
   - https://github.com/Mintberry1628/wm-tipps/settings/secrets/actions
   - **New repository secret** → Name exakt: **`GEMINI_API_KEY`** → Value: Schlüssel einfügen → **Add secret**.

**3. Testen:**
   - https://github.com/Mintberry1628/wm-tipps/actions → **WM-Tipps Update** → **Run workflow**
     (manueller Lauf nutzt `--force`, läuft also sofort, egal welche Uhrzeit).
   - Nach ~1–2 Min sollte der Lauf grün sein; danach App am Handy neu öffnen.

## Zeitplan
- Die Action wird stündlich 13–21 Uhr (deutscher Zeit) angestoßen, der Roboter **feuert
  aber nur EINMAL pro Tag** — ca. **3 Std. vor dem ersten Spiel des Tages, spätestens 21 Uhr**.
  Alle anderen Aufrufe brechen sofort & kostenlos ab.
- Einstellbar in `update_bot.py` (`LEAD_HOURS`, `CAP_HOUR`) und `.github/workflows/update.yml` (cron).
- Modell: **`gemini-2.5-flash`** (Free Tier). Über Env-Variable `WM_MODEL` umstellbar
  (z. B. `gemini-2.5-flash-lite` noch sparsamer).

## Kosten
- GitHub Actions: kostenlos (öffentliches Repo).
- Gemini Free Tier: bei 1 Lauf/Tag mit wenigen Such-Anfragen **0 €** (Google-Suche-Grounding
  ist bis 500 Anfragen/Tag gratis; keine Kreditkarte).

## Was der Roboter tut (pro Tageslauf)
1. Endergebnisse fälliger Spiele recherchieren und eintragen (+ Tipp-Bewertung).
2. K.-o.-Baum fortschreiben (Sieger rückt deterministisch ins Folgespiel).
3. Tipps für Spiele in den nächsten ~30 Std. erstellen/auffrischen (geänderte markiert).
4. `data.js` committen & pushen (Zeitstempel täglich, Inhalt nur bei Änderung).
