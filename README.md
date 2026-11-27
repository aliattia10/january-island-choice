# December getaway choice

A public, mobile-friendly page so Ella and Ali can pick a December 2026 city. Live: [https://aliattia10.github.io/january-island-choice/](https://aliattia10.github.io/january-island-choice/)

This is a GitHub Pages *project* site. Asset URLs are relative (`./styles.css`, `./photos/…`) so they resolve under `/january-island-choice/`. Pages serves `main` from `/`. No custom domain.

## The trip shape

Every destination uses the same itinerary, in **1, 2, 3 or 7 nights**. There is no flight back to Hannover.

1. Ella: Hannover (HAJ) → the city
2. Ali: Oviedo / Asturias (OVD) → the city
3. Stay: N nights in a private room or whole place for two. Check-in on arrival day, check-out on the day you both fly to Asturias. Totals use the cheapest verified private option — never a shared room.
4. Both: the city → Asturias (OVD), two people
5. Two days together in Asturias at home (no hotel)
6. Ella: Asturias (OVD) → Frankfurt (FRA), one way, after those days, to go home to Germany

If OVD→FRA has no verified fare, the page says **check live price** and the total is the city stay **plus her flight to Frankfurt**. There is no December nonstop; Lufthansa’s direct starts in March 2027. Priced options are one-stop. Santander and Bilbao are dated Google Flights links only — no stored prices.

A euro trip total is Ella inbound + Ali inbound + dest→OVD (already a two-adult pair) + cheapest verified private stay + Ella OVD→FRA when known.

## What the numbers are

Prices come from [`data/prices.json`](data/prices.json). Flight fares can be refreshed with [`scripts/update_prices.py`](scripts/update_prices.py) (`fast-flights`) and by the daily GitHub Action at 06:30 UTC, which stops after 14 December 2026. Rebuild the page with [`scripts/_rebuild.py`](scripts/_rebuild.py).

Flight snapshot is 27 November 2026. Economy, no checked bags. Inbound is one adult. The dest→OVD figure in the totals is for two adults.

Rooms were checked 27 November 2026 on Airbnb (airbnb.es, EUR stay totals for 2 adults, fees included). Booking.com hotel euro prices were last checked 22 November 2026 and could not be re-verified on 27 November — the page labels them **recheck live**, but they still compete with Airbnb when choosing the cheapest stay. Nicer 3–4★ rooms from the Booking check came back in USD and stay out of euro totals. 1 USD ≈ 0.911 EUR (EUR/USD ~1.0975 on 27 November) is only for those USD cards.

Google Hotels one-night lines are display only, not in the trip total.

OVD→FRA rechecked 27 November 2026: 17 Dec €91, 18 Dec €116, 19 Dec €116, 20 Dec €116, 22 Dec €116 (Air Europa, 1 stop). 21, 23, 24 and 27 December: check live.

**Cheapest complete trip** (Frankfurt included): 1 night Palma €346. **Best value** per city is the cheapest full city stay (room + all three city flights).

| City | 1 night | 2 nights | 3 nights | 7 nights |
| --- | --- | --- | --- | --- |
| Palma | €346 complete (Airbnb €63) | €433 complete (Airbnb €125) | €457 complete (Airbnb €187) | €615 before Frankfurt (Airbnb €435) |
| Las Palmas | €512 complete (Airbnb €48) | €680 complete (Airbnb €110) | €370 before Frankfurt (Booking Isleta €155) | €686 before Frankfurt (Airbnb €446) |
| Maspalomas | flights €348 + room check live | €718 complete (Airbnb €148) | €405 before Frankfurt (Airbnb €190) | €763 before Frankfurt (Airbnb €523) |
| Málaga | €336 before Frankfurt (Airbnb €39; FRA 21 Dec check live) | €508 complete (Airbnb €116) | €531 complete (Booking NV €115) | €544 before Frankfurt (Booking NV €324) |
| Barcelona | €430 complete (Airbnb €45) | €691 complete (Airbnb €90) | €490 complete (Airbnb €135) | €670 before Frankfurt (Booking House €410) |

Maspalomas 1 night had no Airbnb in town within €35–85 — check live. All other 1n/2n stays now have a stored Airbnb price.

Still needs a live check:

- Maspalomas 1n 16–17 December private stay
- Booking.com hotel euro prices (22 November snapshot)
- Ella **OVD→FRA on 21, 23, 24 and 27 December**

All 1n/2n **returns to Asturias are verified**. Do not fetch those again unless they look stale.

Málaga 18–21 December is not a headline plan: Ella’s return to Asturias on 21 December was not priced.

Prices jump after 22 December, so arriving 14–18 December is best. Food, local buses, airport transfers, attraction tickets, bags and insurance are not included. Self-transfers are separate tickets.

## Local preview

```bash
python3 -m http.server 8080
```

Then visit `http://localhost:8080/`.

## Photographs

Real Wikimedia Commons files in `photos/`. Booking hotel cards use a city photograph labelled as the city, not a hotel façade. Airbnb cards use the listing photo when we have one, otherwise a city photograph. Credits: [`photos/CREDITS.md`](photos/CREDITS.md).

## Licence

Site code is MIT (see `LICENSE`). Photographs remain under their Wikimedia licences.
