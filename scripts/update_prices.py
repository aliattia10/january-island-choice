#!/usr/bin/env python3
"""Refresh EUR flight fares in data/prices.json via fast-flights (Google Flights).

Hotels are left as-is. A fetch that errors or looks insane keeps the stored value.
Stops doing work after 2026-12-14 (UTC).
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRICES_PATH = ROOT / "data" / "prices.json"
STOP_AFTER = date(2026, 12, 14)
SLEEP_S = 3.0
RETRY_SLEEP_S = 6.0
MIN_EUR = 8
MAX_EUR = 2500
CHANGE_FACTOR = 3.0


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def parse_price(raw) -> int | None:
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        if raw <= 0:
            return None
        return int(round(raw))
    if isinstance(raw, str):
        digits = "".join(ch for ch in raw if ch.isdigit())
        if not digits:
            return None
        return int(digits)
    return None


def segment_count(flight) -> int | None:
    segs = getattr(flight, "flights", None)
    if segs is None:
        return None
    try:
        return len(segs)
    except TypeError:
        return None


def fetch_one_adult(origin: str, dest: str, day: str):
    from fast_flights import FlightQuery, Passengers, create_query, get_flights

    query = create_query(
        flights=[FlightQuery(date=day, from_airport=origin, to_airport=dest)],
        seat="economy",
        trip="one-way",
        passengers=Passengers(adults=1),
        language="en-GB",
        currency="EUR",
    )
    return get_flights(query)


def pick_cheapest(result, want_nonstop: bool):
    flights = list(result or [])
    if not flights:
        return None, None, "no results"

    priced = []
    for item in flights:
        price = parse_price(getattr(item, "price", None))
        if price is None:
            continue
        priced.append((price, item, segment_count(item)))
    if not priced:
        return None, None, "no numeric prices"

    if want_nonstop:
        nonstop = [row for row in priced if row[2] == 1]
        if not nonstop:
            cheapest = min(priced, key=lambda row: row[0])
            return None, None, f"no 1-segment result (cheapest connecting €{cheapest[0]})"
        price, item, segs = min(nonstop, key=lambda row: row[0])
        return price, segs, item

    price, item, segs = min(priced, key=lambda row: row[0])
    return price, segs, item


def sane(new: int, old: int | None, segs: int | None) -> str | None:
    if new < MIN_EUR or new > MAX_EUR:
        return f"out of range €{new}"
    if old and old > 0:
        if new >= old * CHANGE_FACTOR or new * CHANGE_FACTOR <= old:
            return f"€{new} vs stored €{old} exceeds {CHANGE_FACTOR:g}x"
        # fast-flights often omits the cheap fare and returns a connecting itinerary.
        if segs is not None and segs >= 2 and new >= old * 2:
            return f"connecting €{new} vs stored €{old} looks like a missing cheap fare"
    return None


def recompute(data: dict) -> None:
    flights = {item["id"]: item for item in data["flights"]}
    hotels = {item["id"]: item for item in data["hotels"]}

    def eur_sum(ids: list[str]) -> int:
        total = 0
        for fid in ids:
            fare = flights[fid]
            if fare.get("currency") == "USD":
                raise ValueError(f"{fid} is USD and cannot enter an EUR total")
            total += int(fare["price_eur"])
        return total

    for plan in data["plans"]:
        flight_total = eur_sum(plan["flights"])
        hotel = hotels[plan["hotel"]]
        plan["total_eur"] = flight_total + int(hotel["price"])
        alt_id = plan.get("alt_hotel")
        if alt_id:
            alt = hotels[alt_id]
            plan["alt_total_eur"] = flight_total + int(alt["price"])

    for bundle in data.get("bundles") or []:
        bundle["total_eur"] = eur_sum(bundle["flights"])


def dump(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    if utc_today() > STOP_AFTER:
        print(f"Past {STOP_AFTER.isoformat()}; skipping.")
        return 0

    try:
        from fast_flights import FlightsNotFound
    except ImportError as err:
        print(f"fast-flights is not installed: {err}", file=sys.stderr)
        return 1

    original = PRICES_PATH.read_text(encoding="utf-8")
    data = json.loads(original)

    any_success = False
    changed = []
    skipped = []

    fetchable = [leg for leg in data["flights"] if leg.get("fetch")]
    for index, leg in enumerate(fetchable):
        if index:
            time.sleep(SLEEP_S)

        adults = int(leg.get("adults") or 1)
        want_nonstop = bool(leg.get("nonstop"))
        old = leg.get("price_eur")
        label = f"{leg['id']} {leg['origin']}→{leg['destination']} {leg['date']}"

        new_one = None
        segs = None
        reason = None
        for attempt in range(2):
            try:
                result = fetch_one_adult(leg["origin"], leg["destination"], leg["date"])
                new_one, segs, detail = pick_cheapest(result, want_nonstop)
                if new_one is None:
                    reason = detail
                    break
                reason = None
                break
            except FlightsNotFound:
                reason = "FlightsNotFound"
            except Exception as err:  # noqa: BLE001 — scraper network/parse noise
                reason = f"{type(err).__name__}: {err}"
            if attempt == 0:
                time.sleep(RETRY_SLEEP_S)

        if new_one is None:
            skipped.append(f"{label}: {reason}")
            print(f"SKIP {label}: {reason}")
            continue

        new = new_one * adults
        problem = sane(new, old if isinstance(old, int) else None, segs)
        if problem:
            skipped.append(f"{label}: {problem}")
            print(f"SKIP {label}: {problem}")
            continue

        any_success = True
        if old != new:
            leg["price_eur"] = new
            changed.append(f"{label}: €{old} → €{new}")
            print(f"UPDATE {label}: €{old} → €{new}")
        else:
            print(f"OK {label}: still €{new}")

    if any_success:
        data["snapshot"] = utc_today().isoformat()
        recompute(data)

    next_text = dump(data)
    if next_text == original:
        print("No changes to write.")
        if skipped:
            print("Skipped legs:")
            print("\n".join(skipped))
        return 0

    PRICES_PATH.write_text(next_text, encoding="utf-8")
    print(f"Wrote {PRICES_PATH.relative_to(ROOT)}")
    if changed:
        print("Changed fares:")
        print("\n".join(changed))
    if skipped:
        print("Skipped legs:")
        print("\n".join(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
