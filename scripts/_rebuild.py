#!/usr/bin/env python3
"""One-shot rebuild of prices.json + index.html for the six-step itinerary."""

from __future__ import annotations

import base64
import json
import sys
from datetime import date as date_cls
from html import escape
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ella_home_data

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


USD_TO_EUR = 0.911


def euro(n) -> str:
    return f"€{int(n)}"


def euro_night(n) -> str:
    if n is None:
        return ""
    rounded = round(float(n), 2)
    if abs(rounded - round(rounded)) < 1e-9:
        return euro(int(round(rounded)))
    return f"€{rounded:.2f}"


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
    priced = price is not None
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
        "source": "booking",
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
        "checked": "2026-11-22",
        "recheck_live": priced,
    }
    if score is not None:
        item["score"] = score
    if stars is not None:
        item["stars"] = stars
    if id_ in OFFICIAL:
        item["official_url"] = OFFICIAL[id_]
    return item


PHOTO_PALMA_BANO = "https://a0.muscache.com/im/pictures/hosting/Hosting-1660088592494940730/original/d178b13a-ca8c-4c4d-9a08-7709efdaa840.jpeg"
PHOTO_PALMA_BONANY = "https://a0.muscache.com/im/pictures/miso/Hosting-567818665423745418/original/c344d8ff-b634-4a7c-bd19-2aa319e9e3ca.jpeg"
PHOTO_PALMA_ENSUITE = "https://a0.muscache.com/im/pictures/hosting/Hosting-1189630582178272314/original/61fe1c68-535d-4b43-bce5-d8767e07bbcc.jpeg"
PHOTO_LP_ISLETA = "https://a0.muscache.com/im/pictures/ec5d2852-399e-4864-b8af-3c5227783605.jpg"
PHOTO_LP_VEGUETA = "https://a0.muscache.com/im/pictures/4440c882-1eb9-489a-ab9a-b3a85df1159f.jpg"
PHOTO_LP_CANTERAS = "https://a0.muscache.com/im/pictures/BnbProperty/BnbProperty-1715250806937003647/original/4def2dd7-7116-4f58-974f-50749a503c62.jpeg"
PHOTO_LP_LINDA = "https://a0.muscache.com/im/pictures/miso/Hosting-1281183146777399181/original/926c8d95-b4c1-43dc-88c9-20b0819503be.jpeg"
PHOTO_MASP_DESCANSO = "https://a0.muscache.com/im/pictures/prohost-api/Hosting-807751336662960005/original/af678cb8-d75b-4048-89b2-cbe233eea8a5.jpeg"
PHOTO_MASP_RELAX = "https://a0.muscache.com/im/pictures/hosting/Hosting-613764810682076874/original/834ef981-e7ff-43ed-ba13-596c91c14c19.jpeg"
PHOTO_MASP_GOLDEN = "https://a0.muscache.com/im/pictures/BnbProperty/BnbProperty-1789791386166815998/original/30190661-9838-46b1-9010-a6308dc7e5e2.jpeg"
PHOTO_MASP_OASIS = "https://a0.muscache.com/im/pictures/BnbProperty/BnbProperty-1715238920882280449/original/d21e37dd-596e-453a-8380-2a003787356c.jpeg"
PHOTO_AGP_HAB = "https://a0.muscache.com/im/pictures/5b5266e1-7694-450d-8ccd-c5b52c315914.jpg"
PHOTO_AGP_ROSA = "https://a0.muscache.com/im/pictures/BnbProperty/BnbProperty-1715257557710795771/original/5bf61abc-48f9-4a1f-8441-c6e0dea68958.jpeg"


def airbnb(
    id_,
    name,
    dest,
    nights,
    price,
    per_night,
    checkin,
    checkout,
    room_kind,
    url,
    rating=None,
    reviews=None,
    photo_url=None,
    photo_i=0,
):
    photos = PHOTOS[dest]
    src, alt = photos[photo_i % len(photos)]
    city = CITY_LABEL[dest]
    item = {
        "id": id_,
        "name": name,
        "dest": dest,
        "nights": nights,
        "currency": "EUR",
        "price": price,
        "per_night": per_night,
        "price_status": "known",
        "checkin": checkin,
        "checkout": checkout,
        "search_only": False,
        "tier": "airbnb",
        "source": "airbnb",
        "room_type": room_kind,
        "photo": photo_url or src,
        "photo_alt": name if photo_url else alt,
        "photo_caption": (
            "From the Airbnb listing."
            if photo_url
            else f"A photograph of {city}, not the listing."
        ),
        "booking_url": url,
        "airbnb_url": url,
        "checked": "2026-11-27",
        "recheck_live": False,
        "private": True,
    }
    if rating == "new":
        item["rating_label"] = "New listing"
    elif rating is not None:
        item["rating"] = rating
        if reviews is not None:
            item["reviews"] = reviews
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


def pick_stay(plan, hotels, airbnb_for_plan):
    plan["booking_hotel"] = plan["hotel"]
    if plan.get("alt_hotel"):
        plan["booking_alt"] = plan["alt_hotel"]
    ab = list(airbnb_for_plan.get(plan["id"], []))
    plan["airbnb"] = ab
    ids = [plan["hotel"]]
    if plan.get("alt_hotel"):
        ids.append(plan["alt_hotel"])
    ids.extend(ab)
    priced = []
    seen = set()
    for hid in ids:
        if hid in seen:
            continue
        seen.add(hid)
        h = hotels.get(hid)
        if not h:
            continue
        p = hotel_price_eur(h)
        if p is not None:
            priced.append((p, hid))
    priced.sort()
    if priced:
        plan["hotel"] = priced[0][1]
        plan["alt_hotel"] = priced[1][1] if len(priced) > 1 else None


def plan_totals(plan, flights, hotels):
    ella = fare_eur(flights[plan["ella_in"]])
    ali = fare_eur(flights[plan["ali_in"]])
    tog = fare_eur(flights[plan["together"]])
    hotel = hotels[plan["hotel"]]
    room = hotel_price_eur(hotel)
    plan["together_missing"] = tog is None
    plan["hotel_missing"] = room is None
    plan["fra_known"] = False
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
    plan["total_eur"] = sub
    plan["total_complete"] = True
    alt_id = plan.get("alt_hotel")
    if alt_id:
        alt_room = hotel_price_eur(hotels[alt_id])
        if alt_room is not None:
            plan["alt_subtotal_eur"] = ella + ali + tog + alt_room
            plan["alt_total_eur"] = plan["alt_subtotal_eur"]


def build_prices() -> dict:
    flights = [
        flight("haj-pmi-14", "HAJ", "PMI", "2026-12-14", "Eurowings", "07:55", "nonstop", 1, True, True, 63),
        flight("ovd-pmi-14", "OVD", "PMI", "2026-12-14", "Vueling", "08:50", "", 1, False, True, 23),
        flight("pmi-ovd-17", "PMI", "OVD", "2026-12-17", "Vueling", "08:00", "pair for 2 adults", 2, False, True, 68),
        flight("pmi-ovd-21", "PMI", "OVD", "2026-12-21", "Vueling", "06:30", "pair for 2 adults", 2, False, True, 94),
        flight("haj-lpa-16", "HAJ", "LPA", "2026-12-16", "Eurowings", "12:50", "nonstop", 1, True, True, 72),
        flight("ovd-lpa-16", "OVD", "LPA", "2026-12-16", "Air Europa", "", "via Madrid", 1, False, True, 66),
        flight("ovd-lpa-16-binter", "OVD", "LPA", "2026-12-16", "Binter", "", "nonstop alternative, not used in totals", 1, True, True, 186),
        flight("lpa-ovd-19", "LPA", "OVD", "2026-12-19", "Volotea", "18:45", "pair for 2 adults", 2, False, True, 77),
        flight("haj-lpa-15", "HAJ", "LPA", "2026-12-15", "TUI fly", "", "nonstop", 1, True, True, 71),
        flight("ovd-lpa-15", "OVD", "LPA", "2026-12-15", "", "", "his inbound in the 7-night Gran Canaria flight total", 1, False, True, 66),
        flight("lpa-ovd-22", "LPA", "OVD", "2026-12-22", "", "", "pair for 2 adults", 2, False, True, 103),
        flight("haj-agp-15", "HAJ", "AGP", "2026-12-15", "Vueling", "", "1 stop", 1, False, True, 152),
        flight("ovd-agp-15", "OVD", "AGP", "2026-12-15", "Volotea", "", "", 1, False, True, 24),
        flight("agp-ovd-18", "AGP", "OVD", "2026-12-18", "", "", "pair for 2 adults", 2, False, True, 124),
        flight("haj-agp-18", "HAJ", "AGP", "2026-12-18", "Eurowings", "07:10", "nonstop", 1, True, True, 115),
        flight("ovd-agp-18", "OVD", "AGP", "2026-12-18", "Volotea", "", "", 1, False, True, 28),
        flight("agp-ovd-25", "AGP", "OVD", "2026-12-25", "Volotea", "", "pair for 2 adults", 2, False, True, 77),
        flight("haj-bcn-15", "HAJ", "BCN", "2026-12-15", "Vueling", "10:10", "nonstop", 1, True, True, 77),
        flight("ovd-bcn-15", "OVD", "BCN", "2026-12-15", "Vueling", "20:55", "", 1, False, True, 18),
        flight("bcn-ovd-18", "BCN", "OVD", "2026-12-18", "Vueling", "07:20", "pair for 2 adults", 2, False, True, 144),
        flight("bcn-ovd-22", "BCN", "OVD", "2026-12-22", "Air Europa", "", "pair for 2 adults", 2, False, True, 165),
        flight("ovd-fra-19", "OVD", "FRA", "2026-12-19", "Air Europa", "", "1 stop via Madrid. Not in trip totals — see Ella’s flight home.", 1, False, True, 116),
        flight("ovd-fra-20", "OVD", "FRA", "2026-12-20", "Air Europa", "", "1 stop via Madrid. Not in trip totals — see Ella’s flight home.", 1, False, True, 116),
        flight("ovd-fra-21", "OVD", "FRA", "2026-12-21", "Iberia", "13:20", "1 stop via Madrid. Not in trip totals — see Ella’s flight home.", 1, False, True, 71),
        flight("ovd-fra-23", "OVD", "FRA", "2026-12-23", "Air Europa", "", "1 stop via Madrid. Not in trip totals — see Ella’s flight home.", 1, False, True, 62),
        flight("ovd-fra-24", "OVD", "FRA", "2026-12-24", "Air Europa", "10:35", "1 stop via Madrid. Not in trip totals — see Ella’s flight home.", 1, False, True, 62),
        flight("ovd-fra-27", "OVD", "FRA", "2026-12-27", "Air Europa", "", "1 stop via Madrid. Not in trip totals — see Ella’s flight home.", 1, False, True, 62),
        flight("ovd-fra-17", "OVD", "FRA", "2026-12-17", "Air Europa", "10:35", "1 stop via Madrid. Not in trip totals — see Ella’s flight home.", 1, False, True, 91),
        flight("ovd-fra-18", "OVD", "FRA", "2026-12-18", "Air Europa", "", "1 stop via Madrid. Not in trip totals — see Ella’s flight home.", 1, False, True, 116),
        flight("ovd-fra-22", "OVD", "FRA", "2026-12-22", "Air Europa", "", "1 stop via Madrid. Not in trip totals — see Ella’s flight home.", 1, False, True, 116),
        flight("pmi-ovd-15", "PMI", "OVD", "2026-12-15", "", "", "pair for 2 adults, 1 stop", 2, False, True, 106),
        flight("pmi-ovd-16", "PMI", "OVD", "2026-12-16", "", "", "pair for 2 adults, 1 stop", 2, False, True, 106),
        flight("lpa-ovd-17", "LPA", "OVD", "2026-12-17", "", "", "pair for 2 adults, 1 stop", 2, False, True, 210),
        flight("lpa-ovd-18", "LPA", "OVD", "2026-12-18", "", "", "pair for 2 adults, 1 stop", 2, False, True, 316),
        flight("agp-ovd-19", "AGP", "OVD", "2026-12-19", "", "", "pair for 2 adults, 1 stop", 2, False, True, 154),
        flight("agp-ovd-20", "AGP", "OVD", "2026-12-20", "", "", "pair for 2 adults, 1 stop", 2, False, True, 133),
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
        airbnb("ab-palma-bano-1", "Habitacion con bano privado, Palma", "palma", 1, 63, 63, "2026-12-14", "2026-12-15", "private room, private bath", "https://www.airbnb.com/rooms/1660088592494940730?check_in=2026-12-14&check_out=2026-12-15&adults=2&currency=EUR", 4.5, 22, PHOTO_PALMA_BANO, 0),
        airbnb("ab-palma-bonany-1", "Hostal Bonany, double A/C + pool", "palma", 1, 76, 76, "2026-12-14", "2026-12-15", "private room", "https://www.airbnb.com/rooms/567818665423745418?check_in=2026-12-14&check_out=2026-12-15&adults=2&currency=EUR", 4.73, 236, PHOTO_PALMA_BONANY, 1),
        airbnb("ab-palma-bano-2", "Habitacion con bano privado", "palma", 2, 125, 62.50, "2026-12-14", "2026-12-16", "private room", "https://www.airbnb.com/rooms/1660088592494940730?check_in=2026-12-14&check_out=2026-12-16&adults=2&currency=EUR", 4.5, 22, PHOTO_PALMA_BANO, 0),
        airbnb("ab-palma-bonany-2", "Hostal Bonany", "palma", 2, 151, 75.50, "2026-12-14", "2026-12-16", "private room", "https://www.airbnb.com/rooms/567818665423745418?check_in=2026-12-14&check_out=2026-12-16&adults=2&currency=EUR", 4.73, 236, PHOTO_PALMA_BONANY, 1),
        airbnb("ab-palma-bano-3", "Habitacion con bano privado", "palma", 3, 187, 62.33, "2026-12-14", "2026-12-17", "private room", "https://www.airbnb.com/rooms/1660088592494940730?check_in=2026-12-14&check_out=2026-12-17&adults=2&currency=EUR", 4.5, 22, PHOTO_PALMA_BANO, 0),
        airbnb("ab-palma-bonany-3", "Hostal Bonany", "palma", 3, 226, 75.33, "2026-12-14", "2026-12-17", "private room", "https://www.airbnb.com/rooms/567818665423745418?check_in=2026-12-14&check_out=2026-12-17&adults=2&currency=EUR", 4.73, 236, PHOTO_PALMA_BONANY, 1),
        airbnb("ab-palma-bano-7", "Habitacion con bano privado", "palma", 7, 435, 62.14, "2026-12-14", "2026-12-21", "private room", "https://www.airbnb.com/rooms/1660088592494940730?check_in=2026-12-14&check_out=2026-12-21&adults=2&currency=EUR", 4.5, 22, PHOTO_PALMA_BANO, 0),
        airbnb("ab-palma-ensuite-7", "Habitacion en suite con balcon privado", "palma", 7, 589, 84.14, "2026-12-14", "2026-12-21", "private ensuite, double bed", "https://www.airbnb.com/rooms/1189630582178272314?check_in=2026-12-14&check_out=2026-12-21&adults=2&currency=EUR", 4.85, 53, PHOTO_PALMA_ENSUITE, 2),
        airbnb("ab-lp-isleta-1", "La Casa De La Isleta, private bath", "laspalmas", 1, 48, 48, "2026-12-16", "2026-12-17", "private room, queen", "https://www.airbnb.com/rooms/49125025?check_in=2026-12-16&check_out=2026-12-17&adults=2&currency=EUR", 4.73, 203, PHOTO_LP_ISLETA, 0),
        airbnb("ab-lp-vegueta-1", "Vacacional Vegueta II", "laspalmas", 1, 75, 75, "2026-12-16", "2026-12-17", "entire apt", "https://www.airbnb.com/rooms/26576543?check_in=2026-12-16&check_out=2026-12-17&adults=2&currency=EUR", 4.48, 29, PHOTO_LP_VEGUETA, 1),
        airbnb("ab-lp-rose-2", "Dona Rose room", "laspalmas", 2, 110, 55, "2026-12-16", "2026-12-18", "private room in shared house", "https://www.airbnb.com/rooms/649728177997271973?check_in=2026-12-16&check_out=2026-12-18&adults=2&currency=EUR", 4.55, 31, None, 0),
        airbnb("ab-lp-brocante-2", "Apartamento de Brocante 209", "laspalmas", 2, 140, 70, "2026-12-16", "2026-12-18", "entire apt", "https://www.airbnb.com/rooms/43818149?check_in=2026-12-16&check_out=2026-12-18&adults=2&currency=EUR", 4.64, 151, None, 1),
        airbnb("ab-lp-canteras-3", "Las Canteras, Estudio 07", "laspalmas", 3, 183, 61, "2026-12-16", "2026-12-19", "entire studio", "https://www.airbnb.com/rooms/1329455057515605400?check_in=2026-12-16&check_out=2026-12-19&adults=2&currency=EUR", 4.2, 54, PHOTO_LP_CANTERAS, 0),
        airbnb("ab-lp-linda-3", "La Isleta Linda", "laspalmas", 3, 203, 67.67, "2026-12-16", "2026-12-19", "entire place", "https://www.airbnb.com/rooms/1281183146777399181?check_in=2026-12-16&check_out=2026-12-19&adults=2&currency=EUR", 5.0, 7, PHOTO_LP_LINDA, 2),
        airbnb("ab-lp-loft-7", "Loft 25, Las Canteras", "laspalmas", 7, 446, 63.71, "2026-12-15", "2026-12-22", "entire loft", "https://www.airbnb.com/rooms/18480977?check_in=2026-12-15&check_out=2026-12-22&adults=2&currency=EUR", 4.64, 342, None, 0),
        airbnb("ab-lp-mindfit-7", "MindFit Holidays 2D Eclipse", "laspalmas", 7, 474, 67.71, "2026-12-15", "2026-12-22", "entire apt", "https://www.airbnb.com/rooms/1183937454852677557?check_in=2026-12-15&check_out=2026-12-22&adults=2&currency=EUR", 4.42, 331, None, 1),
        airbnb("ab-masp-descanso-2", "Un descanso 1", "maspalomas", 2, 148, 74, "2026-12-16", "2026-12-18", "entire apt", "https://www.airbnb.com/rooms/807751336662960005?check_in=2026-12-16&check_out=2026-12-18&adults=2&currency=EUR", 4.32, 50, PHOTO_MASP_DESCANSO, 0),
        airbnb("ab-masp-relax-2", "Relax Playa Ingles", "maspalomas", 2, 168, 84, "2026-12-16", "2026-12-18", "entire apt", "https://www.airbnb.com/rooms/613764810682076874?check_in=2026-12-16&check_out=2026-12-18&adults=2&currency=EUR", 4.92, 24, PHOTO_MASP_RELAX, 1),
        airbnb("ab-masp-camara-3", "Camara de la pasion (San Bartolome de Tirajana)", "maspalomas", 3, 190, 63.33, "2026-12-16", "2026-12-19", "private room", "https://www.airbnb.com/rooms/1434866096222916233?check_in=2026-12-16&check_out=2026-12-19&adults=2&currency=EUR", 4.85, 26, None, 0),
        airbnb("ab-masp-golden-3", "Apartamentos Golden Views", "maspalomas", 3, 248, 82.67, "2026-12-16", "2026-12-19", "entire apt (new)", "https://www.airbnb.com/rooms/1789799526109375250?check_in=2026-12-16&check_out=2026-12-19&adults=2&currency=EUR", "new", None, PHOTO_MASP_GOLDEN, 1),
        airbnb("ab-masp-apto-7", "Apartamento de 1 habitacion", "maspalomas", 7, 523, 74.71, "2026-12-15", "2026-12-22", "entire apt (new)", "https://www.airbnb.com/rooms/1790031823493057261?check_in=2026-12-15&check_out=2026-12-22&adults=2&currency=EUR", "new", None, None, 2),
        airbnb("ab-masp-oasis-7", "Green Oasis Bungalow 1207", "maspalomas", 7, 592, 84.57, "2026-12-15", "2026-12-22", "entire bungalow", "https://www.airbnb.com/rooms/735909769349166270?check_in=2026-12-15&check_out=2026-12-22&adults=2&currency=EUR", 4.9, 10, PHOTO_MASP_OASIS, 0),
        airbnb("ab-agp-hab-1", "Habitacion privada 1", "malaga", 1, 39, 39, "2026-12-18", "2026-12-19", "private room", "https://www.airbnb.com/rooms/7599041?check_in=2026-12-18&check_out=2026-12-19&adults=2&currency=EUR", 4.81, 671, PHOTO_AGP_HAB, 0),
        airbnb("ab-agp-rosa-1", "Apartamentos de Rosa Mari", "malaga", 1, 68, 68, "2026-12-18", "2026-12-19", "entire apt", "https://www.airbnb.com/rooms/1209985226467887125?check_in=2026-12-18&check_out=2026-12-19&adults=2&currency=EUR", 4.89, 1330, PHOTO_AGP_ROSA, 1),
        airbnb("ab-agp-suenos-2", "Despierta con tus suenos, near centre", "malaga", 2, 116, 58, "2026-12-18", "2026-12-20", "private room", "https://www.airbnb.com/rooms/29984735?check_in=2026-12-18&check_out=2026-12-20&adults=2&currency=EUR", 4.8, 92, None, 0),
        airbnb("ab-agp-druida-2", "La Casa del Druida, Apt hierbabuena", "malaga", 2, 132, 66, "2026-12-18", "2026-12-20", "entire apt", "https://www.airbnb.com/rooms/27363966?check_in=2026-12-18&check_out=2026-12-20&adults=2&currency=EUR", 4.6, 872, None, 1),
        airbnb("ab-agp-rosa-3", "Apartamentos de Rosa Mari", "malaga", 3, 149, 49.67, "2026-12-15", "2026-12-18", "entire apt", "https://www.airbnb.com/rooms/1209985226467887125?check_in=2026-12-15&check_out=2026-12-18&adults=2&currency=EUR", 4.89, 1330, PHOTO_AGP_ROSA, 1),
        airbnb("ab-agp-rosa-7", "Apartamentos de Rosa Mari", "malaga", 7, 431, 61.57, "2026-12-18", "2026-12-25", "entire apt", "https://www.airbnb.com/rooms/1691362913350835895?check_in=2026-12-18&check_out=2026-12-25&adults=2&currency=EUR", 4.89, 1330, PHOTO_AGP_ROSA, 1),
        airbnb("ab-bcn-rambla-1", "Centro, near Rambla de Catalunya", "barcelona", 1, 45, 45, "2026-12-15", "2026-12-16", "private room", "https://www.airbnb.com/rooms/1770350867264593321?check_in=2026-12-15&check_out=2026-12-16&adults=2&currency=EUR", 4.67, 9, None, 0),
        airbnb("ab-bcn-silvia-1", "Estudios de Silvia (Barcelona Fifteen)", "barcelona", 1, 71, 71, "2026-12-15", "2026-12-16", "entire studio", "https://www.airbnb.com/rooms/19955807?check_in=2026-12-15&check_out=2026-12-16&adults=2&currency=EUR", 4.47, 799, None, 1),
        airbnb("ab-bcn-rambla-2", "Centro, near Rambla de Catalunya", "barcelona", 2, 90, 45, "2026-12-15", "2026-12-17", "private room", "https://www.airbnb.com/rooms/1770350867264593321?check_in=2026-12-15&check_out=2026-12-17&adults=2&currency=EUR", 4.67, 9, None, 0),
        airbnb("ab-bcn-fifteen-2", "Barcelona Fifteen studios", "barcelona", 2, 151, 75.50, "2026-12-15", "2026-12-17", "entire studio", "https://www.airbnb.com/rooms/14020724?check_in=2026-12-15&check_out=2026-12-17&adults=2&currency=EUR", 4.47, 1234, None, 1),
        airbnb("ab-bcn-centre-3", "Centre, 7 blocks from La Rambla, private bath", "barcelona", 3, 135, 45, "2026-12-15", "2026-12-18", "private room", "https://www.airbnb.com/rooms/1787632500437078315?check_in=2026-12-15&check_out=2026-12-18&adults=2&currency=EUR", 4.44, 9, None, 2),
        airbnb("ab-bcn-sagrada-3", "Private room near Sagrada Familia", "barcelona", 3, 162, 54, "2026-12-15", "2026-12-18", "private room", "https://www.airbnb.com/rooms/1750175914325689796?check_in=2026-12-15&check_out=2026-12-18&adults=2&currency=EUR", 4.82, 11, None, 0),
        airbnb("ab-bcn-terraza-7", "Precioso apartamento, terraza doble, A/C", "barcelona", 7, 480, 68.57, "2026-12-15", "2026-12-22", "entire apt", "https://www.airbnb.com/rooms/44060722?check_in=2026-12-15&check_out=2026-12-22&adults=2&currency=EUR", 4.44, 166, None, 1),
        airbnb("ab-bcn-fabrica-7", "La Fabrica &Co, studio double bed", "barcelona", 7, 550, 78.57, "2026-12-15", "2026-12-22", "entire studio", "https://www.airbnb.com/rooms/1157033654900525674?check_in=2026-12-15&check_out=2026-12-22&adults=2&currency=EUR", 4.85, 205, None, 2),
    ]

    airbnb_for_plan = {
        "palma-1": ["ab-palma-bano-1", "ab-palma-bonany-1"],
        "palma-2": ["ab-palma-bano-2", "ab-palma-bonany-2"],
        "palma-3": ["ab-palma-bano-3", "ab-palma-bonany-3"],
        "palma-7": ["ab-palma-bano-7", "ab-palma-ensuite-7"],
        "lp-1": ["ab-lp-isleta-1", "ab-lp-vegueta-1"],
        "lp-2": ["ab-lp-rose-2", "ab-lp-brocante-2"],
        "lp-3": ["ab-lp-canteras-3", "ab-lp-linda-3"],
        "lp-7": ["ab-lp-loft-7", "ab-lp-mindfit-7"],
        "masp-1": [],
        "masp-2": ["ab-masp-descanso-2", "ab-masp-relax-2"],
        "masp-3": ["ab-masp-camara-3", "ab-masp-golden-3"],
        "masp-7": ["ab-masp-apto-7", "ab-masp-oasis-7"],
        "malaga-1": ["ab-agp-hab-1", "ab-agp-rosa-1"],
        "malaga-2": ["ab-agp-suenos-2", "ab-agp-druida-2"],
        "malaga-3": ["ab-agp-rosa-3"],
        "malaga-7": ["ab-agp-rosa-7"],
        "bcn-1": ["ab-bcn-rambla-1", "ab-bcn-silvia-1"],
        "bcn-2": ["ab-bcn-rambla-2", "ab-bcn-fifteen-2"],
        "bcn-3": ["ab-bcn-centre-3", "ab-bcn-sagrada-3"],
        "bcn-7": ["ab-bcn-terraza-7", "ab-bcn-fabrica-7"],
    }

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

    hlookup = {h["id"]: h for h in hotels}
    for plan in plans:
        plan["flights"] = [plan["ella_in"], plan["ali_in"], plan["together"]]
        pick_stay(plan, hlookup, airbnb_for_plan)

    data = {
        "snapshot": "2026-11-27",
        "hotels_checked": "2026-11-22",
        "rooms_checked": "2026-11-27",
        "home_flights_checked": "2026-11-27",
        "usd_to_eur": USD_TO_EUR,
        "ella_home": ella_home_data.payload(gf),
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
            "itinerary": "Ella HAJ→city; Ali OVD→city; private stay for all N city nights (1, 2, 3 or 7); both city→OVD (2 adults, stored as a pair); days in Asturias at home (no hotel); Ella flies home whenever she chooses. Trip totals do not include her flight home. Totals use the cheapest verified private option (Airbnb 27 Nov vs Booking 22 Nov). Never a shared room.",
            "ovd_fra": "Home flights are listed separately under ella_home. No December nonstop from Oviedo. OVD→FRA 17 Dec €91, 18–20 Dec €116, 21 Dec €71 Iberia, 22 Dec €116, 23–31 Dec €62. Rechecked 27 Nov 2026.",
            "needs_check": [
                "Maspalomas 1n 16–17 Dec: no Airbnb in town within €35–85. Booking search and Google Hotels Axel Beach ~€161. Same LPA flights as Las Palmas 1n.",
                "Booking.com hotel euro prices: last checked 22 Nov 2026, could not re-verify 27 Nov — recheck live.",
                "ALSA buses Gijón→BIO/SDR for Ella’s home flight: mid-December tickets not live-verified.",
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
        notes.append("plus the shared flight to Asturias (check live)")
    if plan.get("hotel_missing"):
        notes.append("plus the private room (check live)")
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
    stay = hmap[plan["hotel"]]
    search_city = {
        "palma": "Palma",
        "maspalomas": "Maspalomas",
        "laspalmas": "Las Palmas",
        "malaga": "Málaga",
        "barcelona": "Barcelona",
    }[dest_id]
    city_search = booking(search_city, stay["checkin"], stay["checkout"], kind="private")
    extra_btns = []
    if stay.get("source") == "airbnb":
        extra_btns.append(
            f'<a class="book-link book-link--airbnb" href="{escape(stay["airbnb_url"], quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">Book on Airbnb</a>'
        )
    booking_id = plan.get("booking_hotel")
    booking_h = hmap.get(booking_id) if booking_id else None
    see_hotel = stay if stay.get("source") != "airbnb" else booking_h
    if see_hotel and not see_hotel.get("search_only"):
        hotel_href = see_hotel.get("official_url") or see_hotel["booking_url"]
        extra_btns.append(
            f'<a class="book-link book-link--hotel" href="{escape(hotel_href, quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">See hotel</a>'
        )
    extra_html = "\n          ".join(extra_btns)
    return f"""
        <div class="book-grid">
          <a class="book-link book-link--ella" href="{escape(ella['gf_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Ella: Hannover → {escape(city)}</a>
          <a class="book-link book-link--ali" href="{escape(ali['gf_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Ali: Oviedo → {escape(city)}</a>
          <a class="book-link book-link--together" href="{escape(tog['gf_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Together: {escape(city)} → Asturias (2 people)</a>
          <a class="book-link book-link--home" href="#ella-home">Ella: pick your flight home</a>
          {extra_html}
          <a class="book-link book-link--search" href="{escape(city_search, quote=True)}" target="_blank" rel="noopener noreferrer">Search private rooms for two, {escape(CITY_LABEL[dest_id])}</a>
        </div>"""


def stay_block(plan, fmap, hmap, dest_id, extra_html=""):
    ella = fmap[plan["ella_in"]]
    ali = fmap[plan["ali_in"]]
    tog = fmap[plan["together"]]
    hotel = hmap[plan["hotel"]]
    nights_word = NIGHTS_WORD.get(plan["nights"], f"{plan['nights']} nights")
    total_bind = f'data-bind="p:{plan["id"]}:display"'
    sub_bind = f'data-bind="p:{plan["id"]}:sub"'
    alt = ""
    if plan.get("alt_hotel"):
        ah = hmap[plan["alt_hotel"]]
        alt_price = euro(ah["price"]) if ah["currency"] == "EUR" else f"${ah['price']}"
        alt_tot = display_plan({"total_complete": plan.get("total_complete") and plan.get("alt_total_eur") is not None, "total_eur": plan.get("alt_total_eur"), "subtotal_eur": plan.get("alt_subtotal_eur")})
        if ah.get("source") == "airbnb":
            src_note = "Airbnb, fees included, 27 November"
        elif ah.get("recheck_live"):
            src_note = "Booking.com, 22 November — recheck live"
        else:
            src_note = "priced option"
        alt_nights = "1 night" if ah["nights"] == 1 else f'{ah["nights"]} nights'
        alt = (
            f'<p class="alt-stay">Other private stay we priced: {escape(ah["name"])} at '
            f'<span data-bind="h:{ah["id"]}">{alt_price}</span> for the same {alt_nights} '
            f'({pretty(ah["checkin"])} – {pretty(ah["checkout"])}; {src_note}). '
            f'That trip is about <span data-bind="p:{plan["id"]}:alt">{escape(alt_tot)}</span>.</p>'
        )
    hotel_nights_label = "1 night" if plan["nights"] == 1 else f"{plan['nights']} nights"
    if hotel.get("source") == "airbnb":
        hotel_price_html = f'<span data-bind="h:{hotel["id"]}">{euro(hotel["price"])}</span>'
        hotel_who = escape(hotel["name"])
        stay_copy = (
            f"Private stay for two at {hotel_who} ({escape(hotel['room_type'])}). "
            f"Airbnb, fees included, checked <span data-bind=\"rooms_checked\">27 November 2026</span>. "
            f"Check-in on the day you arrive, check-out on the day you fly together to Asturias. "
            f"<strong>{hotel_price_html}</strong> for {hotel_nights_label} (2 adults). "
            f"The trip total uses this price. Booking hotel figures below were last checked "
            f"<span data-bind=\"hotels_checked\">22 November 2026</span> and need a live recheck. Never a shared room."
        )
        hotel_line = (
            f"Stay: {hotel_nights_label}, check-in {pretty(hotel['checkin'])}, "
            f"check-out {pretty(hotel['checkout'])}"
        )
        kicker = f"Airbnb · {nights_word}"
    elif hotel.get("price") is None or hotel.get("price_status") == "check_live":
        hotel_price_html = f'<span data-bind="h:{hotel["id"]}">check live price</span>'
        stay_copy = (
            f"No Airbnb in the €35–85 band for these dates, and no stored Booking fare — "
            f"a private-room search only (we did not invent a price). "
            f"<strong>{hotel_price_html}</strong> for {hotel_nights_label}. "
            f"Booking last checked <span data-bind=\"hotels_checked\">22 November 2026</span>. Never a shared dorm."
        )
        hotel_line = (
            f"Hotel: {hotel_nights_label}, check-in {pretty(hotel['checkin'])}, "
            f"check-out {pretty(hotel['checkout'])}"
        )
        kicker = f"Budget private room · {nights_word}"
    elif hotel.get("search_only"):
        hotel_price_html = f'<span data-bind="h:{hotel["id"]}">{euro(hotel["price"])}</span>'
        stay_copy = (
            f"A south-coast private-room search (not a named property). "
            f"<strong>{hotel_price_html}</strong> for {hotel_nights_label} (2 adults, 1 room). "
            f"Booking last checked <span data-bind=\"hotels_checked\">22 November 2026</span> — recheck live, before about 10% tax. Never a shared dorm."
        )
        hotel_line = (
            f"Hotel: {hotel_nights_label}, check-in {pretty(hotel['checkin'])}, "
            f"check-out {pretty(hotel['checkout'])}"
        )
        kicker = f"Budget private room · {nights_word}"
    elif hotel.get("currency") == "EUR":
        hotel_price_html = f'<span data-bind="h:{hotel["id"]}">{euro(hotel["price"])}</span>'
        stay_copy = (
            f"Private double room for two at {escape(hotel['name'])}. "
            f"Check-in on the day you arrive, check-out on the day you fly together to Asturias. "
            f"<strong>{hotel_price_html}</strong> for {hotel_nights_label} (2 adults, 1 room). "
            f"Booking.com, checked <span data-bind=\"hotels_checked\">22 November 2026</span> — recheck live, before about 10% tax. "
            f"Cheaper than the Airbnb options we priced today. Never a shared dorm."
        )
        hotel_line = (
            f"Hotel: {hotel_nights_label}, check-in {pretty(hotel['checkin'])}, "
            f"check-out {pretty(hotel['checkout'])}"
        )
        kicker = f"Budget private room · {nights_word}"
    else:
        hotel_price_html = "check live price"
        stay_copy = f"Private double at {escape(hotel['name'])}. <strong>{hotel_price_html}</strong>."
        hotel_line = (
            f"Hotel: {hotel_nights_label}, check-in {pretty(hotel['checkin'])}, "
            f"check-out {pretty(hotel['checkout'])}"
        )
        kicker = f"Budget private room · {nights_word}"
    airbnb_cards = [
        hotel_card(
            hmap[hid],
            "Used in the trip total." if hid == plan["hotel"] else "Airbnb option for these dates.",
        )
        for hid in plan.get("airbnb") or []
    ]
    airbnb_block = ""
    if airbnb_cards:
        airbnb_block = f"""
        <h4 class="hotels-title">Airbnb for these dates</h4>
        <p class="fine">Private rooms and whole places only — never a shared room. Stay totals from airbnb.es on <span data-bind="rooms_checked">27 November 2026</span>, fees included, 2 adults.</p>
        <div class="hotel-grid">
          {''.join(airbnb_cards)}
        </div>"""
    return f"""
      <article class="stay" id="{escape(plan['id'])}">
        <header class="stay-head">
          <p class="kicker">{escape(kicker)}</p>
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
              <p>{stay_copy}</p>
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
              <h4>Days in Asturias, at home</h4>
              <p>Slow days together after the city. No hotel — you stay at home. Stay as long as you like; Ali is happy if you stay longer.</p>
            </div>
          </li>
          <li>
            <span class="step-n">6</span>
            <div>
              <h4>Ella flies home whenever she chooses</h4>
              <p>This trip total does not include your flight home, so you can pick the day. Window 17 December 2026 – 4 January 2027. See <a href="#ella-home">Ella’s flight home</a> for the options we opened.</p>
            </div>
          </li>
        </ol>
        {airbnb_block}
        {alt}
        {extra_html}
        <p class="stay-total">Trip total: <strong {total_bind}>{escape(display_plan(plan))}</strong>. City flights plus the room: <span {sub_bind}>{euro(plan['subtotal_eur'] if plan.get('subtotal_eur') is not None else plan.get('partial_eur')) if (plan.get('subtotal_eur') is not None or plan.get('partial_eur') is not None) else '—'}</span>. Does not include Ella’s flight home — she picks that separately. Totals never invent a missing city flight or hotel figure.</p>
        {buttons(plan, fmap, hmap, dest_id)}
      </article>"""


def hotel_card(h, used_in=""):
    meta = []
    if h.get("stars"):
        meta.append(f'{h["stars"]}★')
    if h.get("score") is not None:
        meta.append(f'score {h["score"]}')
    if h.get("rating_label"):
        meta.append(h["rating_label"])
    elif h.get("rating") is not None:
        rating_bit = f'{h["rating"]}'
        if h.get("reviews") is not None:
            rating_bit += f' ({h["reviews"]})'
        meta.append(rating_bit)
    nights_label = "1 night" if h["nights"] == 1 else f"{h['nights']} nights"
    if h.get("source") == "airbnb":
        nights_line = (
            f"Stay: {nights_label}, check-in {pretty(h['checkin'])}, "
            f"check-out {pretty(h['checkout'])}"
        )
        price = f'<p class="hotel-price" data-bind="h:{h["id"]}">{euro(h["price"])}</p>'
        night_bit = f'{euro_night(h.get("per_night"))} per night'
        approx = (
            f'<p class="hotel-approx">EUR stay total, Airbnb, fees included, 2 adults. '
            f"{night_bit}. Checked 27 November 2026.</p>"
        )
        see = h["airbnb_url"]
        see_label = "Book on Airbnb"
        btn_class = "book-link book-link--airbnb"
        tier = "Airbnb"
        room_label = h.get("room_type") or "private stay"
        card_mod = "airbnb"
    else:
        nights_line = (
            f"Hotel: {nights_label}, check-in {pretty(h['checkin'])}, "
            f"check-out {pretty(h['checkout'])}"
        )
        if h["currency"] == "USD":
            price = f'<p class="hotel-price" data-bind="usd:{h["id"]}">${int(h["price"])}</p>'
            approx = (
                f'<p class="hotel-approx">USD as returned. About '
                f'<span data-bind="usdapprox:{h["id"]}">{euro(round(h["price"] * USD_TO_EUR))}</span> '
                f"at 1 USD ≈ {USD_TO_EUR} EUR. Recheck live.</p>"
            )
        elif h.get("price") is None or h.get("price_status") == "check_live":
            price = f'<p class="hotel-price" data-bind="h:{h["id"]}">check live price</p>'
            approx = '<p class="hotel-approx">No stored Booking fare — open the private-room search. We did not invent a price.</p>'
        else:
            price = f'<p class="hotel-price" data-bind="h:{h["id"]}">{euro(h["price"])}</p>'
            approx = '<p class="hotel-approx">EUR, Booking.com, checked 22 November 2026 — recheck live. Before about 10% tax. Total for those nights, not per night.</p>'
        see = h.get("official_url") or h["booking_url"]
        see_label = "See hotel" if not h.get("search_only") else "Search private rooms for two"
        btn_class = "book-link book-link--hotel"
        tier = "Nicer stay" if h.get("tier") == "nicer" else "Budget private room"
        room_label = "Private double room"
        card_mod = h.get("tier") or "budget"
    used = f'<p class="hotel-used">{escape(used_in)}</p>' if used_in else ""
    name = h["name"]
    if h["id"] == "masp-south-7":
        name = "Maspalomas south-coast search"
    meta_bits = meta + [room_label]
    return f"""
        <article class="hotel-card hotel-card--{escape(card_mod)}">
          <figure>
            <img src="{escape(h['photo'], quote=True)}" alt="{escape(h['photo_alt'])}" width="800" height="520" loading="lazy">
            <figcaption>{escape(h['photo_caption'])}</figcaption>
          </figure>
          <div class="hotel-body">
            <p class="room-badge">{escape(tier)} · {escape(room_label)}</p>
            <h3>{escape(name)}</h3>
            <p class="hotel-meta">{escape(' · '.join(meta_bits))}</p>
            <p class="hotel-nights">{escape(nights_line)}</p>
            {price}
            {approx}
            {used}
            <a class="{btn_class}" href="{escape(see, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(see_label)}</a>
          </div>
        </article>"""


DESTS = [
    {
        "id": "palma",
        "name": "Palma",
        "full": "Palma, Mallorca",
        "photo": "./photos/palma-cathedral.jpg",
        "photo_alt": "Palma Cathedral, La Seu, seen across the water from the harbour",
        "lede": "Gold stone, winter sea, and a compact old town you can walk. Cheapest verified stays: an Airbnb private room for one, two, three nights and a week. Booking hotels from 22 November are still listed — recheck live.",
        "plans": ["palma-1", "palma-2", "palma-3", "palma-7"],
        "budget_hotels": ["palma-priv-1", "palma-priv-2", "brick-palma-3", "bonany-palma-3", "hesperia-palma-7", "bonany-palma-7"],
        "nicer_hotels": ["nou-baleares"],
        "hotel_used": {
            "palma-priv-1": "One-night Booking search for 14–15 December. No stored Booking fare — Airbnb is on the stay above.",
            "palma-priv-2": "Two-night Booking search for 14–16 December. No stored Booking fare — Airbnb is on the stay above.",
            "brick-palma-3": "Booking.com private room for three nights, checked 22 November — recheck live. Airbnb was cheaper.",
            "bonany-palma-3": "Booking.com private room for three nights, checked 22 November — recheck live.",
            "nou-baleares": "Nicer 4★ pick, USD, not in the euro total.",
            "hesperia-palma-7": "Booking.com week, checked 22 November — recheck live. Airbnb was cheaper.",
            "bonany-palma-7": "Booking.com week, checked 22 November — recheck live.",
        },
        "extra": {
            "palma-1": '<p class="fine">Best inbound alignment: both arrive 14 December (Ella’s Eurowings nonstop). Hotels for one night (Google Hotels, taxes included, 1 USD ≈ 0.911 EUR): <a href="https://www.google.com/travel/hotels/entity/ChgIs8fDpOumy_DmARoLL2cvMXRqMmYwamIQAQ?checkin=2026-12-14&amp;checkout=2026-12-15&amp;adults=2&amp;curr=EUR" target="_blank" rel="noopener noreferrer">Hotel Joan Miro Museum</a> about €68; <a href="https://www.google.com/travel/hotels/entity/ChkI1Or1xO_I6N42Gg0vZy8xMXN2NTc3NXltEAE?checkin=2026-12-14&amp;checkout=2026-12-15&amp;adults=2&amp;curr=EUR" target="_blank" rel="noopener noreferrer">Belle Marivent Boutique Hotel</a> about €75. Display only — not in the trip total.</p>',
            "palma-2": '<p class="fine">Same 14 December inbounds as the one-night plan.</p>',
            "palma-7": '<p class="fine">Home to Asturias on 21 December is Vueling 06:30 — an early start.</p>',
        },
    },
    {
        "id": "laspalmas",
        "name": "Las Palmas",
        "full": "Las Palmas, Gran Canaria city",
        "photo": "./photos/laspalmas-canteras.jpg",
        "photo_alt": "Las Canteras beach with the Alfredo Kraus auditorium at the far end",
        "lede": "A real city with a long beach. Same Gran Canaria flights as Maspalomas — airport LPA. Cheapest verified stays: Airbnb for one, two nights and a week; Booking’s La Isleta Linda studio still wins three nights (22 November — recheck live).",
        "plans": ["lp-1", "lp-2", "lp-3", "lp-7"],
        "budget_hotels": ["lp-priv-1", "lp-priv-2", "isleta-lp-3", "canaria-lp-3", "vegueta-lp-7", "canaria-lp-7"],
        "nicer_hotels": ["matilde-lp", "cordial-galdos", "ac-gran-canaria"],
        "hotel_used": {
            "lp-priv-1": "One-night Booking search for 16–17 December. No stored Booking fare — Airbnb is on the stay above.",
            "lp-priv-2": "Two-night Booking search for 16–18 December. No stored Booking fare — Airbnb is on the stay above.",
            "isleta-lp-3": "Cheapest verified private stay for three nights — used in the total. Booking.com, 22 November — recheck live.",
            "canaria-lp-3": "Booking.com private room for three nights, checked 22 November — recheck live.",
            "matilde-lp": "Nicer 3★ pick, USD, not in the euro total.",
            "cordial-galdos": "Nicer 4★ pick, USD, not in the euro total.",
            "ac-gran-canaria": "Nicer 4★ pick, USD, not in the euro total.",
            "vegueta-lp-7": "Booking.com week, checked 22 November — recheck live. Airbnb was cheaper.",
            "canaria-lp-7": "Booking.com week, checked 22 November — recheck live.",
        },
        "extra": {
            "lp-1": '<p class="fine">Uses Ella’s <span data-bind="f:haj-lpa-16">€72</span> nonstop on 16 December. The 17 December flight home for two is dearer than the 19 December three-night return. Hotels for one night (Google Hotels): <a href="https://www.google.com/travel/hotels/entity/ChkI55fevZql9bNDGg0vZy8xMXA5bnowM2M1EAE?checkin=2026-12-16&amp;checkout=2026-12-17&amp;adults=2&amp;curr=EUR" target="_blank" rel="noopener noreferrer">Alma Canaria Apartments &amp; Rooms</a> about €45. Display only — not in the trip total.</p>',
            "lp-2": '<p class="fine">Same cheap 16 December inbounds. The 18 December flight home for two is expensive.</p>',
            "lp-7": '<p class="fine">Arriving a day later, 16–22 December, keeps Ella on the <span data-bind="f:haj-lpa-16">€72</span> nonstop (city flights <span data-bind="b:gc-16-22">€241</span>). That is not the headline seven-night total.</p>',
        },
    },
    {
        "id": "maspalomas",
        "name": "Maspalomas",
        "full": "Maspalomas, Gran Canaria south",
        "photo": "./photos/maspalomas-dunes.jpg",
        "photo_alt": "Aerial view of the Maspalomas dunes meeting the Atlantic",
        "lede": "Dunes, lighthouse, south-coast light. You still fly into Las Palmas (LPA). Airbnb covers two, three nights and a week. One night had nothing in town within €35–85 — check live. Booking hotels from 22 November are still listed — recheck live. We did not price 3–4★ rooms here.",
        "plans": ["masp-1", "masp-2", "masp-3", "masp-7"],
        "budget_hotels": ["masp-priv-1", "masp-priv-2", "ohana-masp-3", "hhriz-masp-3", "masp-south-7"],
        "nicer_hotels": [],
        "hotel_used": {
            "masp-priv-1": "One-night Booking search for 16–17 December. No stored Booking fare, and no Airbnb in town within €35–85 — check live.",
            "masp-priv-2": "Two-night Booking search for 16–18 December. No stored Booking fare — Airbnb is on the stay above.",
            "ohana-masp-3": "Booking.com private room for three nights, checked 22 November — recheck live. Airbnb was cheaper.",
            "hhriz-masp-3": "Booking.com private room for three nights, checked 22 November — recheck live.",
            "masp-south-7": "Booking south-coast search, 22 November — recheck live. Airbnb was cheaper. HH Riz was unavailable these dates.",
        },
        "extra": {
            "masp-1": '<p class="fine">Same Gran Canaria flights as Las Palmas — airport LPA, Ella’s 16 December nonstop. No Airbnb in town within €35–85 — <a href="https://www.airbnb.es/s/Maspalomas--Spain/homes?checkin=2026-12-16&amp;checkout=2026-12-17&amp;adults=2&amp;price_min=35&amp;price_max=85&amp;currency=EUR" target="_blank" rel="noopener noreferrer">check live on Airbnb</a>. Cheapest hotel that night on Google: Axel Beach Maspalomas about €161. Display only — not in the trip total.</p>',
            "masp-2": '<p class="fine">Same 16 December inbounds. The 18 December LPA→OVD pair is expensive.</p>',
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
        "lede": "Picasso’s city, a working port, winter sun on the mainland. Airbnb covers one and two nights. Hostal NV Palacio Congresos still wins three nights and a week (Booking, 22 November — recheck live). The 4★ picks were priced for 18–21 December, a different window.",
        "plans": ["malaga-1", "malaga-2", "malaga-3", "malaga-7"],
        "budget_hotels": ["agp-priv-1", "agp-priv-2", "nv-agp-3", "nv-agp-7"],
        "nicer_hotels": ["alameda-agp", "icon-malabar"],
        "hotel_used": {
            "agp-priv-1": "One-night Booking search for 18–19 December (Ella’s Eurowings nonstop). No stored Booking fare — Airbnb is on the stay above.",
            "agp-priv-2": "Two-night Booking search for 18–20 December. No stored Booking fare — Airbnb is on the stay above.",
            "nv-agp-3": "Cheapest verified private stay for 15–18 December — used in the three-night total. Booking.com, 22 November — recheck live.",
            "alameda-agp": "Nicer 4★ pick for 18–21 December, USD. Together AGP→OVD on 21 December was not priced, so this is not a headline plan.",
            "icon-malabar": "Nicer 4★ pick for 18–21 December, USD. Same incomplete window.",
            "nv-agp-7": "Cheapest verified private stay for 18–25 December — used in the seven-night total. Booking.com, 22 November — recheck live.",
        },
        "extra": {
            "malaga-1": '<p class="fine">Best inbound alignment is 18 December (Ella nonstop). Hotels for one night (Google Hotels): Futurotel Malagueta 3★ about €50; Sol Málaga Guadalmar 4★ about €80 (near the airport). Display only — not in the trip total.</p>',
            "malaga-2": '<p class="fine">Same 18 December inbounds.</p>',
            "malaga-3": '<p class="fine">There is a second three-night window, 18–21 December, on Ella’s Eurowings 07:10 nonstop (about <span data-bind="usd:haj-agp-18-usd">$130</span>). Ali’s OVD–AGP round trip those dates was about <span data-bind="usd:ovd-agp-rt-18-21">$111</span>. Her flight home to Asturias on 21 December was not priced, so it is not a full plan. Partial with Alameda Centro: about <span data-bind="partial:alameda">$651</span>; with ICON Malabar about <span data-bind="partial:malabar">$706</span>.</p>',
        },
    },
    {
        "id": "barcelona",
        "name": "Barcelona",
        "full": "Barcelona",
        "photo": "./photos/barcelona-sagrada.jpg",
        "photo_alt": "The towers of the Sagrada Família in Barcelona",
        "lede": "The Christmas-city option, and the best-value 3–4★ rooms we priced. Airbnb wins one, two and three nights. Hostal House still wins the week (Booking, 22 November — recheck live). Hostal Argo is the other private week we priced.",
        "plans": ["bcn-1", "bcn-2", "bcn-3", "bcn-7"],
        "budget_hotels": ["bcn-priv-1", "bcn-priv-2", "maragall-bcn-3", "house-bcn-7", "argo-bcn-7"],
        "nicer_hotels": ["arc-rambla", "arcelon", "pestana-arena"],
        "hotel_used": {
            "bcn-priv-1": "One-night Booking search for 15–16 December. No stored Booking fare — Airbnb is on the stay above.",
            "bcn-priv-2": "Two-night Booking search for 15–17 December. No stored Booking fare — Airbnb is on the stay above.",
            "maragall-bcn-3": "Booking.com three nights, checked 22 November — recheck live. Airbnb was cheaper.",
            "arc-rambla": "Nicer 3★ pick, USD, not in the euro total.",
            "arcelon": "Nicer 4★ pick, USD, not in the euro total.",
            "pestana-arena": "Nicer 4★ pick, USD, not in the euro total.",
            "argo-bcn-7": "Booking.com week, checked 22 November — recheck live.",
            "house-bcn-7": "Cheapest verified private stay for a week — used in the total. Booking.com, 22 November — recheck live.",
        },
        "extra": {
            "bcn-1": '<p class="fine">Both arrive 15 December on cheap Vueling. The 16 December flight home has two stops — possible self-transfer, separate tickets. Hotels for one night (Google Hotels): cheapest about €92 (Negresco Princess / Acta Voraport). Display only — not in the trip total.</p>',
            "bcn-2": '<p class="fine">Same 15 December inbounds. The 17 December flight home for two is expensive.</p>',
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


def pretty_date_list(dates: list[str]) -> str:
    if not dates:
        return ""
    if len(dates) == 1:
        return pretty(dates[0])
    parsed = [date_cls.fromisoformat(d) for d in dates]
    consecutive = all((parsed[i] - parsed[i - 1]).days == 1 for i in range(1, len(parsed)))
    if consecutive and parsed[0].month == parsed[-1].month:
        month = pretty(dates[0]).split(" ", 1)[1]
        return f"{parsed[0].day}–{parsed[-1].day} {month}"
    labels = [pretty(d) for d in dates]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return ", ".join(labels[:-1]) + " and " + labels[-1]


def home_route(opt: dict) -> str:
    names = ella_home_data.HOME_IATA
    return (
        f"{names[opt['origin']]} ({opt['origin']}) → "
        f"{names[opt['destination']]} ({opt['destination']})"
    )


def home_stops(opt: dict) -> str:
    if opt.get("nonstop") or opt.get("stops") == 0:
        return "Nonstop"
    via = opt.get("via")
    via_name = {"MAD": "Madrid", "BCN": "Barcelona"}.get(via or "", via or "")
    if via_name:
        return f"1 stop, {via_name}"
    return "1 stop"


def home_pick_card(opt: dict, kicker: str, title: str) -> str:
    extra = ""
    if opt.get("bus"):
        extra = f'<p class="fine">{escape(opt["bus"])}</p>'
    date_s = pretty_date_list(opt.get("dates") or [opt["date"]])
    return f"""
        <article class="home-pick home-pick--{escape(kicker)}">
          <p class="kicker">{escape(title)}</p>
          <h3>{escape(home_route(opt))}</h3>
          <p class="hotel-price" data-bind="home:{opt['id']}">{euro(opt['price_eur'])}</p>
          <p>{escape(date_s)}. {escape(opt['airline'])}. {escape(home_stops(opt))}. {escape(opt['duration'])}, {escape(opt['times'])}.</p>
          <p class="fine">{escape(opt['train_to_haj'])}</p>
          {extra}
          <p class="fine">{escape(opt.get('note') or '')}</p>
          <a class="book-link book-link--home" href="{escape(opt['gf_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Book</a>
        </article>"""


def home_row(opt: dict) -> str:
    date_s = pretty_date_list(opt.get("dates") or [opt["date"]])
    badges = []
    if "cheapest" in (opt.get("badges") or []):
        badges.append('<span class="best-tag best-tag--trip">Cheapest overall</span>')
    if "cheapest_ovd" in (opt.get("badges") or []):
        badges.append('<span class="best-tag best-tag--value">Cheapest from Oviedo</span>')
    if "haj_ovd" in (opt.get("badges") or []):
        badges.append('<span class="best-tag">Closest — lands at home</span>')
    if "ham_ovd" in (opt.get("badges") or []):
        badges.append('<span class="best-tag">Hamburg, from Oviedo</span>')
    if "cheapest_haj" in (opt.get("badges") or []):
        badges.append('<span class="best-tag">Cheapest into Hannover</span>')
    if "nonstop" in (opt.get("badges") or []):
        badges.append('<span class="best-tag best-tag--value">Nonstop</span>')
    badge_html = " ".join(badges)
    extra_btns = []
    shown_links = opt.get("links") or []
    if len(shown_links) > 4:
        shown_links = [shown_links[0]]
    for link in shown_links:
        label = "Book" if link["date"] == opt["date"] and len(shown_links) == 1 else pretty(link["date"])
        extra_btns.append(
            f'<a class="book-link book-link--home" href="{escape(link["gf_url"], quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">{escape(label)}</a>'
        )
    books = extra_btns or [
        f'<a class="book-link book-link--home" href="{escape(opt["gf_url"], quote=True)}" '
        f'target="_blank" rel="noopener noreferrer">Book</a>'
    ]
    bus = f'<p class="fine">{escape(opt["bus"])}</p>' if opt.get("bus") else ""
    note = f'<p class="fine">{escape(opt["note"])}</p>' if opt.get("note") else ""
    return f"""
          <tr>
            <td>{opt['rank']}</td>
            <td>
              <strong>{escape(home_route(opt))}</strong>
              {badge_html}
            </td>
            <td>{escape(date_s)}</td>
            <td><strong data-bind="home:{opt['id']}">{euro(opt['price_eur'])}</strong></td>
            <td>{escape(opt['airline'])}</td>
            <td>{escape(home_stops(opt))}</td>
            <td>{escape(opt['duration'])}<br>{escape(opt['times'])}</td>
            <td>{escape(opt['train_to_haj'])}{bus}{note}</td>
            <td class="home-book">{''.join(books)}</td>
          </tr>"""


def date_pills(rows: list[dict], bind_kind: str) -> str:
    bits = []
    for row in rows:
        bits.append(
            f'<a class="date-pill" href="{escape(row["gf_url"], quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">'
            f'<span>{escape(pretty(row["date"]))}</span>'
            f'<strong data-bind="{bind_kind}:{row["id"]}">{euro(row["price_eur"])}</strong>'
            f'<span class="fine">{escape(row["airline"])}</span>'
            f"</a>"
        )
    return "".join(bits)


def home_badge(options, badge: str):
    return next(o for o in options if badge in (o.get("badges") or []))


def home_section(data: dict) -> str:
    home = data["ella_home"]
    options = home["options"]
    cheapest = home_badge(options, "cheapest")
    cheapest_ovd = home_badge(options, "cheapest_ovd")
    ham_ovd = home_badge(options, "ham_ovd")
    haj_ovd = home_badge(options, "haj_ovd")
    rows = "".join(home_row(o) for o in options)
    airport_rows = []
    for item in home["cheapest_by_airport"]:
        price = euro(item["price_eur"]) if item.get("price_eur") is not None else "calendar only"
        tag = "" if item.get("verified") else ' <span class="best-tag">Unverified</span>'
        origin = ella_home_data.HOME_IATA.get(item.get("from") or "", item.get("from") or "")
        airport_rows.append(
            f"<tr><th scope=\"row\">{escape(item['name'])} ({escape(item['airport'])})</th>"
            f"<td>{escape(price)} from {escape(origin)}{tag}</td>"
            f"<td>{escape(item['note'])}</td></tr>"
        )
    gaps = "".join(f"<li>{escape(g)}</li>" for g in home["gaps"])
    return f"""
  <section class="dest-section dest-home" id="ella-home">
    <div class="container">
      <header class="dest-head">
        <div>
          <p class="kicker">Whenever you like</p>
          <h2>Ella’s flight home</h2>
          <p>Stay in Asturias as long as you want — Ali is happy if you stay longer. This is separate from the city trip totals, so you can pick the day. Window 17 December 2026 – 4 January 2027. Home is near Hannover, so these options land at Hannover, Hamburg, Bremen, Düsseldorf or Cologne — Frankfurt is the backup. Amsterdam is too far. Prices checked <span data-bind="home_flights_checked">27 November 2026</span>, one adult, economy, one way, euros including taxes as Google Flights showed them. Nothing is booked.</p>
          <p>There is <strong>no December nonstop from Oviedo</strong> to Hannover, Frankfurt, Hamburg or Düsseldorf. Lufthansa’s Oviedo–Frankfurt nonstop starts in March 2027. The one confirmed nonstop is Eurowings Bilbao → Düsseldorf.</p>
        </div>
      </header>
      <div class="home-picks">
        {home_pick_card(haj_ovd, "wine", "Closest — lands at home")}
        {home_pick_card(ham_ovd, "sea", "Hamburg, from Oviedo")}
        {home_pick_card(cheapest_ovd, "gold", "Cheapest from Oviedo")}
        {home_pick_card(cheapest, "gold", "Cheapest overall")}
      </div>
      <p class="aside">Bilbao and Santander need a bus from Gijón. Bilbao about €31–50 and 4.5–6 hours; Santander about €20–23 and 3–4 hours. Those bus fares are recent published prices, <strong>not live-verified</strong> for the exact mid-December day — recheck before you book. The cheapest fare into Hannover itself is Bilbao → Hannover €88 on 23 December, but after the bus Oviedo → Hannover €104 is usually kinder.</p>
      <h3 class="hotels-title">Options near Hannover</h3>
      <p class="fine">Sorted closest first: Hannover, Hamburg, Bremen, Düsseldorf, Cologne, then Frankfurt as a backup. Flight only. Add the bus for Bilbao and Santander. Book opens Google Flights for that day.</p>
      <div class="table-wrap">
        <table class="home-table">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">Route</th>
              <th scope="col">Date</th>
              <th scope="col">Price</th>
              <th scope="col">Airline</th>
              <th scope="col">Stops</th>
              <th scope="col">Times</th>
              <th scope="col">On to Hannover</th>
              <th scope="col">Book</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
      <h3 class="hotels-title">Pick a date: Oviedo → Frankfurt</h3>
      <p class="fine">Confirmed opened fares, 27 November 2026. 21 December is Iberia; the rest are Air Europa, one stop via Madrid.</p>
      <div class="date-pills">
        {date_pills(home["calendar"]["ovd_fra"], "homecal")}
      </div>
      <h3 class="hotels-title">Pick a date: Oviedo → Hannover</h3>
      <p class="fine">Confirmed opened fares that land at home. Other dates we opened were €196–300, or 34 hours on 24 December — skip those.</p>
      <div class="date-pills">
        {date_pills(home["calendar"]["ovd_haj"], "homecal")}
      </div>
      <h3 class="hotels-title">Cheapest confirmed fare per airport</h3>
      <p class="fine">Closest to Hannover first. Frankfurt is the backup.</p>
      <div class="table-wrap">
        <table class="home-table home-table--airports">
          <thead>
            <tr>
              <th scope="col">Airport</th>
              <th scope="col">Cheapest</th>
              <th scope="col">On to Hannover</th>
            </tr>
          </thead>
          <tbody>
            {''.join(airport_rows)}
          </tbody>
        </table>
      </div>
      <h3 class="hotels-title">Buses to Bilbao and Santander</h3>
      <p>{escape(home["buses"]["bio"])}</p>
      <p>{escape(home["buses"]["sdr"])}</p>
      <h3 class="hotels-title">What we did not treat as a recommendation</h3>
      <ul class="home-gaps">
        {gaps}
      </ul>
    </div>
  </section>
"""


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

        def used_line(hid):
            for pid in dest["plans"]:
                plan = pmap[pid]
                nights = plan["nights"]
                word = "night" if nights == 1 else "nights"
                if plan.get("hotel") == hid:
                    return f"Cheapest verified private stay for {nights} {word} — used in the total."
                if plan.get("alt_hotel") == hid:
                    src = (
                        "Airbnb, 27 November"
                        if hmap[hid].get("source") == "airbnb"
                        else "Booking.com, 22 November — recheck live"
                    )
                    return f"Priced alternative for {nights} {word} ({src})."
            return dest["hotel_used"].get(hid, "")

        budget_cards = [
            hotel_card(hmap[hid], used_line(hid))
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
        <h3 class="hotels-title">Budget private rooms on Booking</h3>
        <p class="fine">Private double rooms for two — hostels, guesthouses, hostales, studios. Never a shared dorm. Booking euro prices were last checked 22 November 2026 and need a live recheck. Totals use the cheapest verified option after comparing these with Airbnb. Photos are of the city, labelled as such.</p>
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
      <a href="#ella-home">Home</a>
    </nav>
  </header>

  <section class="hero" aria-label="Cover">
    <figure class="hero-photo">
      <img src="./photos/palma-cathedral.jpg" width="2400" height="1364" alt="Palma Cathedral, La Seu, seen across the water from the harbour" fetchpriority="high">
    </figure>
    <div class="hero-plate">
      <p class="kicker">14 December 2026 – 1 January 2027</p>
      <h1>Our first vacation, together.</h1>
      <p class="lead">Ella, this is the shape of the trip — five cities, one night to a week, then home whenever you choose.</p>
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
    <a href="#ella-home">Flight home</a>
  </nav>

  <section class="intro" id="hello">
    <div class="container">
      <p class="kicker">For Ella</p>
      <h2>How this trip actually works</h2>
      <p>You fly from Hannover to the city. Ali flies from Oviedo. Trip length is flexible: one night, two, three, or a week. You share a <strong>private stay for two</strong> for every night in the city — check-in on the day you arrive, check-out on the day you fly together to Asturias. Then days in Asturias at home, no hotel — stay as long as you like. Your flight home is separate, so you can pick the day. Totals use the cheapest verified private option: Airbnb checked <span data-bind="rooms_checked">27 November 2026</span> versus Booking hotels checked <span data-bind="hotels_checked">22 November 2026</span> (recheck Booking live — we could not re-verify those today). Never a shared room.</p>
      <ol class="shape">
        <li><strong>You</strong> — Hannover (HAJ) → the city.</li>
        <li><strong>Ali</strong> — Oviedo / Asturias (OVD) → the city.</li>
        <li><strong>Stay</strong> — N nights in a private room or whole place for two. Check-in arrival day, check-out the morning you both fly to Asturias.</li>
        <li><strong>Both of you</strong> — the city → Asturias (OVD), two people.</li>
        <li><strong>Days in Asturias</strong> — at home, no hotel. Stay longer if you want.</li>
        <li><strong>You</strong> — fly home whenever you choose. See <a href="#ella-home">Ella’s flight home</a>. Not in the trip totals.</li>
      </ol>
      <p class="aside">This page does not process payment. Flight snapshot <span data-bind="snapshot">27 November 2026</span>. Rooms checked <span data-bind="rooms_checked">27 November 2026</span>. Booking hotels last checked <span data-bind="hotels_checked">22 November 2026</span> — recheck live. Flights are economy, no checked bags. Recheck before you pay. Food, buses, transfers, tickets, bags and insurance are not included. Self-transfers are separate tickets.</p>
    </div>
  </section>

  <section class="compare" id="compare">
    <div class="container">
      <p class="kicker">At a glance</p>
      <h2>Which city is kindest to the budget?</h2>
      <p>A trip total is Ella’s inbound + Ali’s inbound + the shared flight to Asturias (already priced for two) + the cheapest verified private stay for all N city nights. Ella’s flight home is <strong>not</strong> in these numbers — pick that in <a href="#ella-home">Ella’s flight home</a>. An unpriced room is left out and labelled check live. <strong>Best value</strong> is the cheapest full city stay in that row (room + all three city flights). <strong>Cheapest trip</strong> is the lowest complete total on the page.</p>
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
      <p class="fine" data-bind="cheapestHeadline">Headline cheapest: 1 night Palma.</p>
      <p class="fine">One- and two-night columns now include Airbnb stay totals except Maspalomas one night, which is still check live. Booking hotel prices are from 22 November — recheck live. All 1n/2n returns to Asturias are verified. Totals do not include Ella’s flight home. Prices jump after 22 December, so arriving 14–18 December is the kinder window. 1 USD ≈ 0.911 EUR is approximate, only for the USD hotel cards.</p>
    </div>
  </section>

  {''.join(sections)}

  {home_section(data)}

  <footer class="site-foot">
    <div class="container">
      <p>A private page for two people. Ella’s first name is on the buttons because Ali asked. No last names. Photographs are Wikimedia Commons files — credits in <a href="./photos/CREDITS.md">photos/CREDITS.md</a>.</p>
      <p>Live at <a href="https://aliattia10.github.io/january-island-choice/">aliattia10.github.io/january-island-choice</a>. Flight snapshot <span data-bind="snapshot">27 November 2026</span>. Rooms checked <span data-bind="rooms_checked">27 November 2026</span>. Home flights checked <span data-bind="home_flights_checked">27 November 2026</span>.</p>
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
        print(
            plan["id"],
            "stay",
            plan.get("hotel"),
            "sub",
            plan.get("subtotal_eur"),
            "total",
            plan.get("total_eur"),
            "complete",
            plan.get("total_complete"),
        )


if __name__ == "__main__":
    main()
