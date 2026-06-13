# -*- coding: utf-8 -*-
"""
Baut data.js (window.WM_DATA) fuer die WM-2026-Tipp-App aus dem Prognose-Workflow.
Einmaliger Initial-Build. Danach pflegt der Update-Task data.js direkt weiter.
"""
import json, datetime, os, io

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "_predictions_raw.json")
OUT = os.path.join(HERE, "data.js")

NOW = "2026-06-13T12:00:00+02:00"  # Zeitpunkt des Initial-Tipps

def minus1h(iso):
    d = datetime.datetime.fromisoformat(iso)
    return (d - datetime.timedelta(hours=1)).isoformat()

def outcome(sh, sa):
    return "1" if sh > sa else ("2" if sa > sh else "X")

# ---------- Gruppenspiele aus Workflow ----------
with io.open(RAW, "r", encoding="utf-8") as f:
    raw = json.load(f)
results = raw["result"]["results"]

EARLY_PLAYED = {1, 2, 3, 4}  # vor App-Start gespielt -> zaehlen nicht fuer Bilanz

matches = []
for grp in results:
    gletter = grp["group"].replace("Gruppe", "").strip()  # "Gruppe C" -> "C"
    for m in grp["matches"]:
        played = bool(m.get("played"))
        result = None
        if played and m.get("actualHome", -1) >= 0:
            result = {"home": m["actualHome"], "away": m["actualAway"],
                      "notes": m.get("actualNotes", ""), "at": NOW}
        pred = {
            "scoreHome": m["scoreHome"], "scoreAway": m["scoreAway"],
            "winnerCode": m["winnerCode"], "outcome": outcome(m["scoreHome"], m["scoreAway"]),
            "confidence": m.get("confidence", "mittel"),
            "reasons": m.get("reasons", []),
            "updatedAt": NOW, "changed": False, "changeNote": None,
        }
        hist = [{"scoreHome": m["scoreHome"], "scoreAway": m["scoreAway"],
                 "winnerCode": m["winnerCode"], "confidence": m.get("confidence", "mittel"),
                 "reasons": m.get("reasons", []), "at": NOW, "changeNote": None}]
        matches.append({
            "matchNo": m["matchNo"], "stage": "group", "group": gletter,
            "roundCode": "GROUP", "matchday": m["matchday"],
            "home": m["home"], "away": m["away"],
            "homeCode": m["homeCode"], "awayCode": m["awayCode"],
            "homePlaceholder": None, "awayPlaceholder": None,
            "kickoffBerlin": m["kickoffBerlin"], "kickoffLocal": m.get("kickoffLocal", ""),
            "venue": m.get("venue", ""), "city": m.get("city", ""),
            "feedsInto": None, "loserFeedsInto": None,
            "status": "gespielt" if played else "geplant",
            "teamsKnown": True,
            "prediction": pred, "history": hist, "result": result,
            "evaluation": None,
            "countsForStats": (not played),
            "finalCheckBerlin": minus1h(m["kickoffBerlin"]),
        })

# ---------- K.-o.-Phase (Platzhalter, Teams folgen) ----------
KO = [
 (73,"R32","Zweiter Gruppe A","Zweiter Gruppe B",90,None,"2026-06-28T21:00:00+02:00","SoFi Stadium","Inglewood"),
 (74,"R32","Sieger Gruppe E","Dritter Gruppe A/B/C/D/F",89,None,"2026-06-29T22:30:00+02:00","Gillette Stadium","Foxborough"),
 (75,"R32","Sieger Gruppe F","Zweiter Gruppe C",90,None,"2026-06-30T03:00:00+02:00","Estadio BBVA","Monterrey"),
 (76,"R32","Sieger Gruppe C","Zweiter Gruppe F",91,None,"2026-06-29T19:00:00+02:00","NRG Stadium","Houston"),
 (77,"R32","Sieger Gruppe I","Dritter Gruppe C/D/F/G/H",89,None,"2026-06-30T23:00:00+02:00","MetLife Stadium","East Rutherford"),
 (78,"R32","Zweiter Gruppe E","Zweiter Gruppe I",91,None,"2026-06-30T19:00:00+02:00","AT&T Stadium","Arlington"),
 (79,"R32","Sieger Gruppe A","Dritter Gruppe C/E/F/H/I",92,None,"2026-07-01T03:00:00+02:00","Estadio Azteca","Mexiko-Stadt"),
 (80,"R32","Sieger Gruppe L","Dritter Gruppe E/H/I/J/K",92,None,"2026-07-01T18:00:00+02:00","Mercedes-Benz Stadium","Atlanta"),
 (81,"R32","Sieger Gruppe D","Dritter Gruppe B/E/F/I/J",94,None,"2026-07-02T02:00:00+02:00","Levi's Stadium","Santa Clara"),
 (82,"R32","Sieger Gruppe G","Dritter Gruppe A/E/H/I/J",94,None,"2026-07-01T22:00:00+02:00","Lumen Field","Seattle"),
 (83,"R32","Zweiter Gruppe K","Zweiter Gruppe L",93,None,"2026-07-03T01:00:00+02:00","BMO Field","Toronto"),
 (84,"R32","Sieger Gruppe H","Zweiter Gruppe J",93,None,"2026-07-02T21:00:00+02:00","SoFi Stadium","Inglewood"),
 (85,"R32","Sieger Gruppe B","Dritter Gruppe E/F/G/I/J",96,None,"2026-07-03T05:00:00+02:00","BC Place","Vancouver"),
 (86,"R32","Sieger Gruppe J","Zweiter Gruppe H",95,None,"2026-07-04T00:00:00+02:00","Hard Rock Stadium","Miami Gardens"),
 (87,"R32","Sieger Gruppe K","Dritter Gruppe D/E/I/J/L",96,None,"2026-07-04T03:30:00+02:00","Arrowhead Stadium","Kansas City"),
 (88,"R32","Zweiter Gruppe D","Zweiter Gruppe G",95,None,"2026-07-03T20:00:00+02:00","AT&T Stadium","Arlington"),
 (89,"R16","Sieger Spiel 74","Sieger Spiel 77",97,None,"2026-07-04T23:00:00+02:00","Lincoln Financial Field","Philadelphia"),
 (90,"R16","Sieger Spiel 73","Sieger Spiel 75",97,None,"2026-07-04T19:00:00+02:00","NRG Stadium","Houston"),
 (91,"R16","Sieger Spiel 76","Sieger Spiel 78",99,None,"2026-07-05T22:00:00+02:00","MetLife Stadium","East Rutherford"),
 (92,"R16","Sieger Spiel 79","Sieger Spiel 80",99,None,"2026-07-06T02:00:00+02:00","Estadio Azteca","Mexiko-Stadt"),
 (93,"R16","Sieger Spiel 83","Sieger Spiel 84",98,None,"2026-07-06T21:00:00+02:00","AT&T Stadium","Arlington"),
 (94,"R16","Sieger Spiel 81","Sieger Spiel 82",98,None,"2026-07-07T02:00:00+02:00","Lumen Field","Seattle"),
 (95,"R16","Sieger Spiel 86","Sieger Spiel 88",100,None,"2026-07-07T18:00:00+02:00","Mercedes-Benz Stadium","Atlanta"),
 (96,"R16","Sieger Spiel 85","Sieger Spiel 87",100,None,"2026-07-07T22:00:00+02:00","BC Place","Vancouver"),
 (97,"QF","Sieger Spiel 89","Sieger Spiel 90",101,None,"2026-07-09T22:00:00+02:00","Gillette Stadium","Foxborough"),
 (98,"QF","Sieger Spiel 93","Sieger Spiel 94",101,None,"2026-07-10T21:00:00+02:00","SoFi Stadium","Inglewood"),
 (99,"QF","Sieger Spiel 91","Sieger Spiel 92",102,None,"2026-07-11T23:00:00+02:00","Hard Rock Stadium","Miami Gardens"),
 (100,"QF","Sieger Spiel 95","Sieger Spiel 96",102,None,"2026-07-12T03:00:00+02:00","Arrowhead Stadium","Kansas City"),
 (101,"SF","Sieger Spiel 97","Sieger Spiel 98",104,103,"2026-07-14T21:00:00+02:00","AT&T Stadium","Arlington"),
 (102,"SF","Sieger Spiel 99","Sieger Spiel 100",104,103,"2026-07-15T21:00:00+02:00","Mercedes-Benz Stadium","Atlanta"),
 (103,"P3","Verlierer Spiel 101","Verlierer Spiel 102",None,None,"2026-07-18T23:00:00+02:00","Hard Rock Stadium","Miami Gardens"),
 (104,"FINAL","Sieger Spiel 101","Sieger Spiel 102",None,None,"2026-07-19T21:00:00+02:00","MetLife Stadium","East Rutherford"),
]
RLABEL = {"R32":"Sechzehntelfinale","R16":"Achtelfinale","QF":"Viertelfinale","SF":"Halbfinale","P3":"Spiel um Platz 3","FINAL":"Finale"}
for (no, rc, hp, ap, feed, lfeed, ko, ven, city) in KO:
    matches.append({
        "matchNo": no, "stage": "knockout", "group": RLABEL[rc],
        "roundCode": rc, "matchday": None,
        "home": None, "away": None, "homeCode": None, "awayCode": None,
        "homePlaceholder": hp, "awayPlaceholder": ap,
        "kickoffBerlin": ko, "kickoffLocal": "", "venue": ven, "city": city,
        "feedsInto": feed, "loserFeedsInto": lfeed,
        "status": "geplant", "teamsKnown": False,
        "prediction": None, "history": [], "result": None, "evaluation": None,
        "countsForStats": True, "finalCheckBerlin": minus1h(ko),
    })

matches.sort(key=lambda x: x["matchNo"])

data = {
    "meta": {
        "tournament": "FIFA WM 2026",
        "host": "USA / Kanada / Mexiko",
        "timezone": "Europe/Berlin",
        "generatedAt": NOW,
        "lastUpdate": NOW,
        "updateSchedule": "mehrmals taeglich (ca. 5x), zuletzt ~1 Std. vor Anpfiff",
        "appVersion": 1,
    },
    "matches": matches,
}

js = "window.WM_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write(js)

# Plausi-Checks
ng = sum(1 for m in matches if m["stage"] == "group")
nk = sum(1 for m in matches if m["stage"] == "knockout")
npred = sum(1 for m in matches if m["prediction"])
played = sum(1 for m in matches if m["result"])
print("Gruppenspiele:", ng, "| K.-o.-Spiele:", nk, "| mit Tipp:", npred, "| gespielt:", played)
print("geschrieben:", OUT, "(", os.path.getsize(OUT), "Bytes )")
assert ng == 72, "Erwarte 72 Gruppenspiele"
assert nk == 32, "Erwarte 32 K.-o.-Spiele"
print("OK")
