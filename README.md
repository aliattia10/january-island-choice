# December getaway choice

A public, mobile-friendly page so Ella and Ali can pick a December 2026 city. Live: [https://aliattia10.github.io/january-island-choice/](https://aliattia10.github.io/january-island-choice/)

This is a GitHub Pages *project* site. Asset URLs are relative (`./styles.css`, `./photos/…`) so they resolve under `/january-island-choice/`. Pages serves `main` from `/`. No custom domain.

## The trip shape

Every destination uses the same itinerary, in **1, 2, 3 or 7 nights**. There is no flight back to Hannover.

1. Ella: Hannover (HAJ) → the city
2. Ali: Oviedo / Asturias (OVD) → the city
3. Hotel: N nights in a private double for two. Check-in on arrival day, check-out on the day you both fly to Asturias. Totals use the cheapest private room we priced — never a shared dorm.
4. Both: the city → Asturias (OVD), two people
5. Two days together in Asturias at home (no hotel)
6. Ella: Asturias (OVD) → Frankfurt (FRA), one way, after those days, to go home to Germany

If OVD→FRA has no verified fare, the page says **check live price** and the total is the city stay **plus her flight to Frankfurt**. There is no December nonstop; Lufthansa’s direct starts in March 2027. Priced options are one-stop. Santander and Bilbao are dated Google Flights links only — no stored prices.

A euro trip total is Ella inbound + Ali inbound + dest→OVD (already a two-adult pair) + hotel + Ella OVD→FRA when known.

## What the numbers are

Prices come from [`data/prices.json`](data/prices.json). Flight fares can be refreshed with [`scripts/update_prices.py`](scripts/update_prices.py) (`fast-flights`) and by the daily GitHub Action at 06:30 UTC, which stops after 14 December 2026. Hotels stay as last checked.

Flight snapshot is 24 November 2026. Economy, no checked bags. Inbound is one adult. The dest→OVD figure in the totals is for two adults. Hotel euro figures were last checked 22 November 2026 (Booking.com, before about 10% tax). Nicer 3–4★ rooms from that check came back in USD and are labelled USD, with 1 USD ≈ 0.86 EUR as an approximate conversion only.

OVD→FRA verified 23 November 2026 (unchanged in the 24 November flight refresh): 17 Dec €123, 18 Dec €141, 19 Dec €141, 20 Dec €91, 22 Dec €169 (Air Europa, 1 stop). 21, 23, 24 and 27 December: check live (fetch returned no results).

Headline cheapest complete trip (Frankfurt included): 3 nights Barcelona €483. Best value per city is the cheapest full city stay (3n or 7n until 1n/2n rooms are priced).

1-night and 2-night plans reuse the cheapest known inbounds. Together (city→OVD) fares that were not in the 24 November list stay as last fetched. Private-room prices for 1n/2n are **check live** — not stored, not invented — so those columns are flights only plus the room search.

| City | 1 night | 2 nights | 3 nights | 7 nights |
| --- | --- | --- | --- | --- |
| Palma | 14–15 Dec, flights €216 + room check live (FRA €123) | 14–16 Dec, flights €216 + room check live (FRA €141) | €377 (14–17 Dec) + FRA €141 → €518 | €668 (14–21 Dec) + FRA check live |
| Las Palmas | 16–17 Dec, flights €358 + room check live (FRA €141) | 16–18 Dec, flights €464 + room check live (FRA €91) | €369 (16–19 Dec) + FRA check live | €778 (15–22 Dec) + FRA check live |
| Maspalomas | same LPA flights as Las Palmas 1n | same LPA flights as Las Palmas 2n | €444 (16–19 Dec) + FRA check live | €846 (15–22 Dec) + FRA check live |
| Málaga | 18–19 Dec, flights €312 + room check live + FRA 21 Dec check live | 18–20 Dec, flights €312 + room check live (FRA €169) | €415 (15–18 Dec) + FRA €91 → €506 | €559 (18–25 Dec) + FRA check live |
| Barcelona | 15–16 Dec, flights €275 + room check live (FRA €141) | 15–17 Dec, flights €491 + room check live (FRA €141) | €392 (15–18 Dec) + FRA €91 → €483 | €676 (15–22 Dec, Hostal House) + FRA check live |

Still needs a live check (so we can fill the 1n/2n columns without inventing a figure):

- Every 1n/2n **private double room** (10 Booking searches; no named hotel stored)
- Ella **OVD→FRA on 21 December** (Málaga 1-night, after two days in Asturias)

All 1n/2n **returns to Asturias are verified**. Do not fetch those again unless they look stale.

Málaga 18–21 December is not a headline plan: Ella’s return to Asturias on 21 December was not priced.

Prices jump after 22 December, so arriving 14–18 December is best. Food, local buses, airport transfers, attraction tickets, bags and insurance are not included. Self-transfers are separate tickets.

## Local preview

```bash
python3 -m http.server 8080
```

Then visit `http://localhost:8080/`.

## Photographs

Real Wikimedia Commons files in `photos/`. Hotel cards use a city photograph labelled as the city, not a hotel façade. Credits: [`photos/CREDITS.md`](photos/CREDITS.md).

## Licence

Site code is MIT (see `LICENSE`). Photographs remain under their Wikimedia licences.
