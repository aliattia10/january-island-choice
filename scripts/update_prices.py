#!/usr/bin/env python3
"""Refresh EUR flight fares in data/prices.json via fast-flights (Google Flights).

Hotels are left as-is. A fetch that errors or looks insane keeps the stored value.
Stops doing work after 2026-12-14 (UTC).

Plan totals are:
  Ella inbound + Ali inbound + dest→OVD (already a 2-adult pair) + hotel.
Ella’s flight home is stored under ella_home and is not added to trip totals.
A missing dest→OVD or hotel is excluded from subtotal_eur and noted.
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


def fare_eur(fare: dict) -> int | None:
    if fare.get("currency") == "USD":
        return None
    if fare.get("price_status") == "check_live":
        return None
    price = fare.get("price_eur")
    if price is None:
        return None
    return int(price)


def recompute(data: dict) -> None:
    flights = {item["id"]: item for item in data["flights"]}
    hotels = {item["id"]: item for item in data["hotels"]}

    for plan in data["plans"]:
        ella = fare_eur(flights.get(plan.get("ella_in") or "", {}))
        ali = fare_eur(flights.get(plan.get("ali_in") or "", {}))
        tog = fare_eur(flights.get(plan.get("together") or "", {}))
        hotel = hotels[plan["hotel"]]
        room = None
        if hotel.get("currency") != "USD" and hotel.get("price") is not None and hotel.get("price_status") != "check_live":
            room = int(hotel["price"])
        plan["together_missing"] = tog is None
        plan["hotel_missing"] = room is None
        plan["fra_known"] = False
        plan["inbound_eur"] = None if ella is None or ali is None else ella + ali
        pieces: list[int] = []
        if ella is not None:
            pieces.append(ella)
        if ali is not None:
            pieces.append(ali)
        if tog is not None:
            pieces.append(tog)
        if room is not None:
            pieces.append(room)
        plan["partial_eur"] = sum(pieces) if ella is not None and ali is not None else None
        if ella is None or ali is None or tog is None or room is None:
            plan["subtotal_eur"] = None
            plan["total_eur"] = None
            plan["total_complete"] = False
            continue
        subtotal = ella + ali + tog + room
        plan["subtotal_eur"] = subtotal
        plan["total_eur"] = subtotal
        plan["total_complete"] = True
        alt_id = plan.get("alt_hotel")
        if alt_id:
            alt = hotels[alt_id]
            if (
                alt.get("currency") != "USD"
                and alt.get("price") is not None
                and alt.get("price_status") != "check_live"
            ):
                plan["alt_subtotal_eur"] = ella + ali + tog + int(alt["price"])
                plan["alt_total_eur"] = plan["alt_subtotal_eur"]

    for bundle in data.get("bundles") or []:
        total = 0
        ok = True
        for fid in bundle["flights"]:
            value = fare_eur(flights[fid])
            if value is None:
                ok = False
                break
            total += value
        if ok:
            bundle["total_eur"] = total


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

    home = data.get("ella_home") or {}
    home_legs: list[dict] = list(home.get("options") or [])
    for rows in (home.get("calendar") or {}).values():
        home_legs.extend(rows)
    fetchable = [leg for leg in data["flights"] if leg.get("fetch")]
    fetchable += [leg for leg in home_legs if leg.get("fetch")]
    home_ids = {leg["id"] for leg in home_legs}
    home_updated = False
    for index, leg in enumerate(fetchable):
        if index:
            time.sleep(SLEEP_S)

        adults = int(leg.get("adults") or 1)
        want_nonstop = bool(leg.get("nonstop"))
        old = leg.get("price_eur")
        old_int = old if isinstance(old, int) else None
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
        problem = sane(new, old_int, segs)
        if problem:
            skipped.append(f"{label}: {problem}")
            print(f"SKIP {label}: {problem}")
            continue

        any_success = True
        if old != new or leg.get("price_status") == "check_live":
            leg["price_eur"] = new
            leg["price_status"] = "known"
            changed.append(f"{label}: {old} → €{new}")
            print(f"UPDATE {label}: {old} → €{new}")
            if leg.get("id") in home_ids:
                home_updated = True
        else:
            print(f"OK {label}: still €{new}")

    if any_success:
        data["snapshot"] = utc_today().isoformat()
        if home_updated:
            data["home_flights_checked"] = utc_today().isoformat()
            if "ella_home" in data:
                data["ella_home"]["checked"] = data["home_flights_checked"]
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
