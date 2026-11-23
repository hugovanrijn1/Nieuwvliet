#!/usr/bin/env python3
"""Optioneel: haalt gezondheidsdata (rusthartslag, HRV, slaap, gewicht) op uit intervals.icu.

intervals.icu synchroniseert dit gratis vanuit Garmin, Apple Health (via app), Oura, Whoop enz.
Strava zelf levert GEEN HRV/slaap/rusthartslag.
Secrets: INTERVALS_ATHLETE_ID (bv. i12345) en INTERVALS_API_KEY (Instellingen > Developer).
"""
import base64, datetime as dt, json, os, sys, urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "wellness.json"


def main():
    aid, key = os.environ.get("INTERVALS_ATHLETE_ID"), os.environ.get("INTERVALS_API_KEY")
    if not (aid and key):
        print("intervals.icu-secrets ontbreken; wellness-sync overgeslagen.")
        return 0
    newest = dt.date.today()
    oldest = newest - dt.timedelta(days=120)
    url = f"https://intervals.icu/api/v1/athlete/{aid}/wellness?oldest={oldest}&newest={newest}"
    auth = base64.b64encode(f"API_KEY:{key}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = json.load(r)
    entries = [{
        "date": w["id"],
        "rhr": w.get("restingHR"),
        "hrv": w.get("hrv"),
        "sleep_h": round(w["sleepSecs"] / 3600, 1) if w.get("sleepSecs") else None,
        "weight": w.get("weight"),
        "readiness": w.get("readiness"),
        "soreness": w.get("soreness"),
        "fatigue": w.get("fatigue"),
    } for w in rows]
    DATA.write_text(json.dumps({"source": "intervals.icu", "updated": dt.datetime.now().isoformat(timespec="seconds"),
                                "entries": entries}, indent=1))
    print(f"{len(entries)} wellness-dagen opgehaald")
    return 0


if __name__ == "__main__":
    sys.exit(main())
