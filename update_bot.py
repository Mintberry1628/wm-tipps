# -*- coding: utf-8 -*-
"""
WM-2026 Update-Roboter fuer GitHub Actions (laeuft in der Cloud, PC aus).
- traegt Endergebnisse gespielter Spiele ein (per Gemini + Google-Suche)
- erstellt/aktualisiert Tipps fuer anstehende Spiele (per Gemini + Google-Suche)
- loest die K.-o.-Runde deterministisch fort (Sieger -> Folgespiel)
- aktualisiert meta.lastUpdate; schreibt data.js

Aufrufe:
  python update_bot.py --selftest   # ohne API: zeigt nur, was zu tun waere
  python update_bot.py              # echter Lauf (braucht GEMINI_API_KEY)
"""
import json, io, os, sys, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.js")
MODEL = os.environ.get("WM_MODEL", "gemini-2.5-flash")
SELFTEST = "--selftest" in sys.argv
FORCE = "--force" in sys.argv   # manueller Lauf: Zeitfenster-Pruefung ueberspringen
LEAD_HOURS = 3                  # ~3h vor dem ersten Spiel des Tages
CAP_HOUR = 21                   # spaetestens 21:00 deutscher Zeit

def now_berlin():
    # Cloud laeuft in UTC; WM-2026 ist im Sommer -> MESZ = UTC+2
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)

def iso_now():
    return now_berlin().replace(microsecond=0, tzinfo=None).isoformat() + "+02:00"

def load():
    raw = io.open(DATA, "r", encoding="utf-8").read().strip()
    prefix = raw[:raw.index("{")]
    data = json.loads(raw[raw.index("{"):raw.rindex("}")+1])
    return prefix, data

def save(prefix, data):
    io.open(DATA, "w", encoding="utf-8").write(prefix + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")

def sgn(x): return (x > 0) - (x < 0)
def D(iso): return datetime.datetime.fromisoformat(iso) if iso else None

# ---------- deterministische K.-o.-Fortschreibung ----------
def winner_code(m):
    """Code des Weiterkommenden eines gespielten K.-o.-Spiels, sonst None."""
    r = m.get("result")
    if not r: return None
    if r["home"] > r["away"]: return m.get("homeCode")
    if r["away"] > r["home"]: return m.get("awayCode")
    return (r.get("advancesCode") or None)  # Unentschieden -> Elfmeter: aus Recherche

def team_of(data, code):
    for m in data["matches"]:
        if m.get("homeCode") == code and m.get("home"): return (m["home"], code)
        if m.get("awayCode") == code and m.get("away"): return (m["away"], code)
    return (code, code)

def propagate(data):
    by_no = {m["matchNo"]: m for m in data["matches"]}
    changes = []
    # Feeder je Zielspiel sammeln
    feeders = {}
    for m in data["matches"]:
        if m.get("feedsInto"):
            feeders.setdefault(m["feedsInto"], []).append(m["matchNo"])
        if m.get("loserFeedsInto"):
            feeders.setdefault(m["loserFeedsInto"], []).append(("L", m["matchNo"]))
    for target_no, fl in feeders.items():
        tgt = by_no.get(target_no)
        if not tgt or tgt.get("teamsKnown"):
            continue
        # nur normale Sieger-Feeder (keine Verlierer) bestimmen Heim/Auswaerts per matchNo
        win_feeders = sorted([x for x in fl if not isinstance(x, tuple)])
        slots = []
        for fno in win_feeders:
            wc = winner_code(by_no.get(fno, {}))
            slots.append((fno, wc))
        # Spiel um Platz 3: Verlierer der Halbfinals
        lose_feeders = [x[1] for x in fl if isinstance(x, tuple)]
        if lose_feeders:
            slots = []
            for fno in sorted(lose_feeders):
                fm = by_no.get(fno, {})
                wc = winner_code(fm)
                lc = None
                if wc and fm.get("result"):
                    lc = fm["awayCode"] if wc == fm["homeCode"] else fm["homeCode"]
                slots.append((fno, lc))
        if len(slots) == 2 and all(s[1] for s in slots):
            (lo, hc), (hi, ac) = slots[0], slots[1]
            hn, _ = team_of(data, hc); an, _ = team_of(data, ac)
            tgt["homeCode"], tgt["awayCode"] = hc, ac
            tgt["home"], tgt["away"] = hn, an
            tgt["homePlaceholder"] = tgt["awayPlaceholder"] = None
            tgt["teamsKnown"] = True
            changes.append(f"Spiel {target_no}: {hc} vs {ac} aufgeloest")
    return changes

# ---------- Zielauswahl ----------
def select(data):
    now = now_berlin().replace(tzinfo=None)
    need_result, need_pred = [], []
    for m in data["matches"]:
        if not m.get("teamsKnown", True):
            continue
        ko = D(m["kickoffBerlin"])
        ko_naive = ko.replace(tzinfo=None) if ko else None
        played = bool(m.get("result"))
        if not played and ko_naive and ko_naive < now - datetime.timedelta(hours=2.5):
            need_result.append(m)
        if not played:
            if not m.get("prediction"):
                need_pred.append(m)
            elif ko_naive and now <= ko_naive <= now + datetime.timedelta(hours=30):
                need_pred.append(m)
    return need_result, need_pred

# ---------- Claude-Aufrufe ----------
def llm_json(client, prompt):
    """Ein Gemini-Aufruf mit Google-Suche (Grounding); parst JSON aus dem Antworttext."""
    from google.genai import types
    cfg = types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
    resp = client.models.generate_content(model=MODEL, contents=prompt, config=cfg)
    text = resp.text or ""
    mobj = re.search(r"\{.*\}", text, re.S)
    if not mobj:
        raise ValueError("Keine JSON-Antwort: " + text[:200])
    return json.loads(mobj.group(0))

def research_result(client, m):
    ko = D(m["kickoffBerlin"]).strftime("%d.%m.%Y")
    knockout = m["stage"] == "knockout"
    adv_field = ', "advancesCode": "<3-Buchstaben-Code des Weitergekommenen>"' if knockout else ""
    adv_hint = (" Falls das K.-o.-Spiel nach regulaerer Zeit unentschieden war, gib in advancesCode den "
                "per Verlaengerung/Elfmeter weitergekommenen Code an.") if knockout else ""
    teams = m["home"] + " (" + m["homeCode"] + ") gegen " + m["away"] + " (" + m["awayCode"] + ")"
    prompt = ("Suche das ENDERGEBNIS dieses Spiels der Fussball-WM 2026: " + teams +
              ", angesetzt am " + ko + ". Antworte NUR mit JSON: "
              '{"scoreHome": <Tore Heim>, "scoreAway": <Tore Auswaerts>, '
              '"notes": "<1 kurzer Satz: Torschuetzen/Verlauf>"' + adv_field + "}. "
              'Wenn das Spiel noch nicht beendet ist, antworte NUR mit {"played": false}.' + adv_hint)
    return llm_json(client, prompt)

def research_pred(client, m):
    ko = D(m["kickoffBerlin"]).strftime("%d.%m.%Y %H:%M")
    knockout = m["stage"] == "knockout"
    rule = ('K.-o.-Spiel: KEIN Unentschieden, nenne einen Sieger (bei erwartetem Gleichstand decisive tippen, z.B. 2:1, und "n.V." im reason). '
            if knockout else 'Gruppenspiel: Unentschieden erlaubt (winnerCode "X").')
    prompt = (f'Fussball-WM 2026, {m.get("group","")}: {m["home"]} ({m["homeCode"]}) gegen {m["away"]} ({m["awayCode"]}), '
              f'Anstoss {ko} (deutsche Zeit). Recherchiere kurz Form/Verletzungen/Sperren/Quoten und erstelle eine Ergebnisprognose. {rule} '
              f'Antworte NUR mit JSON: {{"scoreHome": <int>, "scoreAway": <int>, "winnerCode": "<Code oder X>", '
              f'"confidence": "niedrig|mittel|hoch", "reasons": ["2-3 kurze deutsche Stichpunkte"]}}.')
    return llm_json(client, prompt)

# ---------- Anwenden ----------
def apply_result(m, r):
    if r.get("played") is False or "scoreHome" not in r:
        return False
    sh, sa = int(r["scoreHome"]), int(r["scoreAway"])
    res = {"home": sh, "away": sa, "notes": r.get("notes", ""), "at": iso_now()}
    if r.get("advancesCode"): res["advancesCode"] = r["advancesCode"]
    m["result"] = res
    m["status"] = "gespielt"
    pr = m.get("prediction")
    if pr:
        m["evaluation"] = {"tendency": sgn(pr["scoreHome"]-pr["scoreAway"]) == sgn(sh-sa),
                           "exact": pr["scoreHome"] == sh and pr["scoreAway"] == sa}
        pr["changed"] = False
    return True

def apply_pred(m, p):
    sh, sa = int(p["scoreHome"]), int(p["scoreAway"])
    wc = p.get("winnerCode") or ("X" if sh == sa else (m["homeCode"] if sh > sa else m["awayCode"]))
    outcome = "1" if sh > sa else ("2" if sa > sh else "X")
    old = m.get("prediction")
    changed = bool(old) and (old["scoreHome"] != sh or old["scoreAway"] != sa or old.get("winnerCode") != wc)
    note = None
    if changed:
        note = f'Tipp angepasst (vorher {old["scoreHome"]}:{old["scoreAway"]})'
    pred = {"scoreHome": sh, "scoreAway": sa, "winnerCode": wc, "outcome": outcome,
            "confidence": p.get("confidence", "mittel"), "reasons": p.get("reasons", []),
            "updatedAt": iso_now(), "changed": changed, "changeNote": note}
    m["prediction"] = pred
    snap = {"scoreHome": sh, "scoreAway": sa, "winnerCode": wc, "confidence": pred["confidence"],
            "reasons": pred["reasons"], "at": iso_now(), "changeNote": note}
    m.setdefault("history", []).append(snap)
    return changed

# ---------- Zeitfenster: nur 1x/Tag, ~3h vor dem 1. Spiel, spaetestens 21:00 ----------
def decide_run(data):
    if FORCE:
        return True, "manueller Lauf (--force)"
    now = now_berlin().replace(tzinfo=None)
    last = data.get("meta", {}).get("lastUpdate")
    if last and D(last) and D(last).date() == now.date():
        return False, "heute bereits aktualisiert"
    horizon = now + datetime.timedelta(hours=18)
    upcoming = sorted([D(m["kickoffBerlin"]).replace(tzinfo=None) for m in data["matches"]
                       if m.get("teamsKnown", True) and not m.get("result")
                       and now < D(m["kickoffBerlin"]).replace(tzinfo=None) <= horizon])
    if not upcoming:
        return False, "kein Spiel in den naechsten 18 Std."
    target = upcoming[0] - datetime.timedelta(hours=LEAD_HOURS)
    if now >= target:
        return True, f"innerhalb {LEAD_HOURS} Std. vor Anstoss ({upcoming[0].strftime('%H:%M')})"
    if now.hour >= CAP_HOUR:
        return True, f"{CAP_HOUR}:00-Grenze erreicht (Spiel um {upcoming[0].strftime('%H:%M')})"
    return False, f"zu frueh – Lauf ab {target.strftime('%H:%M')} oder {CAP_HOUR}:00"

# ---------- main ----------
def main():
    prefix, data = load()
    now = now_berlin().replace(tzinfo=None)
    run, reason = decide_run(data)
    print(f"Zeitfenster-Entscheidung: {'LAUFEN' if run else 'ueberspringen'} – {reason}")
    if not run and not SELFTEST:
        return
    # vergangene Spiele: alte "changed"-Markierung entfernen
    for m in data["matches"]:
        ko = D(m["kickoffBerlin"]); pr = m.get("prediction")
        if pr and ko and ko.replace(tzinfo=None) < now:
            pr["changed"] = False
    prop = propagate(data)
    need_result, need_pred = select(data)
    print(f"Jetzt: {iso_now()}")
    print(f"K.-o. aufgeloest: {prop}")
    print(f"Ergebnisse offen: {[m['matchNo'] for m in need_result]}")
    print(f"Tipps zu erstellen/aktualisieren: {[m['matchNo'] for m in need_pred]}")
    if SELFTEST:
        print("(Selftest – keine API-Aufrufe, nichts geschrieben.)")
        return

    from google import genai
    client = genai.Client()  # liest GEMINI_API_KEY (oder GOOGLE_API_KEY)
    touched = bool(prop)
    for m in need_result:
        try:
            r = research_result(client, m)
            if apply_result(m, r):
                print(f"Ergebnis {m['matchNo']}: {m['result']['home']}:{m['result']['away']}"); touched = True
        except Exception as e:
            print(f"! Ergebnis {m['matchNo']} fehlgeschlagen: {e}")
    # nach neuen Ergebnissen erneut K.-o. fortschreiben (Sieger weiterruecken)
    if propagate(data): touched = True
    # neu aufgeloeste K.-o.-Spiele brauchen ggf. einen Tipp
    _, need_pred = select(data)
    for m in need_pred:
        try:
            p = research_pred(client, m)
            ch = apply_pred(m, p)
            print(f"Tipp {m['matchNo']}: {p['scoreHome']}:{p['scoreAway']}" + (" (geaendert)" if ch else "")); touched = True
        except Exception as e:
            print(f"! Tipp {m['matchNo']} fehlgeschlagen: {e}")
    # Tageslauf immer stempeln + speichern, damit weitere Aufrufe heute abbrechen
    data["meta"]["lastUpdate"] = iso_now()
    save(prefix, data)
    print("data.js geschrieben." if touched else "Nur Zeitstempel aktualisiert (keine inhaltliche Aenderung).")

if __name__ == "__main__":
    main()
