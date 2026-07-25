# Who Represents Me — MVP

A civic-info tool: enter an address, see who represents you at every
level of government and what that office actually controls.

## How to read this project (in order)

If you're reviewing this for the first time, read the files in this order —
it follows the actual request flow, address in → answer out.

```
civic-app/
│
├── run.py                     ← START HERE. Boots the Flask app.
│
├── app/
│   ├── __init__.py            ← App factory. Wires routes together.
│   ├── config.py               ← All settings/API keys live here, nowhere else.
│   │
│   ├── routes/                 ← "What URL does what" — the traffic cops.
│   │   ├── lookup.py            → /api/lookup and /api/office-explainer
│   │   │                          This is the main logic: calls the services
│   │   │                          below, merges their results, returns JSON.
│   │   └── pages.py             → / (serves the HTML page)
│   │
│   ├── services/                ← "How do we actually get the data" — one
│   │   │                          file per external data source, so each
│   │   │                          API integration is isolated and swappable.
│   │   ├── geocode.py            → Census Bureau: address → lat/lon + district
│   │   └── openstates.py         → OpenStates: lat/lon → state legislators
│   │
│   └── templates/
│       └── index.html           ← The one page: address box + results.
│
├── data/                        ← Hand-maintained data (not from an API).
│   ├── office_explainers.json    "What does a county commissioner control?"
│   ├── oregon_federal.json       OR's 2 senators + 6 House reps (small
│   │                             enough to hardcode, update after elections)
│   └── columbia_county_or.json   Pilot county's local officials — the part
│                                 with no API, so it's manually researched.
│                                 REPLACE_ME fields = your homework.
│
└── requirements.txt             ← pip install -r requirements.txt
```

## The three kinds of data, and why they're handled differently

1. **Live API data** (`services/`) — state legislators, geocoding. Always
   current, but depends on external services staying up.
2. **Small static data** (`data/oregon_federal.json`) — only 8 people for
   the whole state, not worth an API integration. Update manually each
   election.
3. **Manual local data** (`data/columbia_county_or.json`) — no API exists
   for city council / county commission data, so this is a hand-built
   lookup table. This is the part that takes real research time and is
   the main thing to fill in before launch.

## Running it

```bash
pip install -r requirements.txt
export OPENSTATES_API_KEY=your_key_here   # free at open.pluralpolicy.com
python run.py
```

Then open `http://localhost:5000`.

## Before this is real

- [ ] Fill in `REPLACE_ME` fields in `data/oregon_federal.json` (verify against house.gov)
- [ ] Fill in `REPLACE_ME` fields in `data/columbia_county_or.json` (verify against columbiacountyor.gov, city sites)
- [ ] Get an OpenStates API key and confirm the live response shape matches what `services/openstates.py` expects (untested against the real API in this sandbox — no outbound network access to openstates.org here)
