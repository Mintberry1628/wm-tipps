# -*- coding: utf-8 -*-
"""Erzeugt wm2026-erinnerungen.ics aus data.js.
Pro Spiel ein Kalendereintrag mit Alarm 1 Std. vor Anpfiff
('App oeffnen und Tipp pruefen'). Einmal in den Kalender importieren."""
import json, io, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
with io.open(os.path.join(HERE, "data.js"), "r", encoding="utf-8") as f:
    txt = f.read().strip()
txt = txt[txt.index("{"):txt.rindex("}") + 1]
data = json.loads(txt)

def z(d):  # ISO+02:00 -> UTC ical-Stempel
    dt = datetime.datetime.fromisoformat(d).astimezone(datetime.timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")

def esc(s):
    return str(s).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//WM2026 KI-Tipps//DE",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:WM 2026 KI-Tipps"]
n = 0
for m in data["matches"]:
    ko = m.get("kickoffBerlin")
    if not ko:
        continue
    hn = m.get("home") or m.get("homePlaceholder") or "?"
    an = m.get("away") or m.get("awayPlaceholder") or "?"
    pr = m.get("prediction")
    start = datetime.datetime.fromisoformat(ko)
    end = start + datetime.timedelta(hours=2)
    summ = "WM: %s - %s" % (hn, an)
    if pr:
        summ += " (Tipp %d:%d)" % (pr["scoreHome"], pr["scoreAway"])
    desc = "%s\\nAnpfiff %02d:%02d Uhr." % (m.get("group", ""), start.hour, start.minute)
    if pr:
        desc += "\\nKI-Tipp %d:%d. " % (pr["scoreHome"], pr["scoreAway"]) + esc("; ".join(pr.get("reasons", [])))
    desc += "\\n\\nApp oeffnen und pruefen, ob der Tipp aktualisiert wurde!"
    lines += ["BEGIN:VEVENT", "UID:wm2026-%s@kitipps" % m["matchNo"],
              "DTSTAMP:%s" % z(data["meta"]["generatedAt"]),
              "DTSTART:%s" % z(ko), "DTEND:%s" % z(end.isoformat()),
              "SUMMARY:%s" % esc(summ), "DESCRIPTION:%s" % desc,
              "LOCATION:%s" % esc((m.get("venue") or "") + (", " + m["city"] if m.get("city") else "")),
              "BEGIN:VALARM", "TRIGGER:-PT60M", "ACTION:DISPLAY",
              "DESCRIPTION:%s" % esc("Tipp pruefen: %s - %s" % (hn, an)), "END:VALARM",
              "END:VEVENT"]
    n += 1
lines.append("END:VCALENDAR")

with io.open(os.path.join(HERE, "wm2026-erinnerungen.ics"), "w", encoding="utf-8", newline="\r\n") as f:
    f.write("\r\n".join(lines) + "\r\n")
print("ICS geschrieben:", n, "Termine -> wm2026-erinnerungen.ics")
