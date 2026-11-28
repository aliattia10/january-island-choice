# December getaway choice

A public, mobile-friendly page so Ella and Ali can pick a December 2026 city. Live: [https://aliattia10.github.io/january-island-choice/](https://aliattia10.github.io/january-island-choice/)

This is a GitHub Pages *project* site. Asset URLs are relative (`./styles.css`, `./photos/…`) so they resolve under `/january-island-choice/`. Pages serves `main` from `/`. No custom domain.

## The trip shape

Every destination uses the same itinerary, in **1, 2, 3 or 7 nights**. Ella’s flight home is separate, so she can stay longer in Asturias.

1. Ella: Hannover (HAJ) → the city
2. Ali: Oviedo / Asturias (OVD) → the city
3. Stay: N nights in a private room or whole place for two. Check-in on arrival day, check-out on the day you both fly to Asturias. Totals use the cheapest verified private option — never a shared room.
4. Both: the city → Asturias (OVD), two people
5. Days together in Asturias at home (no hotel). Stay as long as you like.
6. Ella flies home whenever she chooses — see **Ella’s flight home**. Not in the trip totals.

A euro trip total is Ella inbound + Ali inbound + dest→OVD (already a two-adult pair) + cheapest verified private stay. Her Asturias → Germany flight is listed separately.

There is no December nonstop from Oviedo. Lufthansa’s direct starts in March 2027. The one confirmed nonstop in this window is Eurowings Bilbao → Düsseldorf.

## What the numbers are

Prices come from [`data/prices.json`](data/prices.json). Flight fares can be refreshed with [`scripts/update_prices.py`](scripts/update_prices.py) (`fast-flights`) and by the daily GitHub Action at 06:30 UTC, which stops after 14 December 2026. That script also refreshes `ella_home` options and the Oviedo date lists. Rebuild the page with [`scripts/_rebuild.py`](scripts/_rebuild.py).

Flight snapshot is 28 November 2026. Economy, no checked bags. Inbound is one adult. The dest→OVD figure in the totals is for two adults.

Rooms were checked 28 November 2026 on Airbnb (airbnb.es, EUR stay totals for 2 adults, fees included). Listings not found in that search keep the 27 November price and are labelled recheck live. Booking.com hotel euro prices were last checked 22 November 2026 and could not be re-verified on 28 November — the page labels them **recheck live**, but they still compete with Airbnb when choosing the cheapest stay. Nicer 3–4★ rooms from the Booking check came back in USD and stay out of euro totals. 1 USD ≈ 0.911 EUR (EUR/USD ~1.0975 on 27 November) is only for those USD cards.

Google Hotels one-night lines are display only, not in the trip total.

Home flights (`ella_home`) were checked 28 November 2026 on Google Flights (`home_flights_checked`). Near Hannover only: HAJ, HAM, BRE, DUS, CGN, plus FRA as a backup.

**Cheapest complete trip** (city flights + room, no home flight): 1 night Palma €194. **Best value** per city is the cheapest full city stay (room + all three city flights).

| City | 1 night | 2 nights | 3 nights | 7 nights |
| --- | --- | --- | --- | --- |
| Palma | €194 complete (Airbnb €59) | €252 complete (Airbnb €117) | €343 complete (Airbnb €176) | €603 complete (Airbnb €410) |
| Las Palmas | €297 complete (Airbnb €48) | €435 complete (Airbnb €110) | €366 complete (Booking Isleta €155) | €729 complete (Airbnb €446) |
| Maspalomas | flights €249 + room check live | €473 complete (Airbnb €148) | €401 complete (Airbnb €190) | €806 complete (Airbnb €523) |
| Málaga | €330 complete (Airbnb €39) | €403 complete (Airbnb €112) | €429 complete (Booking NV €115) | €559 complete (Booking NV €324) |
| Barcelona | €239 complete (Airbnb €45) | €340 complete (Airbnb €90) | €388 complete (Airbnb €135) | €663 complete (Booking House €410) |

Maspalomas 1 night had no Airbnb in town within €35–85 — check live. All other 1n/2n stays now have a stored Airbnb price.

Still needs a live check:

- Maspalomas 1n 16–17 December private stay
- Booking.com hotel euro prices (22 November snapshot)
- Airbnb listings not found on 28 November (keep 27 November price)
- ALSA buses Gijón → Bilbao / Santander for Ella’s home flight (mid-December tickets not live-verified)

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
