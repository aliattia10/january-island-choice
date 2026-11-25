#!/usr/bin/env python3
"""One-shot rebuild of prices.json + index.html for the six-step itinerary."""

from __future__ import annotations

import base64
import json
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
HEADER = b"\x08\x1c\x10\x02"
PASS_1 = b"@\x01H\x01p\x01\x82\x01\x0b\x08\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x98\x01\x02"
PASS_2 = b"@\x01@\x01H\x01p\x01\x82\x01\x0b\x08\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x98\x01\x02"


def tfs(date: str, origin: str, dest: str, adults: int = 1) -> str:
    raw = (
        HEADER
        + b"\x1a\x1e\x12\n"
        + date.encode()
        + b"j\x07\x08\x01\x12\x03"
        + origin.encode()
        + b"r\x07\x08\x01\x12\x03"
        + dest.encode()
        + (PASS_2 if adults == 2 else PASS_1)
    )
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def gf(date: str, origin: str, dest: str, adults: int = 1) -> str:
    return (
        "https://www.google.com/travel/flights/search?tfs="
        + tfs(date, origin, dest, adults)
        + "&curr=EUR&hl=en"
    )


# Private rooms for two: never a dorm. privacy_type=2 + private bathroom,
# plus hostel / guest house / B&B property types so the search leans budget.
PRIVATE_NFLT = (
    "privacy_type%3D2%3Broomfacility%3D38"
    "%3Bht_id%3D203%3Bht_id%3D208%3Bht_id%3D216"
)


def booking(ss: str, checkin: str, checkout: str, kind: str = "named") -> str:
    extra = ""
    if kind == "private":
        extra = "&nflt=" + PRIVATE_NFLT
    return (
        "https://www.booking.com/searchresults.html?ss="
        + quote(ss)
        + f"&checkin={checkin}&checkout={checkout}"
        "&group_adults=2&no_rooms=1&selected_currency=EUR&order=price"
        + extra
    )


def pretty(iso: str) -> str:
    y, m, d = iso.split("-")
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    return f"{int(d)} {months[int(m) - 1]}"


def euro(n) -> str:
    return f"€{int(n)}"


OFFICIAL = {
    "arc-rambla": "https://hotelarclarambla.com/",
    "arcelon": "https://arcelonhotel.com/en/",
    "pestana-arena": "https://www.pestana.com/en/hotel/pestana-arena-barcelona",
    "ac-gran-canaria": "https://www.marriott.com/en-us/hotels/lpagr-ac-hotel-gran-canaria/overview/",
    "nou-baleares": "https://www.noubaleares.com/",
    "bonany-palma-3": "https://www.hostalbonany.com/es",
    "bonany-palma-7": "https://www.hostalbonany.com/es",
    "hesperia-palma-7": "https://www.hesperia.com/en/hotel-hesperia-mallorca/",
    "icon-malabar": "https://www.iconhotels.com/en/icon-malabar/",
    "alameda-agp": "https://www.melia.com/en/hotels/spain/malaga/hotel-malaga-alameda-centro-by-melia",
}

PHOTOS = {
    "palma": [
        ("./photos/palma-cathedral.jpg", "Palma Cathedral across the harbour"),
        ("./photos/palma-bellver.jpg", "Bellver Castle above Palma"),
        ("./photos/palma-valldemossa.jpg", "The Cartuja in Valldemossa, Mallorca"),
    ],
    "maspalomas": [
        ("./photos/maspalomas-dunes.jpg", "Maspalomas dunes meeting the Atlantic"),
        ("./photos/maspalomas-lighthouse.jpg", "Maspalomas lighthouse"),
        ("./photos/maspalomas-mogan.jpg", "Puerto de Mogán, Gran Canaria south"),
    ],
    "laspalmas": [
        ("./photos/laspalmas-canteras.jpg", "Las Canteras beach in Las Palmas"),
        ("./photos/laspalmas-santa-ana.jpg", "Plaza de Santa Ana, Las Palmas"),
        ("./photos/laspalmas-casa-colon.jpg", "Casa de Colón in Vegueta"),
    ],
    "malaga": [
        ("./photos/malaga-port.jpg", "The port of Málaga"),
        ("./photos/malaga-cathedral.jpg", "Málaga Cathedral"),
        ("./photos/malaga-alcazaba.jpg", "The Alcazaba of Málaga"),
    ],
    "barcelona": [
        ("./photos/barcelona-sagrada.jpg", "The towers of the Sagrada Família"),
        ("./photos/barcelona-gothic.jpg", "A square in Barcelona’s Gothic Quarter"),
        ("./photos/barcelona-lanes.jpg", "A lane in Barcelona’s Gothic Quarter"),
    ],
}

CITY_LABEL = {
    "palma": "Palma",
    "maspalomas": "Maspalomas",
    "laspalmas": "Las Palmas",
    "malaga": "Málaga",
    "barcelona": "Barcelona",
}

BTN_CITY = {
    "palma": "Palma",
    "maspalomas": "Gran Canaria",
    "laspalmas": "Las Palmas",
    "malaga": "Málaga",
    "barcelona": "Barcelona",
}

AIRPORT = {
    "palma": "PMI",
    "maspalomas": "LPA",
    "laspalmas": "LPA",
    "malaga": "AGP",
    "barcelona": "BCN",
}


def flight(id_, origin, dest, date, airline, depart, notes, adults, nonstop, fetch, price_eur, status="known"):
    item = {
        "id": id_,
        "origin": origin,
        "destination": dest,
        "date": date,
        "airline": airline,
        "depart": depart,
        "notes": notes,
        "adults": adults,
        "nonstop": nonstop,
        "fetch": fetch,
        "price_status": status,
        "gf_url": gf(date, origin, dest, adults),
    }
    if price_eur is None:
        item["price_eur"] = None
    else:
        item["price_eur"] = price_eur
    return item


def hotel(
    id_,
    name,
    dest,
    nights,
    currency,
    price,
    checkin,
    checkout,
    search_name,
    score=None,
    stars=None,
    search_only=False,
    photo_i=0,
    tier="budget",
):
    photos = PHOTOS[dest]
    src, alt = photos[photo_i % len(photos)]
    city = CITY_LABEL[dest]
    item = {
        "id": id_,
        "name": name,
        "dest": dest,
        "nights": nights,
        "currency": currency,
        "price": price,
        "price_status": "check_live" if price is None else "known",
        "checkin": checkin,
        "checkout": checkout,
        "search_only": search_only,
        "tier": tier,
        "room_type": "Private double room",
        "photo": src,
        "photo_alt": alt,
        "photo_caption": f"A photograph of {city}, not the hotel.",
        "booking_url": booking(
            search_name,
            checkin,
            checkout,
            kind="private" if search_only else "named",
        ),
    }
    if score is not None:
        item["score"] = score
    if stars is not None:
        item["stars"] = stars
    if id_ in OFFICIAL:
        item["official_url"] = OFFICIAL[id_]
    return item


def fare_map(flights):
    return {f["id"]: f for f in flights}


def hotel_map(hotels):
    return {h["id"]: h for h in hotels}


def fare_eur(f):
    if f.get("currency") == "USD":
        return None
    if f.get("price_status") == "check_live" or f.get("price_eur") is None:
        return None
    return int(f["price_eur"])


NIGHTS_WORD = {
    1: "one night",
    2: "two nights",
    3: "three nights",
    7: "seven nights",
}


def hotel_price_eur(hotel) -> int | None:
    if hotel.get("currency") == "USD":
        return None
    if hotel.get("price") is None or hotel.get("price_status") == "check_live":
        return None
    return int(hotel["price"])


def plan_totals(plan, flights, hotels):
    ella = fare_eur(flights[plan["ella_in"]])
    ali = fare_eur(flights[plan["ali_in"]])
    tog = fare_eur(flights[plan["together"]])
    hotel = hotels[plan["hotel"]]
    room = hotel_price_eur(hotel)
    home = fare_eur(flights[plan["ella_home"]]) if plan.get("ella_home") else None
    plan["together_missing"] = tog is None
    plan["hotel_missing"] = room is None
    plan["fra_known"] = home is not None
    plan["inbound_eur"] = None if ella is None or ali is None else ella + ali
    pieces = []
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
        return
    sub = ella + ali + tog + room
    plan["subtotal_eur"] = sub
    if home is None:
        plan["total_eur"] = None
        plan["total_complete"] = False
    else:
        plan["total_eur"] = sub + home
        plan["total_complete"] = True
    alt_id = plan.get("alt_hotel")
    if alt_id:
        alt_room = hotel_price_eur(hotels[alt_id])
        if alt_room is not None:
            plan["alt_subtotal_eur"] = ella + ali + tog + alt_room
            plan["alt_total_eur"] = (
                plan["alt_subtotal_eur"] + home if home is not None else None
            )


def build_prices() -> dict:
    flights = [
        flight("haj-pmi-14", "HAJ", "PMI", "2026-12-14", "Eurowings", "07:55", "nonstop", 1, True, True, 84),
        flight("ovd-pmi-14", "OVD", "PMI", "2026-12-14", "Vueling", "08:50", "", 1, False, True, 23),
        flight("pmi-ovd-17", "PMI", "OVD", "2026-12-17", "Vueling", "08:00", "pair for 2 adults", 2, False, True, 68),
        flight("pmi-ovd-21", "PMI", "OVD", "2026-12-21", "Vueling", "06:30", "pair for 2 adults", 2, False, True, 86),
        flight("haj-lpa-16", "HAJ", "LPA", "2026-12-16", "Eurowings", "12:50", "nonstop", 1, True, True, 72),
        flight("ovd-lpa-16", "OVD", "LPA", "2026-12-16", "Air Europa", "", "via Madrid", 1, False, True, 66),
        flight("ovd-lpa-16-binter", "OVD", "LPA", "2026-12-16", "Binter", "", "nonstop alternative, not used in totals", 1, True, True, 186),
        flight("lpa-ovd-19", "LPA", "OVD", "2026-12-19", "Volotea", "18:45", "pair for 2 adults", 2, False, True, 66),
        flight("haj-lpa-15", "HAJ", "LPA", "2026-12-15", "Vueling", "", "via Barcelona", 1, False, True, 131),
        flight("ovd-lpa-15", "OVD", "LPA", "2026-12-15", "", "", "his inbound in the 7-night Gran Canaria flight total", 1, False, True, 76),
        flight("lpa-ovd-22", "LPA", "OVD", "2026-12-22", "", "", "pair for 2 adults", 2, False, True, 103),
        flight("haj-agp-15", "HAJ", "AGP", "2026-12-15", "Vueling", "", "1 stop", 1, False, True, 152),
        flight("ovd-agp-15", "OVD", "AGP", "2026-12-15", "Volotea", "", "", 1, False, True, 24),
        flight("agp-ovd-18", "AGP", "OVD", "2026-12-18", "", "", "pair for 2 adults", 2, False, True, 124),
        flight("haj-agp-18", "HAJ", "AGP", "2026-12-18", "Eurowings", "07:10", "nonstop", 1, True, True, 130),
        flight("ovd-agp-18", "OVD", "AGP", "2026-12-18", "Volotea", "", "", 1, False, True, 28),
        flight("agp-ovd-25", "AGP", "OVD", "2026-12-25", "Volotea", "", "pair for 2 adults", 2, False, True, 77),
        flight("haj-bcn-15", "HAJ", "BCN", "2026-12-15", "Vueling", "10:10", "nonstop", 1, True, True, 77),
        flight("ovd-bcn-15", "OVD", "BCN", "2026-12-15", "Vueling", "20:55", "", 1, False, True, 18),
        flight("bcn-ovd-18", "BCN", "OVD", "2026-12-18", "Vueling", "07:20", "pair for 2 adults", 2, False, True, 144),
        flight("bcn-ovd-22", "BCN", "OVD", "2026-12-22", "Air Europa", "", "pair for 2 adults", 2, False, True, 165),
        flight("ovd-fra-19", "OVD", "FRA", "2026-12-19", "Air Europa", "", "1 stop; no December nonstop. Cheapest in this check.", 1, False, True, 141),
        flight("ovd-fra-20", "OVD", "FRA", "2026-12-20", "Air Europa", "", "1 stop; no December nonstop. Cheapest in this check.", 1, False, True, 91),
        flight("ovd-fra-21", "OVD", "FRA", "2026-12-21", "", "", "No verified fare in this check (FlightsNotFound).", 1, False, True, None, "check_live"),
        flight("ovd-fra-23", "OVD", "FRA", "2026-12-23", "", "", "No verified fare in this check (FlightsNotFound).", 1, False, True, None, "check_live"),
        flight("ovd-fra-24", "OVD", "FRA", "2026-12-24", "", "", "No verified fare in this check (FlightsNotFound).", 1, False, True, None, "check_live"),
        flight("ovd-fra-27", "OVD", "FRA", "2026-12-27", "", "", "No verified fare in this check (FlightsNotFound).", 1, False, True, None, "check_live"),
        flight("ovd-fra-17", "OVD", "FRA", "2026-12-17", "", "", "1 stop; no December nonstop.", 1, False, True, 123),
        flight("ovd-fra-18", "OVD", "FRA", "2026-12-18", "", "", "1 stop; no December nonstop.", 1, False, True, 141),
        flight("ovd-fra-22", "OVD", "FRA", "2026-12-22", "", "", "1 stop; no December nonstop.", 1, False, True, 169),
        flight("pmi-ovd-15", "PMI", "OVD", "2026-12-15", "", "", "pair for 2 adults, 1 stop", 2, False, True, 106),
        flight("pmi-ovd-16", "PMI", "OVD", "2026-12-16", "", "", "pair for 2 adults, 1 stop", 2, False, True, 106),
        flight("lpa-ovd-17", "LPA", "OVD", "2026-12-17", "", "", "pair for 2 adults, 1 stop", 2, False, True, 210),
        flight("lpa-ovd-18", "LPA", "OVD", "2026-12-18", "", "", "pair for 2 adults, 1 stop", 2, False, True, 316),
        flight("agp-ovd-19", "AGP", "OVD", "2026-12-19", "", "", "pair for 2 adults, 1 stop", 2, False, True, 154),
        flight("agp-ovd-20", "AGP", "OVD", "2026-12-20", "", "", "pair for 2 adults, 1 stop", 2, False, True, 154),
        flight("bcn-ovd-16", "BCN", "OVD", "2026-12-16", "", "", "pair for 2 adults, 2 stops — possible self-transfer", 2, False, True, 174),
        flight("bcn-ovd-17", "BCN", "OVD", "2026-12-17", "", "", "pair for 2 adults, 1 stop", 2, False, True, 390),
        {
            "id": "haj-agp-18-usd",
            "origin": "HAJ",
            "destination": "AGP",
            "date": "2026-12-18",
            "airline": "Eurowings",
            "depart": "07:10",
            "notes": "USD reading of the 18–21 Dec inbound; not fetched",
            "adults": 1,
            "nonstop": True,
            "fetch": False,
            "currency": "USD",
            "price_usd": 130,
            "price_status": "known",
            "gf_url": gf("2026-12-18", "HAJ", "AGP", 1),
        },
        {
            "id": "ovd-agp-rt-18-21",
            "origin": "OVD",
            "destination": "AGP",
            "date": "2026-12-18",
            "return_date": "2026-12-21",
            "airline": "Volotea / Air Europa",
            "depart": "11:10",
            "notes": "USD round trip 1 adult; return via Madrid 06:20. Not fetched. Incomplete window — her AGP→OVD on 21 Dec was not priced.",
            "adults": 1,
            "nonstop": False,
            "fetch": False,
            "currency": "USD",
            "price_usd": 111,
            "price_status": "known",
            "gf_url": gf("2026-12-18", "OVD", "AGP", 1),
        },
    ]

    hotels = [
        hotel("brick-palma-3", "Brick Palma", "palma", 3, "EUR", 199, "2026-12-14", "2026-12-17", "Brick Palma Palma", 9.0, None, False, 0),
        hotel("bonany-palma-3", "Hostal Bonany", "palma", 3, "EUR", 214, "2026-12-14", "2026-12-17", "Hostal Bonany Palma", None, None, False, 1),
        hotel("nou-baleares", "Hotel Nou Baleares", "palma", 3, "USD", 387, "2026-12-14", "2026-12-17", "Hotel Nou Baleares", 9.4, 4, False, 2, "nicer"),
        hotel("hesperia-palma-7", "Hesperia Mallorca", "palma", 7, "EUR", 472, "2026-12-14", "2026-12-21", "Hesperia Mallorca", None, None, False, 0),
        hotel("bonany-palma-7", "Hostal Bonany", "palma", 7, "EUR", 489, "2026-12-14", "2026-12-21", "Hostal Bonany Palma", None, None, False, 1),
        hotel("ohana-masp-3", "Casa Ohana", "maspalomas", 3, "EUR", 230, "2026-12-16", "2026-12-19", "Casa Ohana Maspalomas", None, None, False, 0),
        hotel("hhriz-masp-3", "HH Riz", "maspalomas", 3, "EUR", 264, "2026-12-16", "2026-12-19", "HH Riz Maspalomas", None, None, False, 1),
        hotel("masp-south-7", "South-coast search", "maspalomas", 7, "EUR", 536, "2026-12-15", "2026-12-22", "Maspalomas", None, None, True, 2),
        hotel("isleta-lp-3", "La Isleta Linda studio", "laspalmas", 3, "EUR", 155, "2026-12-16", "2026-12-19", "La Isleta Linda Las Palmas", 9.6, None, False, 0),
        hotel("canaria-lp-3", "Casa Canaria", "laspalmas", 3, "EUR", 216, "2026-12-16", "2026-12-19", "Casa Canaria Las Palmas", None, None, False, 1),
        hotel("matilde-lp", "Hotel Matilde Las Palmas", "laspalmas", 3, "USD", 243, "2026-12-16", "2026-12-19", "Hotel Matilde Las Palmas", 8.8, 3, False, 2, "nicer"),
        hotel("cordial-galdos", "Boutique Hotel Cordial Galdós Jardín", "laspalmas", 3, "USD", 352, "2026-12-16", "2026-12-19", "Boutique Hotel Cordial Galdós Jardín", 9.4, 4, False, 0, "nicer"),
        hotel("ac-gran-canaria", "AC Hotel Gran Canaria", "laspalmas", 3, "USD", 354, "2026-12-16", "2026-12-19", "AC Hotel Gran Canaria", 8.4, 4, False, 1, "nicer"),
        hotel("vegueta-lp-7", "Apartamentos Vegueta", "laspalmas", 7, "EUR", 468, "2026-12-15", "2026-12-22", "Apartamentos Vegueta Las Palmas", None, None, False, 2),
        hotel("canaria-lp-7", "Casa Canaria", "laspalmas", 7, "EUR", 513, "2026-12-15", "2026-12-22", "Casa Canaria Las Palmas", None, None, False, 0),
        hotel("nv-agp-3", "Hostal NV Palacio Congresos", "malaga", 3, "EUR", 115, "2026-12-15", "2026-12-18", "Hostal NV Palacio Congresos Malaga", 8.4, None, False, 0),
        hotel("alameda-agp", "Malaga Alameda Centro Affiliated by Meliá", "malaga", 3, "USD", 410, "2026-12-18", "2026-12-21", "Malaga Alameda Centro Affiliated by Meliá", 8.8, 4, False, 1, "nicer"),
        hotel("icon-malabar", "ICON Malabar", "malaga", 3, "USD", 465, "2026-12-18", "2026-12-21", "ICON Malabar", 9.1, 4, False, 2, "nicer"),
        hotel("nv-agp-7", "Hostal NV Palacio Congresos", "malaga", 7, "EUR", 324, "2026-12-18", "2026-12-25", "Hostal NV Palacio Congresos Malaga", None, None, False, 0),
        hotel("maragall-bcn-3", "Hotel BestPrice Maragall", "barcelona", 3, "EUR", 147, "2026-12-15", "2026-12-18", "Hotel BestPrice Maragall Barcelona", None, None, False, 0),
        hotel("arc-rambla", "Hotel Arc La Rambla", "barcelona", 3, "USD", 231, "2026-12-15", "2026-12-18", "Hotel Arc La Rambla", 8.8, 3, False, 1, "nicer"),
        hotel("arcelon", "Hotel Arcelon", "barcelona", 3, "USD", 238, "2026-12-15", "2026-12-18", "Hotel Arcelon", 8.8, 4, False, 2, "nicer"),
        hotel("pestana-arena", "Pestana Arena Barcelona", "barcelona", 3, "USD", 261, "2026-12-15", "2026-12-18", "Pestana Arena Barcelona", 8.8, 4, False, 0, "nicer"),
        hotel("argo-bcn-7", "Hostal Argo", "barcelona", 7, "EUR", 427, "2026-12-15", "2026-12-22", "Hostal Argo Barcelona", None, None, False, 1),
        hotel("house-bcn-7", "Hostal House", "barcelona", 7, "EUR", 410, "2026-12-15", "2026-12-22", "Hostal House Barcelona", None, None, False, 2),
        hotel("palma-priv-1", "Palma private-room search", "palma", 1, "EUR", None, "2026-12-14", "2026-12-15", "Palma", None, None, True, 0),
        hotel("palma-priv-2", "Palma private-room search", "palma", 2, "EUR", None, "2026-12-14", "2026-12-16", "Palma", None, None, True, 1),
        hotel("lp-priv-1", "Las Palmas private-room search", "laspalmas", 1, "EUR", None, "2026-12-16", "2026-12-17", "Las Palmas", None, None, True, 0),
        hotel("lp-priv-2", "Las Palmas private-room search", "laspalmas", 2, "EUR", None, "2026-12-16", "2026-12-18", "Las Palmas", None, None, True, 1),
        hotel("masp-priv-1", "Maspalomas private-room search", "maspalomas", 1, "EUR", None, "2026-12-16", "2026-12-17", "Maspalomas", None, None, True, 0),
        hotel("masp-priv-2", "Maspalomas private-room search", "maspalomas", 2, "EUR", None, "2026-12-16", "2026-12-18", "Maspalomas", None, None, True, 1),
        hotel("agp-priv-1", "Málaga private-room search", "malaga", 1, "EUR", None, "2026-12-18", "2026-12-19", "Málaga", None, None, True, 0),
        hotel("agp-priv-2", "Málaga private-room search", "malaga", 2, "EUR", None, "2026-12-18", "2026-12-20", "Málaga", None, None, True, 1),
        hotel("bcn-priv-1", "Barcelona private-room search", "barcelona", 1, "EUR", None, "2026-12-15", "2026-12-16", "Barcelona", None, None, True, 0),
        hotel("bcn-priv-2", "Barcelona private-room search", "barcelona", 2, "EUR", None, "2026-12-15", "2026-12-17", "Barcelona", None, None, True, 1),
    ]

    plans = [
        {
            "id": "palma-1", "dest": "palma", "nights": 1, "headline": True,
            "arrive": "2026-12-14", "leave": "2026-12-15", "asturias_nights": 2,
            "ella_in": "haj-pmi-14", "ali_in": "ovd-pmi-14", "together": "pmi-ovd-15",
            "ella_home": "ovd-fra-17", "hotel": "palma-priv-1",
        },
        {
            "id": "palma-2", "dest": "palma", "nights": 2, "headline": True,
            "arrive": "2026-12-14", "leave": "2026-12-16", "asturias_nights": 2,
            "ella_in": "haj-pmi-14", "ali_in": "ovd-pmi-14", "together": "pmi-ovd-16",
            "ella_home": "ovd-fra-18", "hotel": "palma-priv-2",
        },
        {
            "id": "palma-3", "dest": "palma", "nights": 3, "headline": True,
            "arrive": "2026-12-14", "leave": "2026-12-17", "asturias_nights": 2,
            "ella_in": "haj-pmi-14", "ali_in": "ovd-pmi-14", "together": "pmi-ovd-17",
            "ella_home": "ovd-fra-19", "hotel": "brick-palma-3", "alt_hotel": "bonany-palma-3",
        },
        {
            "id": "palma-7", "dest": "palma", "nights": 7, "headline": True,
            "arrive": "2026-12-14", "leave": "2026-12-21", "asturias_nights": 2,
            "ella_in": "haj-pmi-14", "ali_in": "ovd-pmi-14", "together": "pmi-ovd-21",
            "ella_home": "ovd-fra-23", "hotel": "hesperia-palma-7", "alt_hotel": "bonany-palma-7",
        },
        {
            "id": "masp-1", "dest": "maspalomas", "nights": 1, "headline": True,
            "arrive": "2026-12-16", "leave": "2026-12-17", "asturias_nights": 2,
            "ella_in": "haj-lpa-16", "ali_in": "ovd-lpa-16", "together": "lpa-ovd-17",
            "ella_home": "ovd-fra-19", "hotel": "masp-priv-1",
        },
        {
            "id": "masp-2", "dest": "maspalomas", "nights": 2, "headline": True,
            "arrive": "2026-12-16", "leave": "2026-12-18", "asturias_nights": 2,
            "ella_in": "haj-lpa-16", "ali_in": "ovd-lpa-16", "together": "lpa-ovd-18",
            "ella_home": "ovd-fra-20", "hotel": "masp-priv-2",
        },
        {
            "id": "masp-3", "dest": "maspalomas", "nights": 3, "headline": True,
            "arrive": "2026-12-16", "leave": "2026-12-19", "asturias_nights": 2,
            "ella_in": "haj-lpa-16", "ali_in": "ovd-lpa-16", "together": "lpa-ovd-19",
            "ella_home": "ovd-fra-21", "hotel": "ohana-masp-3", "alt_hotel": "hhriz-masp-3",
        },
        {
            "id": "masp-7", "dest": "maspalomas", "nights": 7, "headline": True,
            "arrive": "2026-12-15", "leave": "2026-12-22", "asturias_nights": 2,
            "ella_in": "haj-lpa-15", "ali_in": "ovd-lpa-15", "together": "lpa-ovd-22",
            "ella_home": "ovd-fra-24", "hotel": "masp-south-7",
        },
        {
            "id": "lp-1", "dest": "laspalmas", "nights": 1, "headline": True,
            "arrive": "2026-12-16", "leave": "2026-12-17", "asturias_nights": 2,
            "ella_in": "haj-lpa-16", "ali_in": "ovd-lpa-16", "together": "lpa-ovd-17",
            "ella_home": "ovd-fra-19", "hotel": "lp-priv-1",
        },
        {
            "id": "lp-2", "dest": "laspalmas", "nights": 2, "headline": True,
            "arrive": "2026-12-16", "leave": "2026-12-18", "asturias_nights": 2,
            "ella_in": "haj-lpa-16", "ali_in": "ovd-lpa-16", "together": "lpa-ovd-18",
            "ella_home": "ovd-fra-20", "hotel": "lp-priv-2",
        },
        {
            "id": "lp-3", "dest": "laspalmas", "nights": 3, "headline": True,
            "arrive": "2026-12-16", "leave": "2026-12-19", "asturias_nights": 2,
            "ella_in": "haj-lpa-16", "ali_in": "ovd-lpa-16", "together": "lpa-ovd-19",
            "ella_home": "ovd-fra-21", "hotel": "isleta-lp-3", "alt_hotel": "canaria-lp-3",
        },
        {
            "id": "lp-7", "dest": "laspalmas", "nights": 7, "headline": True,
            "arrive": "2026-12-15", "leave": "2026-12-22", "asturias_nights": 2,
            "ella_in": "haj-lpa-15", "ali_in": "ovd-lpa-15", "together": "lpa-ovd-22",
            "ella_home": "ovd-fra-24", "hotel": "vegueta-lp-7", "alt_hotel": "canaria-lp-7",
        },
        {
            "id": "malaga-1", "dest": "malaga", "nights": 1, "headline": True,
            "arrive": "2026-12-18", "leave": "2026-12-19", "asturias_nights": 2,
            "ella_in": "haj-agp-18", "ali_in": "ovd-agp-18", "together": "agp-ovd-19",
            "ella_home": "ovd-fra-21", "hotel": "agp-priv-1",
        },
        {
            "id": "malaga-2", "dest": "malaga", "nights": 2, "headline": True,
            "arrive": "2026-12-18", "leave": "2026-12-20", "asturias_nights": 2,
            "ella_in": "haj-agp-18", "ali_in": "ovd-agp-18", "together": "agp-ovd-20",
            "ella_home": "ovd-fra-22", "hotel": "agp-priv-2",
        },
        {
            "id": "malaga-3", "dest": "malaga", "nights": 3, "headline": True,
            "arrive": "2026-12-15", "leave": "2026-12-18", "asturias_nights": 2,
            "ella_in": "haj-agp-15", "ali_in": "ovd-agp-15", "together": "agp-ovd-18",
            "ella_home": "ovd-fra-20", "hotel": "nv-agp-3",
        },
        {
            "id": "malaga-7", "dest": "malaga", "nights": 7, "headline": True,
            "arrive": "2026-12-18", "leave": "2026-12-25", "asturias_nights": 2,
            "ella_in": "haj-agp-18", "ali_in": "ovd-agp-18", "together": "agp-ovd-25",
            "ella_home": "ovd-fra-27", "hotel": "nv-agp-7",
        },
        {
            "id": "bcn-1", "dest": "barcelona", "nights": 1, "headline": True,
            "arrive": "2026-12-15", "leave": "2026-12-16", "asturias_nights": 2,
            "ella_in": "haj-bcn-15", "ali_in": "ovd-bcn-15", "together": "bcn-ovd-16",
            "ella_home": "ovd-fra-18", "hotel": "bcn-priv-1",
        },
        {
            "id": "bcn-2", "dest": "barcelona", "nights": 2, "headline": True,
            "arrive": "2026-12-15", "leave": "2026-12-17", "asturias_nights": 2,
            "ella_in": "haj-bcn-15", "ali_in": "ovd-bcn-15", "together": "bcn-ovd-17",
            "ella_home": "ovd-fra-19", "hotel": "bcn-priv-2",
        },
        {
            "id": "bcn-3", "dest": "barcelona", "nights": 3, "headline": True,
            "arrive": "2026-12-15", "leave": "2026-12-18", "asturias_nights": 2,
            "ella_in": "haj-bcn-15", "ali_in": "ovd-bcn-15", "together": "bcn-ovd-18",
            "ella_home": "ovd-fra-20", "hotel": "maragall-bcn-3",
        },
        {
            "id": "bcn-7", "dest": "barcelona", "nights": 7, "headline": True,
            "arrive": "2026-12-15", "leave": "2026-12-22", "asturias_nights": 2,
            "ella_in": "haj-bcn-15", "ali_in": "ovd-bcn-15", "together": "bcn-ovd-22",
            "ella_home": "ovd-fra-24", "hotel": "house-bcn-7", "alt_hotel": "argo-bcn-7",
        },
    ]

    for plan in plans:
        plan["flights"] = [plan["ella_in"], plan["ali_in"], plan["together"]]

    data = {
        "snapshot": "2026-11-25",
        "hotels_checked": "2026-11-22",
        "usd_to_eur": 0.86,
        "flights": flights,
        "hotels": hotels,
        "plans": plans,
        "bundles": [
            {"id": "gc-3", "flights": ["haj-lpa-16", "ovd-lpa-16", "lpa-ovd-19"], "total_eur": 225},
            {"id": "gc-7", "flights": ["haj-lpa-15", "ovd-lpa-15", "lpa-ovd-22"], "total_eur": 262},
            {"id": "gc-16-22", "flights": ["haj-lpa-16", "ovd-lpa-16", "lpa-ovd-22"], "total_eur": 210},
        ],
        "usd_partials": {"alameda": 651, "malabar": 706},
        "notes": {
            "itinerary": "Ella HAJ→city; Ali OVD→city; private double for all N city nights (1, 2, 3 or 7); both city→OVD (2 adults, stored as a pair); 2 nights in Asturias at home (no hotel); Ella OVD→FRA one way after those days. No return to Hannover. Totals use cheapest private room. Unverified 1n/2n rooms are check live, excluded from totals.",
            "ovd_fra": "No nonstop OVD→FRA in December 2026 (Lufthansa nonstop starts March 2027). 17 Dec €123, 18 Dec €141, 19 Dec €141, 20 Dec €91, 22 Dec €169 Air Europa 1-stop, fetched 23 Nov 2026. 21, 23, 24, 27 Dec: check live.",
            "needs_check": [
                "Palma 1n 14–15 Dec: private double room (palma-priv-1). Return PMI→OVD 15 Dec is verified €106/pair.",
                "Palma 2n 14–16 Dec: private double room (palma-priv-2). Return PMI→OVD 16 Dec is verified €106/pair.",
                "Las Palmas 1n 16–17 Dec: private double room (lp-priv-1). Return LPA→OVD 17 Dec is verified €210/pair.",
                "Las Palmas 2n 16–18 Dec: private double room (lp-priv-2). Return LPA→OVD 18 Dec is verified €316/pair.",
                "Maspalomas 1n 16–17 Dec: private double room (masp-priv-1). Same LPA flights as Las Palmas 1n.",
                "Maspalomas 2n 16–18 Dec: private double room (masp-priv-2). Same LPA flights as Las Palmas 2n.",
                "Málaga 1n 18–19 Dec: private double room (agp-priv-1). Return AGP→OVD 19 Dec is verified €154/pair. Also Ella OVD→FRA 21 Dec (check live).",
                "Málaga 2n 18–20 Dec: private double room (agp-priv-2). Return AGP→OVD 20 Dec is verified €154/pair.",
                "Barcelona 1n 15–16 Dec: private double room (bcn-priv-1). Return BCN→OVD 16 Dec is verified €174/pair (2 stops, possible self-transfer).",
                "Barcelona 2n 15–17 Dec: private double room (bcn-priv-2). Return BCN→OVD 17 Dec is verified €390/pair.",
            ],
        },
    }

    fmap = fare_map(flights)
    hmap = hotel_map(hotels)
    for plan in plans:
        plan_totals(plan, fmap, hmap)
    for bundle in data["bundles"]:
        bundle["total_eur"] = sum(int(fmap[i]["price_eur"]) for i in bundle["flights"])
    return data


def money_flight(f) -> str:
    if f.get("price_status") == "check_live" or f.get("price_eur") is None:
        return "check live price"
    if f.get("currency") == "USD":
        return f"${int(f['price_usd'])}"
    return euro(f["price_eur"])


def display_plan(plan) -> str:
    if plan.get("total_complete"):
        return euro(plan["total_eur"])
    notes = []
    if plan.get("together_missing"):
        notes.append("plus the shared flight home (check live)")
    if plan.get("hotel_missing"):
        notes.append("plus the private room (check live)")
    if not plan.get("fra_known"):
        notes.append("plus her flight to Frankfurt")
    if plan.get("subtotal_eur") is not None:
        return euro(plan["subtotal_eur"]) + (" " + " ".join(notes) if notes else "")
    if plan.get("partial_eur") is not None:
        return euro(plan["partial_eur"]) + (" " + " ".join(notes) if notes else "")
    return "check live"


def flight_line(f) -> str:
    bits = []
    if f.get("airline"):
        bits.append(f["airline"])
    if f.get("depart"):
        bits.append(f["depart"])
    notes = (f.get("notes") or "").replace("pair for 2 adults, ", "").replace("pair for 2 adults", "").strip(" ,")
    if notes:
        bits.append(notes)
    return ", ".join(bits)


def buttons(plan, fmap, hmap, dest_id):
    city = BTN_CITY[dest_id]
    ella = fmap[plan["ella_in"]]
    ali = fmap[plan["ali_in"]]
    tog = fmap[plan["together"]]
    home = fmap[plan["ella_home"]]
    hotel = hmap[plan["hotel"]]
    search_city = {
        "palma": "Palma",
        "maspalomas": "Maspalomas",
        "laspalmas": "Las Palmas",
        "malaga": "Málaga",
        "barcelona": "Barcelona",
    }[dest_id]
    hotel_href = hotel.get("official_url") or hotel["booking_url"]
    city_search = booking(search_city, hotel["checkin"], hotel["checkout"], kind="private")
    hotel_btn = ""
    if not hotel.get("search_only"):
        hotel_btn = (
            f'<a class="book-link book-link--hotel" href="{escape(hotel_href, quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">See hotel</a>'
        )
    return f"""
        <div class="book-grid">
          <a class="book-link book-link--ella" href="{escape(ella['gf_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Ella: Hannover → {escape(city)}</a>
          <a class="book-link book-link--ali" href="{escape(ali['gf_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Ali: Oviedo → {escape(city)}</a>
          <a class="book-link book-link--together" href="{escape(tog['gf_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Together: {escape(city)} → Asturias (2 people)</a>
          <a class="book-link book-link--home" href="{escape(home['gf_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Ella: Asturias → Frankfurt</a>
          {hotel_btn}
          <a class="book-link book-link--search" href="{escape(city_search, quote=True)}" target="_blank" rel="noopener noreferrer">Search private rooms for two, {escape(CITY_LABEL[dest_id])}</a>
        </div>"""


def sdr_bio(date: str) -> str:
    sdr = gf(date, "SDR", "FRA", 1)
    bio = gf(date, "BIO", "FRA", 1)
    return (
        f'<p class="alt-airports">No direct OVD→FRA in December. If the Madrid connection is awkward, '
        f'<a href="{escape(sdr, quote=True)}" target="_blank" rel="noopener noreferrer">Santander → Frankfurt</a> '
        f'and <a href="{escape(bio, quote=True)}" target="_blank" rel="noopener noreferrer">Bilbao → Frankfurt</a> '
        f"are easy dated Google Flights searches — check live, we did not store a price.</p>"
    )


def stay_block(plan, fmap, hmap, dest_id, extra_html=""):
    ella = fmap[plan["ella_in"]]
    ali = fmap[plan["ali_in"]]
    tog = fmap[plan["together"]]
    home = fmap[plan["ella_home"]]
    hotel = hmap[plan["hotel"]]
    nights_word = NIGHTS_WORD.get(plan["nights"], f"{plan['nights']} nights")
    home_bind = f'data-bind="f:{home["id"]}"'
    total_bind = f'data-bind="p:{plan["id"]}:display"'
    sub_bind = f'data-bind="p:{plan["id"]}:sub"'
    fra_note = f'<span {home_bind}>{escape(money_flight(home))}</span>'
    alt = ""
    if plan.get("alt_hotel"):
        ah = hmap[plan["alt_hotel"]]
        alt_price = euro(ah["price"]) if ah["currency"] == "EUR" else f"${ah['price']}"
        alt_tot = display_plan({"total_complete": plan.get("total_complete") and plan.get("alt_total_eur") is not None, "total_eur": plan.get("alt_total_eur"), "subtotal_eur": plan.get("alt_subtotal_eur")})
        alt = (
            f'<p class="alt-stay">Other private room we priced: {escape(ah["name"])} at '
            f'<span data-bind="h:{ah["id"]}">{alt_price}</span> for the same {ah["nights"]} nights '
            f'({pretty(ah["checkin"])} – {pretty(ah["checkout"])}). '
            f'That trip is about <span data-bind="p:{plan["id"]}:alt">{escape(alt_tot)}</span>.</p>'
        )
    if hotel.get("price") is None or hotel.get("price_status") == "check_live":
        hotel_price_html = f'<span data-bind="h:{hotel["id"]}">check live price</span>'
        hotel_who = "a Booking search for a private double (no named hotel — we did not invent a price)"
    elif hotel.get("search_only"):
        hotel_price_html = f'<span data-bind="h:{hotel["id"]}">{euro(hotel["price"])}</span>'
        hotel_who = "a south-coast private-room search (not a named property)"
    elif hotel.get("currency") == "EUR":
        hotel_price_html = f'<span data-bind="h:{hotel["id"]}">{euro(hotel["price"])}</span>'
        hotel_who = escape(hotel["name"])
    else:
        hotel_price_html = "check live price"
        hotel_who = escape(hotel["name"])
    fra_copy = (
        f"Air Europa, 1 stop, {fra_note}. There is no nonstop this month — Lufthansa’s direct starts in March 2027."
        if home.get("price_eur") is not None
        else f"{fra_note}. There is no nonstop this month — Lufthansa’s direct starts in March 2027. Totals below do not invent a Frankfurt fare."
    )
    hotel_nights_label = "1 night" if plan["nights"] == 1 else f"{plan['nights']} nights"
    hotel_line = (
        f"Hotel: {hotel_nights_label}, check-in {pretty(hotel['checkin'])}, "
        f"check-out {pretty(hotel['checkout'])}"
    )
    return f"""
      <article class="stay" id="{escape(plan['id'])}">
        <header class="stay-head">
          <p class="kicker">Budget private room · {nights_word}</p>
          <h3>{escape(CITY_LABEL[dest_id])}, {pretty(plan['arrive'])} – {pretty(plan['leave'])}</h3>
        </header>
        <ol class="timeline">
          <li>
            <span class="step-n">1</span>
            <div>
              <h4>Ella: Hannover → {escape(BTN_CITY[dest_id])}</h4>
              <p>{pretty(ella['date'])}. {escape(flight_line(ella))}. <strong data-bind="f:{ella['id']}">{escape(money_flight(ella))}</strong>, one adult.</p>
            </div>
          </li>
          <li>
            <span class="step-n">2</span>
            <div>
              <h4>Ali: Oviedo → {escape(BTN_CITY[dest_id])}</h4>
              <p>{pretty(ali['date'])}. {escape(flight_line(ali))}. <strong data-bind="f:{ali['id']}">{escape(money_flight(ali))}</strong>, one adult.</p>
            </div>
          </li>
          <li>
            <span class="step-n">3</span>
            <div>
              <h4>{escape(hotel_line)}</h4>
              <p>Private double room for two at {hotel_who}. Check-in on the day you arrive, check-out on the day you fly together to Asturias. <strong>{hotel_price_html}</strong> for {hotel_nights_label} (2 adults, 1 room). Hotels last checked <span data-bind="hotels_checked">22 November 2026</span>, before about 10% tax. Never a shared dorm.</p>
            </div>
          </li>
          <li>
            <span class="step-n">4</span>
            <div>
              <h4>Together: {escape(BTN_CITY[dest_id])} → Asturias</h4>
              <p>{pretty(tog['date'])} — same day as hotel check-out. {escape(flight_line(tog))}. <strong data-bind="f:{tog['id']}">{escape(money_flight(tog))}</strong> for two people (already a pair, not twice a one-person fare).</p>
            </div>
          </li>
          <li>
            <span class="step-n">5</span>
            <div>
              <h4>A couple of days in Asturias, at home</h4>
              <p>Two slow days together after the city. No hotel — you stay at home. Then Ella’s last flight is Asturias to Frankfurt.</p>
            </div>
          </li>
          <li>
            <span class="step-n">6</span>
            <div>
              <h4>Ella: Asturias (OVD) → Frankfurt (FRA)</h4>
              <p>After the days in Asturias, {pretty(home['date'])}. {fra_copy}</p>
              {sdr_bio(home['date'])}
            </div>
          </li>
        </ol>
        {alt}
        {extra_html}
        <p class="stay-total">Trip total: <strong {total_bind}>{escape(display_plan(plan))}</strong>. Known flights (without an unverified home leg or an unpriced room): <span {sub_bind}>{euro(plan['subtotal_eur'] if plan.get('subtotal_eur') is not None else plan.get('partial_eur')) if (plan.get('subtotal_eur') is not None or plan.get('partial_eur') is not None) else '—'}</span>. Totals never invent a missing return or hotel figure.</p>
        {buttons(plan, fmap, hmap, dest_id)}
      </article>"""


def hotel_card(h, used_in=""):
    meta = []
    if h.get("stars"):
        meta.append(f'{h["stars"]}★')
    if h.get("score") is not None:
        meta.append(f'score {h["score"]}')
    nights_label = "1 night" if h["nights"] == 1 else f"{h['nights']} nights"
    nights_line = (
        f"Hotel: {nights_label}, check-in {pretty(h['checkin'])}, "
        f"check-out {pretty(h['checkout'])}"
    )
    if h["currency"] == "USD":
        price = f'<p class="hotel-price" data-bind="usd:{h["id"]}">${int(h["price"])}</p>'
        approx = f'<p class="hotel-approx">USD as returned. About <span data-bind="usdapprox:{h["id"]}">{euro(round(h["price"] * 0.86))}</span> at 1 USD ≈ 0.86 EUR.</p>'
    elif h.get("price") is None or h.get("price_status") == "check_live":
        price = f'<p class="hotel-price" data-bind="h:{h["id"]}">check live price</p>'
        approx = '<p class="hotel-approx">No stored fare — open the private-room search. We did not invent a price.</p>'
    else:
        price = f'<p class="hotel-price" data-bind="h:{h["id"]}">{euro(h["price"])}</p>'
        approx = '<p class="hotel-approx">EUR, Booking.com, before about 10% tax. Total for those nights, not per night.</p>'
    see = h.get("official_url") or h["booking_url"]
    see_label = "See hotel" if not h.get("search_only") else "Search private rooms for two"
    used = f'<p class="hotel-used">{escape(used_in)}</p>' if used_in else ""
    name = h["name"]
    if h["id"] == "masp-south-7":
        name = "Maspalomas south-coast search"
    tier = "Nicer stay" if h.get("tier") == "nicer" else "Budget private room"
    return f"""
        <article class="hotel-card hotel-card--{escape(h.get('tier') or 'budget')}">
          <figure>
            <img src="{escape(h['photo'], quote=True)}" alt="{escape(h['photo_alt'])}" width="800" height="520" loading="lazy">
            <figcaption>{escape(h['photo_caption'])}</figcaption>
          </figure>
          <div class="hotel-body">
            <p class="room-badge">{escape(tier)} · Private double room</p>
            <h3>{escape(name)}</h3>
            <p class="hotel-meta">{escape(' · '.join(meta + ['Private room for two']))}</p>
            <p class="hotel-nights">{escape(nights_line)}</p>
            {price}
            {approx}
            {used}
            <a class="book-link book-link--hotel" href="{escape(see, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(see_label)}</a>
          </div>
        </article>"""


DESTS = [
    {
        "id": "palma",
        "name": "Palma",
        "full": "Palma, Mallorca",
        "photo": "./photos/palma-cathedral.jpg",
        "photo_alt": "Palma Cathedral, La Seu, seen across the water from the harbour",
        "lede": "Gold stone, winter sea, and a compact old town you can walk. Cheapest private rooms: Brick Palma for three nights, Hesperia Mallorca for a week. Hostal Bonany is the other private room we priced.",
        "plans": ["palma-1", "palma-2", "palma-3", "palma-7"],
        "budget_hotels": ["palma-priv-1", "palma-priv-2", "brick-palma-3", "bonany-palma-3", "hesperia-palma-7", "bonany-palma-7"],
        "nicer_hotels": ["nou-baleares"],
        "hotel_used": {
            "palma-priv-1": "One-night private-room search for 14–15 December. No stored price — check live.",
            "palma-priv-2": "Two-night private-room search for 14–16 December. No stored price — check live.",
            "brick-palma-3": "Cheapest private room we priced for three nights — used in the total.",
            "bonany-palma-3": "Private room for two. Priced alternative for three nights.",
            "nou-baleares": "Nicer 4★ pick, USD, not in the euro total.",
            "hesperia-palma-7": "Cheapest private room we priced for a week — used in the total.",
            "bonany-palma-7": "Private room for two. Priced alternative for seven nights.",
        },
        "extra": {
            "palma-1": '<p class="fine">Best inbound alignment: both arrive 14 December (Ella’s Eurowings nonstop). The 15 December flight home is priced; the private room is not — search Booking, we did not invent a figure.</p>',
            "palma-2": '<p class="fine">Same 14 December inbounds as the one-night plan. Room price not stored.</p>',
            "palma-7": '<p class="fine">Home to Asturias on 21 December is Vueling 06:30 — an early start.</p>',
        },
    },
    {
        "id": "laspalmas",
        "name": "Las Palmas",
        "full": "Las Palmas, Gran Canaria city",
        "photo": "./photos/laspalmas-canteras.jpg",
        "photo_alt": "Las Canteras beach with the Alfredo Kraus auditorium at the far end",
        "lede": "A real city with a long beach. Same Gran Canaria flights as Maspalomas — airport LPA. Cheapest private rooms: La Isleta Linda studio for three nights, Apartamentos Vegueta for a week. Casa Canaria is the other private room we priced.",
        "plans": ["lp-1", "lp-2", "lp-3", "lp-7"],
        "budget_hotels": ["lp-priv-1", "lp-priv-2", "isleta-lp-3", "canaria-lp-3", "vegueta-lp-7", "canaria-lp-7"],
        "nicer_hotels": ["matilde-lp", "cordial-galdos", "ac-gran-canaria"],
        "hotel_used": {
            "lp-priv-1": "One-night private-room search for 16–17 December. No stored price — check live.",
            "lp-priv-2": "Two-night private-room search for 16–18 December. No stored price — check live.",
            "isleta-lp-3": "Cheapest private room we priced for three nights — used in the total.",
            "canaria-lp-3": "Private room for two. Priced alternative for three nights.",
            "matilde-lp": "Nicer 3★ pick, USD, not in the euro total.",
            "cordial-galdos": "Nicer 4★ pick, USD, not in the euro total.",
            "ac-gran-canaria": "Nicer 4★ pick, USD, not in the euro total.",
            "vegueta-lp-7": "Cheapest private room we priced for a week — used in the total.",
            "canaria-lp-7": "Private room for two. Priced alternative for seven nights.",
        },
        "extra": {
            "lp-1": '<p class="fine">Uses Ella’s <span data-bind="f:haj-lpa-16">€72</span> nonstop on 16 December. The 17 December flight home for two is dearer than the 19 December three-night return. Room not stored.</p>',
            "lp-2": '<p class="fine">Same cheap 16 December inbounds. The 18 December flight home for two is expensive; room not stored.</p>',
            "lp-7": '<p class="fine">Arriving a day later, 16–22 December, keeps Ella on the <span data-bind="f:haj-lpa-16">€72</span> nonstop and drops city flights to <span data-bind="b:gc-16-22">€241</span>. That is not the headline seven-night total.</p>',
        },
    },
    {
        "id": "maspalomas",
        "name": "Maspalomas",
        "full": "Maspalomas, Gran Canaria south",
        "photo": "./photos/maspalomas-dunes.jpg",
        "photo_alt": "Aerial view of the Maspalomas dunes meeting the Atlantic",
        "lede": "Dunes, lighthouse, south-coast light. You still fly into Las Palmas (LPA). Cheapest private room for three nights: Casa Ohana. HH Riz is the other private room we priced. For a week we only have a south-coast private-room search, not a named hotel. We did not price 3–4★ rooms here.",
        "plans": ["masp-1", "masp-2", "masp-3", "masp-7"],
        "budget_hotels": ["masp-priv-1", "masp-priv-2", "ohana-masp-3", "hhriz-masp-3", "masp-south-7"],
        "nicer_hotels": [],
        "hotel_used": {
            "masp-priv-1": "One-night private-room search for 16–17 December. No stored price — check live.",
            "masp-priv-2": "Two-night private-room search for 16–18 December. No stored price — check live.",
            "ohana-masp-3": "Cheapest private room we priced for three nights — used in the total.",
            "hhriz-masp-3": "Private room for two. Priced alternative for three nights.",
            "masp-south-7": "Used in the seven-night total — a private-room search price, not a named hotel. HH Riz was unavailable these dates.",
        },
        "extra": {
            "masp-1": '<p class="fine">Same Gran Canaria flights as Las Palmas — airport LPA, Ella’s 16 December nonstop. Room not stored.</p>',
            "masp-2": '<p class="fine">Same 16 December inbounds. The 18 December LPA→OVD pair is expensive. Room not stored.</p>',
            "masp-3": '<p class="fine">Ali’s inbound has a dearer Binter nonstop at <span data-bind="f:ovd-lpa-16-binter">€186</span>; the total uses Air Europa via Madrid at <span data-bind="f:ovd-lpa-16">€66</span>.</p>',
            "masp-7": '<p class="fine">Arriving 16–22 December keeps Ella on the <span data-bind="f:haj-lpa-16">€72</span> nonstop (city flights <span data-bind="b:gc-16-22">€241</span>). That is not the headline seven-night total.</p>',
        },
    },
    {
        "id": "malaga",
        "name": "Málaga",
        "full": "Málaga",
        "photo": "./photos/malaga-port.jpg",
        "photo_alt": "The port of Málaga with the cathedral towers beyond",
        "lede": "Picasso’s city, a working port, winter sun on the mainland. Cheapest private room: Hostal NV Palacio Congresos. The 4★ picks were priced for 18–21 December, a different window.",
        "plans": ["malaga-1", "malaga-2", "malaga-3", "malaga-7"],
        "budget_hotels": ["agp-priv-1", "agp-priv-2", "nv-agp-3", "nv-agp-7"],
        "nicer_hotels": ["alameda-agp", "icon-malabar"],
        "hotel_used": {
            "agp-priv-1": "One-night private-room search for 18–19 December (Ella’s Eurowings nonstop). No stored price — check live.",
            "agp-priv-2": "Two-night private-room search for 18–20 December. No stored price — check live.",
            "nv-agp-3": "Cheapest private room we priced for 15–18 December — used in the three-night total.",
            "alameda-agp": "Nicer 4★ pick for 18–21 December, USD. Together AGP→OVD on 21 December was not priced, so this is not a headline plan.",
            "icon-malabar": "Nicer 4★ pick for 18–21 December, USD. Same incomplete window.",
            "nv-agp-7": "Cheapest private room we priced for 18–25 December — used in the seven-night total.",
        },
        "extra": {
            "malaga-1": '<p class="fine">Best inbound alignment is 18 December (Ella nonstop). Frankfurt on 21 December is still check live. Room not stored.</p>',
            "malaga-2": '<p class="fine">Same 18 December inbounds. Room not stored.</p>',
            "malaga-3": '<p class="fine">There is a second three-night window, 18–21 December, on Ella’s Eurowings 07:10 nonstop (about <span data-bind="usd:haj-agp-18-usd">$130</span>). Ali’s OVD–AGP round trip those dates was about <span data-bind="usd:ovd-agp-rt-18-21">$111</span>. Her flight home to Asturias on 21 December was not priced, so it is not a full plan. Partial with Alameda Centro: about <span data-bind="partial:alameda">$651</span>; with ICON Malabar about <span data-bind="partial:malabar">$706</span>.</p>',
        },
    },
    {
        "id": "barcelona",
        "name": "Barcelona",
        "full": "Barcelona",
        "photo": "./photos/barcelona-sagrada.jpg",
        "photo_alt": "The towers of the Sagrada Família in Barcelona",
        "lede": "The Christmas-city option, and the best-value 3–4★ rooms we priced. Cheapest private rooms: Hotel BestPrice Maragall for three nights, Hostal House for a week. Hostal Argo is the other private week we priced.",
        "plans": ["bcn-1", "bcn-2", "bcn-3", "bcn-7"],
        "budget_hotels": ["bcn-priv-1", "bcn-priv-2", "maragall-bcn-3", "house-bcn-7", "argo-bcn-7"],
        "nicer_hotels": ["arc-rambla", "arcelon", "pestana-arena"],
        "hotel_used": {
            "bcn-priv-1": "One-night private-room search for 15–16 December. No stored price — check live.",
            "bcn-priv-2": "Two-night private-room search for 15–17 December. No stored price — check live.",
            "maragall-bcn-3": "Cheapest private room we priced for three nights — used in the total.",
            "arc-rambla": "Nicer 3★ pick, USD, not in the euro total.",
            "arcelon": "Nicer 4★ pick, USD, not in the euro total.",
            "pestana-arena": "Nicer 4★ pick, USD, not in the euro total.",
            "argo-bcn-7": "Private room for two. Priced alternative for seven nights.",
            "house-bcn-7": "Cheapest private room we priced for a week — used in the total.",
        },
        "extra": {
            "bcn-1": '<p class="fine">Both arrive 15 December on cheap Vueling. The 16 December flight home has two stops — possible self-transfer, separate tickets. Room not stored.</p>',
            "bcn-2": '<p class="fine">Same 15 December inbounds. The 17 December flight home for two is expensive. Room not stored.</p>',
        },
    },
]


def compare_cell(plan) -> str:
    badge_n = plan["nights"]
    dest = plan["dest"]
    return (
        f'<td><span data-bind="p:{plan["id"]}:display">{escape(display_plan(plan))}</span> '
        f'<span class="best-tag" data-if-cheapest="{dest}:{badge_n}" hidden>Cheapest {badge_n}n</span> '
        f'<span class="best-tag best-tag--value" data-if-best-value="{dest}:{badge_n}" hidden>Best value</span> '
        f'<span class="best-tag best-tag--trip" data-if-cheapest-trip="{dest}:{badge_n}" hidden>Cheapest trip</span></td>'
    )


def build_html(data: dict) -> str:
    fmap = fare_map(data["flights"])
    hmap = hotel_map(data["hotels"])
    pmap = {p["id"]: p for p in data["plans"]}
    rows = []
    order = ["palma", "laspalmas", "maspalomas", "malaga", "barcelona"]
    for dest in order:
        cells = []
        for nights in (1, 2, 3, 7):
            plan = next(
                p for p in data["plans"]
                if p["dest"] == dest and p["nights"] == nights and p["headline"]
            )
            cells.append(compare_cell(plan))
        rows.append(
            f'<tr data-highlight="{dest}"><th scope="row"><a href="#{dest}">{escape(CITY_LABEL[dest])}</a></th>'
            + "".join(cells)
            + "</tr>"
        )
    sections = []
    for dest in DESTS:
        stays = []
        for pid in dest["plans"]:
            extra = dest["extra"].get(pid, "")
            stays.append(stay_block(pmap[pid], fmap, hmap, dest["id"], extra))
        budget_cards = [
            hotel_card(hmap[hid], dest["hotel_used"].get(hid, ""))
            for hid in dest["budget_hotels"]
        ]
        nicer_cards = [
            hotel_card(hmap[hid], dest["hotel_used"].get(hid, ""))
            for hid in dest["nicer_hotels"]
        ]
        nicer_block = ""
        if nicer_cards:
            nicer_block = f"""
        <h3 class="hotels-title">Nicer stay</h3>
        <p class="fine">3–4★ hotels we actually priced. Still a private double — not in the budget totals. Photos are of the city, labelled as such.</p>
        <div class="hotel-grid">
          {''.join(nicer_cards)}
        </div>"""
        else:
            nicer_block = """
        <h3 class="hotels-title">Nicer stay</h3>
        <p class="fine">We did not price 3–4★ rooms for this city. Nothing invented.</p>"""
        sections.append(f"""
    <section class="dest-section dest-{dest['id']}" id="{dest['id']}">
      <div class="container">
        <header class="dest-head">
          <figure class="dest-hero">
            <img src="{escape(dest['photo'], quote=True)}" alt="{escape(dest['photo_alt'])}" width="1600" height="900" loading="lazy">
          </figure>
          <div>
            <p class="kicker">{escape(dest['full'])}</p>
            <h2>{escape(dest['name'])}</h2>
            <p>{escape(dest['lede'])}</p>
          </div>
        </header>
        {''.join(stays)}
        <h3 class="hotels-title">Budget private rooms</h3>
        <p class="fine">Private double rooms for two — hostels, guesthouses, hostales, studios. Never a shared dorm. Totals use the cheapest of these. Photos are of the city, labelled as such. We did not invent hotels or prices.</p>
        <div class="hotel-grid">
          {''.join(budget_cards)}
        </div>
        {nicer_block}
      </div>
    </section>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Our first vacation, together — December 2026</title>
  <meta name="description" content="Ella, a private page for you and Ali: five December cities, the real trip shape, and the numbers we actually checked.">
  <link rel="canonical" href="https://aliattia10.github.io/january-island-choice/">
  <link rel="icon" href="./favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,400;1,9..144,500;1,9..144,600&amp;family=Nunito:ital,wght@0,400;0,600;0,700;1,400&amp;display=swap">
  <link rel="stylesheet" href="./styles.css">
</head>
<body>
  <a class="skip" href="#compare">Skip to the comparison</a>

  <header class="masthead">
    <a class="wordmark" href="./">December, together</a>
    <nav aria-label="On this page">
      <a href="#hello">Hello</a>
      <a href="#compare">Compare</a>
      <a href="#palma">Cities</a>
    </nav>
  </header>

  <section class="hero" aria-label="Cover">
    <figure class="hero-photo">
      <img src="./photos/palma-cathedral.jpg" width="2400" height="1364" alt="Palma Cathedral, La Seu, seen across the water from the harbour" fetchpriority="high">
    </figure>
    <div class="hero-plate">
      <p class="kicker">14 December 2026 – 1 January 2027</p>
      <h1>Our first vacation, together.</h1>
      <p class="lead">Ella, this is the shape of the trip — five cities, one night to a week, one way home to Frankfurt.</p>
      <div class="hero-actions">
        <a class="btn" href="#compare">See the totals</a>
        <a class="btn btn--ghost" href="#hello">How it works</a>
      </div>
    </div>
  </section>

  <nav class="dest-nav" aria-label="Destinations">
    <a href="#palma">Palma</a>
    <a href="#laspalmas">Las Palmas</a>
    <a href="#maspalomas">Maspalomas</a>
    <a href="#malaga">Málaga</a>
    <a href="#barcelona">Barcelona</a>
  </nav>

  <section class="intro" id="hello">
    <div class="container">
      <p class="kicker">For Ella</p>
      <h2>How this trip actually works</h2>
      <p>You fly from Hannover to the city. Ali flies from Oviedo. Trip length is flexible: one night, two, three, or a week. You share a <strong>private double room</strong> for every night in the city — check-in on the day you arrive, check-out on the day you fly together to Asturias. Then two slow days in Asturias at home, no hotel. After that, you fly Asturias (OVD) to Frankfurt (FRA), one way, to go home to Germany. There is no flight back to Hannover. Totals use the cheapest private room we priced. One- and two-night rooms are still a live search — we did not invent a hotel or a price.</p>
      <ol class="shape">
        <li><strong>You</strong> — Hannover (HAJ) → the city.</li>
        <li><strong>Ali</strong> — Oviedo / Asturias (OVD) → the city.</li>
        <li><strong>Hotel</strong> — N nights in a private double for two. Check-in arrival day, check-out the morning you both fly to Asturias.</li>
        <li><strong>Both of you</strong> — the city → Asturias (OVD), two people.</li>
        <li><strong>Two days in Asturias</strong> — at home, no hotel.</li>
        <li><strong>You</strong> — after those days, Asturias (OVD) → Frankfurt (FRA). No December nonstop; the priced options are one-stop, typically via Madrid.</li>
      </ol>
      <p class="aside">This page does not process payment. Snapshot <span data-bind="snapshot">25 November 2026</span>. Hotels last checked <span data-bind="hotels_checked">22 November 2026</span>. Flights are economy, no checked bags. Recheck before you pay. Food, buses, transfers, tickets, bags and insurance are not included. Self-transfers are separate tickets.</p>
    </div>
  </section>

  <section class="compare" id="compare">
    <div class="container">
      <p class="kicker">At a glance</p>
      <h2>Which city is kindest to the budget?</h2>
      <p>A trip total is Ella’s inbound + Ali’s inbound + the shared flight to Asturias (already priced for two) + the cheapest private double for all N city nights + Ella’s Asturias → Frankfurt when we have a verified fare. A missing return or an unpriced room is left out of the number and labelled check live. <strong>Best value</strong> is the cheapest full city stay in that row (room + all three city flights). <strong>Cheapest trip</strong> is the lowest complete total on the page, Frankfurt included when we have it.</p>
      <div class="table-wrap">
        <table class="compare-table">
          <thead>
            <tr>
              <th scope="col">City</th>
              <th scope="col">1 night</th>
              <th scope="col">2 nights</th>
              <th scope="col">3 nights</th>
              <th scope="col">7 nights</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
      <p class="fine" data-bind="cheapestHeadline">Headline cheapest: 3 nights Barcelona with Frankfurt; 7 nights Málaga before Frankfurt.</p>
      <p class="fine">1-night and 2-night columns are the three city flights only. Private-room prices for those dates are still a live Booking search, so they are left out of the number. All 1n/2n returns to Asturias are verified; we did not invent a hotel figure. Prices jump after 22 December, so arriving 14–18 December is the kinder window. 1 USD ≈ 0.86 EUR is approximate, only for the USD hotel cards.</p>
    </div>
  </section>

  {''.join(sections)}

  <footer class="site-foot">
    <div class="container">
      <p>A private page for two people. Ella’s first name is on the buttons because Ali asked. No last names. Photographs are Wikimedia Commons files — credits in <a href="./photos/CREDITS.md">photos/CREDITS.md</a>.</p>
      <p>Live at <a href="https://aliattia10.github.io/january-island-choice/">aliattia10.github.io/january-island-choice</a>. Flight snapshot <span data-bind="snapshot">25 November 2026</span>.</p>
    </div>
  </footer>
  <script src="./app.js" defer></script>
</body>
</html>
"""


def main() -> None:
    data = build_prices()
    (ROOT / "data" / "prices.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (ROOT / "index.html").write_text(build_html(data), encoding="utf-8")
    print("Wrote data/prices.json and index.html")
    for plan in data["plans"]:
        print(plan["id"], "sub", plan.get("subtotal_eur"), "total", plan.get("total_eur"), "complete", plan.get("total_complete"))


if __name__ == "__main__":
    main()
