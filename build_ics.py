#!/usr/bin/env python3
"""Build tate.ics from exhibitions.json (Tate) and additions.json (shows added on the tracker page).

Each exhibition: a timed event on every Saturday and Sunday in the second half of its run
(halfway day to closing day), using venue_hours from exhibitions.json and skipping closed_dates.
Alerts at 09:00 on the halfway day and 21 days before closing. Each Members Hours session: a timed event.
Times are written in Europe/London so BST is handled.
"""
import json, sys
from datetime import date, timedelta, datetime, timezone

def esc(t): return str(t).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
def D(s): return date.fromisoformat(s)
ADDR = {"Tate Modern": "Tate Modern, Bankside, London SE1 9TG", "Tate Britain": "Tate Britain, Millbank, London SW1P 4RG",
        "V&A East": "V&A East Museum, Queen Elizabeth Olympic Park, London E20"}
VTZ = ["BEGIN:VTIMEZONE","TZID:Europe/London",
       "BEGIN:DAYLIGHT","TZOFFSETFROM:+0000","TZOFFSETTO:+0100","TZNAME:BST","DTSTART:19700329T010000","RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU","END:DAYLIGHT",
       "BEGIN:STANDARD","TZOFFSETFROM:+0100","TZOFFSETTO:+0000","TZNAME:GMT","DTSTART:19701025T020000","RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU","END:STANDARD",
       "END:VTIMEZONE"]

def alarm(day, text):
    # 09:00 London time on `day`, expressed in UTC
    bst = date(day.year,3,31) - timedelta((date(day.year,3,31).weekday()+1)%7) <= day < date(day.year,10,31) - timedelta((date(day.year,10,31).weekday()+1)%7)
    return ["BEGIN:VALARM","ACTION:DISPLAY","DESCRIPTION:"+esc(text),
            f"TRIGGER;VALUE=DATE-TIME:{day:%Y%m%d}T{'08' if bst else '09'}0000Z","END:VALARM"]

def main():
    data = json.load(open("exhibitions.json"))
    try: adds = json.load(open("additions.json"))
    except FileNotFoundError: adds = []
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    L = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Exhibition Countdown//EN","CALSCALE:GREGORIAN",
         "X-WR-CALNAME:Exhibitions","X-WR-TIMEZONE:Europe/London","REFRESH-INTERVAL;VALUE=DURATION:PT12H","X-PUBLISHED-TTL:PT12H", *VTZ]
    titles = {}
    hours = data.get("venue_hours", {})
    closed = {D(x) for x in data.get("closed_dates", [])}
    for e in data["exhibitions"] + adds:
        a, b = D(e.get("start") or e["end"]), D(e["end"])
        titles[e["id"]] = e["title"]
        mid = a + timedelta((b - a).days // 2)
        wk3 = b - timedelta(21)
        vh = hours.get(e["venue"], {})
        days = [mid + timedelta(i) for i in range((b - mid).days + 1)]
        days = [d for d in days if d.weekday() in (5, 6) and d not in closed]
        first = days[0] if days else None
        wk3_day = next((d for d in days if d >= wk3), None)
        for d in days:
            o, c = vh.get("sat" if d.weekday() == 5 else "sun", ["10:00", "18:00"])
            alarms = []
            if d == first: alarms += alarm(mid, f"Halfway point: {e['title']} closes {b:%-d %b}")
            if d == wk3_day: alarms += alarm(wk3, f"3 weeks left: {e['title']} closes {b:%-d %b}")
            last = " Last weekend." if (b - d).days < 7 else ""
            L += ["BEGIN:VEVENT", f"UID:{e['id']}-{d:%Y%m%d}@exhibition-countdown", f"DTSTAMP:{stamp}",
                  f"DTSTART;TZID=Europe/London:{d:%Y%m%d}T{o.replace(':','')}00",
                  f"DTEND;TZID=Europe/London:{d:%Y%m%d}T{c.replace(':','')}00",
                  "SUMMARY:"+esc(f"{e['title']} ({e['venue']})"),
                  "LOCATION:"+esc(ADDR.get(e["venue"], e["venue"])),
                  "DESCRIPTION:"+esc(f"Open {o}-{c}. Closes {b:%a %-d %b %Y}.{last}" + (f"\n{e['url']}" if e.get("url") else "")),
                  *( [f"URL:{e['url']}"] if e.get("url") else [] ),
                  "TRANSP:TRANSPARENT", *alarms, "END:VEVENT"]
    for s in data.get("members_hours", []):
        d = D(s["date"]); names = " + ".join(titles.get(i, i) for i in s["exhibitions"])
        L += ["BEGIN:VEVENT", f"UID:mh-{s['venue'].split()[-1].lower()}-{d:%Y%m%d}@exhibition-countdown", f"DTSTAMP:{stamp}",
              f"DTSTART;TZID=Europe/London:{d:%Y%m%d}T{s['start'].replace(':','')}00",
              f"DTEND;TZID=Europe/London:{d:%Y%m%d}T{s['end'].replace(':','')}00",
              "SUMMARY:"+esc(f"Members Hours: {names}"),
              "LOCATION:"+esc(ADDR.get(s["venue"], s["venue"])),
              "DESCRIPTION:"+esc("Members only. No booking - bring your card."),
              "TRANSP:TRANSPARENT","END:VEVENT"]
    L.append("END:VCALENDAR")
    out = "\r\n".join(L) + "\r\n"
    open("tate.ics", "w", newline="").write(out)
    print(f"tate.ics: {len(data['exhibitions'])} Tate + {len(adds)} added exhibitions, {len(data.get('members_hours', []))} Members Hours sessions")

if __name__ == "__main__":
    main()
