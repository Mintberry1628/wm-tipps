# Automatische Tipp-Updates über GitHub Actions (läuft ohne PC)

Die Aktualisierung läuft als **GitHub Action** in der Cloud — unabhängig von deinem
PC und vom Claude-Abo/-Limit. Der Roboter (`update_bot.py`) trägt Ergebnisse ein,
erstellt/aktualisiert Tipps (per Anthropic-API mit Websuche) und schreibt die K.-o.-Runde
fort; die Action committet die Änderung, GitHub Pages veröffentlicht sie aufs Handy.

## Einmalige Einrichtung

**1. Anthropic-API-Schlüssel mit Guthaben anlegen** (getrennt vom Claude-Abo):
   - https://console.anthropic.com → anmelden (gleiche E-Mail möglich).
   - **Billing** → Zahlungsmittel hinterlegen → **5 $ Guthaben** kaufen (reicht fürs ganze Turnier).
   - **API keys** → **Create Key** → Schlüssel kopieren (beginnt mit `sk-ant-...`).

**2. Schlüssel als GitHub-Secret hinterlegen:**
   - https://github.com/Mintberry1628/wm-tipps/settings/secrets/actions
   - **New repository secret** → Name exakt: **`ANTHROPIC_API_KEY`** → Value: Schlüssel einfügen → **Add secret**.

**3. Testen:**
   - https://github.com/Mintberry1628/wm-tipps/actions → **WM-Tipps Update** → **Run workflow**.
   - Nach ~1–2 Min sollte der Lauf grün sein; danach zeigt das Handy den frischen Stand.

## Zeitplan
- Läuft automatisch **3× täglich** (ca. 10:00 / 18:00 / 21:00 deutscher Zeit), siehe
  `.github/workflows/update.yml` (`cron` in UTC). Häufigkeit dort anpassbar.
- Modell: **Haiku 4.5** (günstig). Über die Env-Variable `WM_MODEL` umstellbar.

## Kosten
- GitHub Actions: kostenlos (öffentliches Repo).
- Anthropic-API: ~0,10 $/Lauf → grob **5–10 $ fürs restliche Turnier**.

## Was der Roboter tut (pro Lauf)
1. Endergebnisse fälliger Spiele recherchieren und eintragen (+ Tipp-Bewertung).
2. K.-o.-Baum fortschreiben (Sieger rückt deterministisch ins Folgespiel).
3. Tipps für Spiele in den nächsten ~30 Std. erstellen/auffrischen (geänderte markiert).
4. Nur bei Änderung: `data.js` committen & pushen.
