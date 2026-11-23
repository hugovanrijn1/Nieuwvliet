#!/usr/bin/env python3
"""Haalt activiteiten op uit de Strava API en voegt ze samen in data/activities.json.

Benodigde omgevingsvariabelen (GitHub Secrets):
  STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
Optioneel: SYNC_DAYS (standaard 60) - hoeveel dagen terug opnieuw ophalen.
Alleen standaardbibliotheek, geen pip install nodig.
"""
import json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "activities.json"


def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    cid, secret, refresh = (os.environ.get(k) for k in ("STRAVA_CLIENT_ID", "STRAVA_CLIENT_SECRET", "STRAVA_REFRESH_TOKEN"))
    if not all((cid, secret, refresh)):
        print("Strava-secrets ontbreken; sync overgeslagen.")
        return 0
    tok = post("https://www.strava.com/oauth/token", {
        "client_id": cid, "client_secret": secret, "grant_type": "refresh_token", "refresh_token": refresh})
    if tok.get("refresh_token") and tok["refresh_token"] != refresh:
        print("::warning::Strava gaf een nieuwe refresh token terug; werk het secret STRAVA_REFRESH_TOKEN bij.")
    access = tok["access_token"]

    days = int(os.environ.get("SYNC_DAYS", "60"))
    after = int(time.time()) - days * 86400
    fetched, page = [], 1
    while True:
        url = f"https://www.strava.com/api/v3/athlete/activities?after={after}&per_page=100&page={page}"
        batch = get(url, access)
        fetched += batch
        if len(batch) < 100:
            break
        page += 1

    existing = json.loads(DATA.read_text()) if DATA.exists() else {"activities": []}
    by_id = {a["id"]: a for a in existing.get("activities", [])}
    for a in fetched:
        by_id[str(a["id"])] = {
            "id": str(a["id"]),
            "date": a["start_date_local"].rstrip("Z"),
            "sport": a.get("sport_type") or a.get("type"),
            "name": (a.get("name") or "")[:80],
            "km": round((a.get("distance") or 0) / 1000, 2),
            "moving_s": a.get("moving_time"),
            "elev": a.get("total_elevation_gain"),
            "re": a.get("suffer_score"),
            "hr": a.get("average_heartrate"),
        }
    out = {"source": "strava", "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "activities": sorted(by_id.values(), key=lambda x: x["date"])}
    DATA.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{len(fetched)} activiteiten opgehaald, totaal {len(by_id)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
