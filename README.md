# Two Rivers Logboek

Persoonlijke trainings-app richting de **Two Rivers Marathon, zondag 21 maart 2027, Zaltbommel**.

Eén statische pagina (`index.html`), werkt op telefoon en desktop en is als app op je beginscherm te zetten (PWA). Geen server nodig: een GitHub Action haalt elke 3 uur je Strava-data en het nieuws op en publiceert via GitHub Pages.

| Tab | Wat je ziet |
|---|---|
| **Vandaag** | Aftellen, training van vandaag en morgen, weekvolume vs. plan, de belangrijkste aandachtspunten |
| **Schema** | Weekschema met tempo’s afgeleid van je doeltijd, gepland vs. gedaan, import van je ProRun-trainingen |
| **Voortgang** | Km per week (gelopen vs. gepland), langste duurloop, schaatsen en andere sporten, totalen per sport |
| **Analyse** | Fitheid/vermoeidheid/vorm (CTL/ATL/TSB), acuut:chronisch, marathonvoorspelling (Riegel + Tanda), adviezen |
| **Gezondheid** | Rusthartslag, HRV, slaap, gewicht, gevoel: handmatig of automatisch via intervals.icu |
| **Nieuws** | Two Rivers-nieuws (feed van de officiële site, anders Google News) |

## Lokaal bekijken

```bash
python3 -m http.server 8000   # open http://localhost:8000
```

## Inrichten (eenmalig, ~15 min)

1. **Strava API-app**: maak er een op <https://www.strava.com/settings/api> (callback-domein `localhost`).
2. **Refresh token met leesrechten op activiteiten**: open in je browser
   `https://www.strava.com/oauth/authorize?client_id=JOUW_ID&response_type=code&redirect_uri=http://localhost&scope=activity:read_all&approval_prompt=force`,
   kopieer de `code` uit de URL waar je op uitkomt en wissel hem in:
   ```bash
   curl -X POST https://www.strava.com/oauth/token -d client_id=JOUW_ID -d client_secret=JOUW_SECRET -d code=DE_CODE -d grant_type=authorization_code
   ```
   Bewaar de `refresh_token` uit het antwoord.
3. **GitHub Secrets** (Settings → Secrets and variables → Actions): `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, `STRAVA_REFRESH_TOKEN`.
4. **GitHub Pages**: Settings → Pages → Source: *GitHub Actions*. Merge naar `main` of start de workflow *Sync data & deploy* handmatig.
5. **Optioneel, gezondheid**: maak een gratis account op [intervals.icu](https://intervals.icu), koppel Garmin/Apple Health/Oura, en zet `INTERVALS_ATHLETE_ID` en `INTERVALS_API_KEY` als secrets.

## Bekende beperkingen

- **ProRun heeft geen publieke API of agenda-export.** Het schema in `data/plan.json` is een *voorbeeldschema* op basis van je Strava-patroon. Zet je ProRun-trainingen in de app via *Schema → ProRun-schema importeren* (`datum;type;titel;km;omschrijving`), of vervang `data/plan.json`.
- **Strava levert geen HRV, slaap of rusthartslag.** Die komen alleen binnen via handmatige invoer of intervals.icu.
- **Privacy**: GitHub Pages is openbaar, ook bij een privé-repo. Je activiteiten (`data/activities.json`) staan dan publiek online. Handmatige gezondheidsdata blijft in je browser (localStorage). Wil je dat niet, draai de app lokaal of host hem achter een login (bijv. Cloudflare Pages + Access).
- Belasting = Strava *Relative Effort*. Activiteiten zonder hartslag krijgen een schatting op basis van duur en sport.

## Bestanden

```
index.html                 de app
data/activities.json       Strava-activiteiten (door sync bijgewerkt)
data/plan.json             trainingsschema
data/news.json             nieuws
data/wellness.json         gezondheid uit intervals.icu
scripts/sync_strava.py     Strava API → activities.json
scripts/fetch_news.py      feed / Google News → news.json
scripts/sync_wellness.py   intervals.icu → wellness.json
.github/workflows/sync.yml elke 3 uur syncen + deploy naar Pages
```
