# January island choice

A public, mobile-friendly page so Ali’s girlfriend can tap through three January 2027 bases and pick an island:

- Palma (Mallorca)
- Maspalomas (Gran Canaria south)
- Las Palmas (Gran Canaria city)

Trip lengths are 2, 3 or 7 nights. There are no bookings and no forms that collect data.

**Live site (once Pages is on):** [https://aliattia10.github.io/january-island-choice/](https://aliattia10.github.io/january-island-choice/)

This is a GitHub Pages *project* site. Asset URLs are relative (`./styles.css`, `./photos/…`) so they resolve under `/january-island-choice/`.

The site files are on `main` at the repo root. Enable Pages in the GitHub UI: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / root.** First publish can take a few minutes. Do not add a custom domain.

## What the numbers are

Flight prices are a Google Flights snapshot from Sunday 8 November 2026, Madrid time: economy, taxes included, bags extra. Inbound is one adult. Island to Asturias is the total for two adults.

Hotel figures are earlier quotes, not rechecked on 8 November 2026. Las Palmas is complete only for 2 nights.

A trip total is inbound pair + hotel + island to Asturias. Food, local buses, airport transfers, attraction tickets, bags, insurance, connection-night hotels and her later Frankfurt ticket are not included.

Self-transfers are separate tickets. A delay can mean buying a new onward flight.

## Local preview

Open `index.html` in a browser, or from this folder:

```bash
python3 -m http.server 8080
```

Then visit `http://localhost:8080/`.

## Photographs

Real Wikimedia Commons files, downloaded and committed in `photos/`. Credits are on the page footer and in [`photos/CREDITS.md`](photos/CREDITS.md). They are reference photographs from various seasons, not a promise of January weather.

## Licence

Site code is MIT (see `LICENSE`). Photographs remain under their Wikimedia licences (CC BY, CC BY-SA, or CC0).
