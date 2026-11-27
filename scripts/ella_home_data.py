"""Confirmed Ella home-flight options from Google Flights, 27 Nov 2026.

Do not invent airline, times, or prices. Calendar-only / unverified rows
are labelled as such. gf() is passed in so generated extra-date URLs match
the rest of the site.
"""

from __future__ import annotations


HOME_IATA = {
    "OVD": "Oviedo",
    "BIO": "Bilbao",
    "SDR": "Santander",
    "DUS": "Düsseldorf",
    "AMS": "Amsterdam",
    "HAM": "Hamburg",
    "FRA": "Frankfurt",
    "BER": "Berlin",
    "HAJ": "Hannover",
    "BRE": "Bremen",
    "CGN": "Cologne",
    "EIN": "Eindhoven",
}

TRAIN_TO_HAJ = {
    "HAJ": "S5 about 15–18 min to Hannover Hbf — you land at home.",
    "BRE": "About 1 hour plus the airport tram.",
    "HAM": "ICE about 1h15 after the airport S-Bahn.",
    "DUS": "ICE about 2h25 to Hannover Hbf.",
    "FRA": "ICE about 2h20 from Flughafen Fernbahnhof.",
    "CGN": "ICE about 2h33.",
    "BER": "ICE about 2h50 plus the airport transfer.",
    "AMS": "ICE International typically about 4–4.5 hours.",
    "EIN": "Often 4.5–6 hours overland.",
}

BUS = {
    "BIO": "Add a bus from Gijón: about €31–50 and 4.5–6 hours (ALSA + airport bus). Mid-December tickets not live-verified.",
    "SDR": "Add a bus from Gijón: about €20–23 and 3–4 hours. Mid-December tickets not live-verified.",
}


def opt(
    rank: int,
    origin: str,
    dest: str,
    dates: list[str],
    price: int,
    airline: str,
    stops: int,
    via: str,
    duration: str,
    times: str,
    gf_url: str,
    extra_links: list[dict] | None = None,
    badges: list[str] | None = None,
    note: str = "",
    fetch: bool = True,
    primary: str | None = None,
) -> dict:
    primary = primary or dates[0]
    links = [{"date": primary, "gf_url": gf_url}]
    for item in extra_links or []:
        if item["date"] != primary:
            links.append(item)
    return {
        "id": f"home-{rank:02d}",
        "rank": rank,
        "origin": origin,
        "destination": dest,
        "date": primary,
        "dates": dates,
        "price_eur": price,
        "price_status": "known",
        "airline": airline,
        "stops": stops,
        "via": via or None,
        "nonstop": stops == 0,
        "duration": duration,
        "times": times,
        "gf_url": gf_url,
        "links": links,
        "train_to_haj": TRAIN_TO_HAJ[dest],
        "bus": BUS.get(origin),
        "badges": badges or [],
        "note": note,
        "verified": True,
        "fetch": fetch,
        "adults": 1,
    }


def cal_row(origin: str, dest: str, date: str, price: int, airline: str, gf_fn, url: str | None = None, fetch: bool = True) -> dict:
    return {
        "id": f"cal-{origin.lower()}-{dest.lower()}-{date[5:7]}{date[8:10]}",
        "origin": origin,
        "destination": dest,
        "date": date,
        "price_eur": price,
        "price_status": "known",
        "airline": airline,
        "gf_url": url or gf_fn(date, origin, dest, 1),
        "verified": True,
        "fetch": fetch,
        "adults": 1,
        "nonstop": False,
    }


def payload(gf) -> dict:
    options = [
        opt(
            1, "BIO", "DUS", ["2026-12-21"], 50, "Eurowings", 0, "",
            "1h55", "15:40–17:35",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIxagcIARIDQklPcgcIARIDRFVTQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            badges=["cheapest", "nonstop"],
            note="The only confirmed nonstop. Flight-only beats Oviedo; after the bus the door-to-airport total is usually higher than flying from Oviedo, but the hop itself is a short afternoon.",
        ),
        opt(
            2, "OVD", "AMS", ["2026-12-19"], 55, "Air Europa", 1, "MAD",
            "12h35", "21:05–09:40+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE5agcIARIDT1ZEcgcIARIDQU1TQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            badges=["cheapest_ovd"],
            note="Cheapest confirmed fare from Oviedo. Long layover, then a long train.",
        ),
        opt(
            3, "BIO", "AMS", ["2026-12-19"], 58, "Air Europa", 1, "MAD",
            "12h35", "21:05–09:40+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE5agcIARIDQklPcgcIARIDQU1TQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Same itinerary as Oviedo–Amsterdam that day; add the bus, so Oviedo is usually better.",
        ),
        opt(
            4, "OVD", "DUS", ["2026-12-24"], 59, "Air Europa", 1, "MAD",
            "7h10", "10:35–17:45",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTI0agcIARIDT1ZEcgcIARIDRFVTQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Best timing of the €59 Düsseldorf fares — daytime, and it beats same-day Frankfurt €62.",
        ),
        opt(
            5, "OVD", "DUS", ["2026-12-17", "2026-12-21", "2026-12-27", "2026-12-29"], 59, "Air Europa", 1, "MAD",
            "12h30", "21:05–09:35+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE3agcIARIDT1ZEcgcIARIDRFVTQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            extra_links=[
                {"date": "2026-12-21", "gf_url": "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIxagcIARIDT1ZEcgcIARIDRFVTQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en"},
                {"date": "2026-12-27", "gf_url": gf("2026-12-27", "OVD", "DUS", 1)},
                {"date": "2026-12-29", "gf_url": gf("2026-12-29", "OVD", "DUS", 1)},
            ],
            note="Overnight €59 on 17, 21, 27 and 29 December. Beats 17 Dec Frankfurt €91 and 21 Dec Frankfurt €71.",
        ),
        opt(
            6, "OVD", "HAM", ["2026-12-24"], 60, "Vueling, Iberia", 1, "BCN",
            "11h35", "23:00–10:35+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTI0agcIARIDT1ZEcgcIARIDSEFNQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Beats same-day Frankfurt €62, and Hamburg is the closest cheap airport to home after Hannover itself.",
        ),
        opt(
            7, "BIO", "DUS", ["2026-12-17", "2026-12-24", "2026-12-28"], 60, "Air Europa", 1, "MAD",
            "9h15–12h30", "08:30–17:45 (24 Dec) or 21:05–09:35+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTI0agcIARIDQklPcgcIARIDRFVTQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            extra_links=[
                {"date": "2026-12-17", "gf_url": gf("2026-12-17", "BIO", "DUS", 1)},
                {"date": "2026-12-28", "gf_url": gf("2026-12-28", "BIO", "DUS", 1)},
            ],
            note="Add the bus; usually worse than Oviedo–Düsseldorf €59.",
            primary="2026-12-24",
        ),
        opt(
            8, "OVD", "FRA", [
                "2026-12-23", "2026-12-24", "2026-12-25", "2026-12-26", "2026-12-27",
                "2026-12-28", "2026-12-29", "2026-12-30", "2026-12-31",
            ], 62, "Air Europa", 1, "MAD",
            "7h20 or 12h40", "10:35–17:55 or 21:05–09:45+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTI0agcIARIDT1ZEcgcIARIDRlJBQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            extra_links=[
                {"date": d, "gf_url": gf(d, "OVD", "FRA", 1)}
                for d in [
                    "2026-12-23", "2026-12-25", "2026-12-26", "2026-12-27",
                    "2026-12-28", "2026-12-29", "2026-12-30", "2026-12-31",
                ]
            ],
            note="Cheapest confirmed Oviedo–Frankfurt in this window. Morning 7h20 on several dates (24–26, 28, 29, 31 December).",
            primary="2026-12-24",
        ),
        opt(
            9, "OVD", "AMS", ["2026-12-20", "2026-12-24"], 63, "Air Europa", 1, "MAD",
            "12h35", "21:05–09:40+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIwagcIARIDT1ZEcgcIARIDQU1TQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            extra_links=[{"date": "2026-12-24", "gf_url": gf("2026-12-24", "OVD", "AMS", 1)}],
            note="Near Frankfurt €62, then a long train.",
        ),
        opt(
            10, "OVD", "BER", ["2026-12-24"], 67, "Vueling, Iberia", 1, "BCN",
            "10h45", "23:00–09:45+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTI0agcIARIDT1ZEcgcIARIDQkVSQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Slightly above Frankfurt; longer onward train (~2h50).",
        ),
        opt(
            11, "OVD", "BER", ["2026-12-21"], 68, "Vueling, Iberia", 1, "BCN",
            "10h45", "23:00–09:45+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIxagcIARIDT1ZEcgcIARIDQkVSQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Beats same-day Frankfurt €71.",
        ),
        opt(
            12, "BIO", "BER", ["2026-12-17"], 70, "Vueling, Iberia", 1, "BCN",
            "11h55", "21:50–09:45+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE3agcIARIDQklPcgcIARIDQkVSQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Add the bus.",
        ),
        opt(
            13, "OVD", "FRA", ["2026-12-21"], 71, "Iberia", 1, "MAD",
            "9h15", "13:20–22:35",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIxagcIARIDT1ZEcgcIARIDRlJBQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Mid-window Frankfurt alternative.",
        ),
        opt(
            14, "SDR", "FRA", ["2026-12-28"], 71, "Iberia", 1, "MAD",
            "12h30", "10:05–22:35",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTI4agcIARIDU0RScgcIARIDRlJBQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Plus the bus ~€20–23; worse than Oviedo–Frankfurt €62 that day.",
        ),
        opt(
            15, "OVD", "BER", ["2026-12-17"], 72, "Vueling, Iberia", 1, "BCN",
            "5h45", "14:55–20:40",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE3agcIARIDT1ZEcgcIARIDQkVSQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Short connection; beats same-day Frankfurt €91.",
        ),
        opt(
            16, "SDR", "HAM", ["2026-12-19"], 78, "Vueling, Iberia", 1, "BCN",
            "16h00", "18:00–10:00+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE5agcIARIDU0RScgcIARIDSEFNQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Plus the bus; long layover. Oviedo options are usually better.",
        ),
        opt(
            17, "BIO", "HAM", ["2026-12-19"], 78, "Vueling, Iberia", 1, "BCN",
            "14h20", "19:40–10:00+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE5agcIARIDQklPcgcIARIDSEFNQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Plus the bus; long layover.",
        ),
        opt(
            18, "OVD", "HAM", ["2026-12-20"], 80, "Vueling", 1, "BCN",
            "11h35", "23:00–10:35+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIwagcIARIDT1ZEcgcIARIDSEFNQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Beats same-day Frankfurt €116.",
        ),
        opt(
            19, "BIO", "HAJ", ["2026-12-23"], 88, "Vueling, Iberia", 1, "BCN",
            "10h25", "23:00–09:25+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIzagcIARIDQklPcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            badges=["cheapest_haj"],
            note="Lands at home. The flight looks cheaper than Oviedo–Hannover €104 until you add the bus (~€31–50), which usually makes Oviedo cheaper.",
        ),
        opt(
            20, "OVD", "FRA", ["2026-12-17"], 91, "Air Europa", 1, "MAD",
            "7h20", "10:35–17:55",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE3agcIARIDT1ZEcgcIARIDRlJBQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Older site baseline day — Düsseldorf €59 is kinder on this date.",
        ),
        opt(
            21, "OVD", "HAM", ["2026-12-17"], 93, "Vueling, Iberia", 1, "BCN",
            "5h20", "14:55–20:15",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE3agcIARIDT1ZEcgcIARIDSEFNQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Short connection, close to home; almost matches 17 December Frankfurt €91.",
        ),
        opt(
            22, "BIO", "HAJ", ["2026-12-30"], 98, "Vueling, Iberia", 1, "BCN",
            "10h25", "23:00–09:25+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTMwagcIARIDQklPcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Lands at home. Plus the bus versus Oviedo–Hannover €124 that day may be close.",
        ),
        opt(
            23, "OVD", "HAJ", ["2026-12-23"], 104, "Vueling", 1, "BCN",
            "10h25", "23:00–09:25+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIzagcIARIDT1ZEcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            badges=["haj_ovd"],
            note="Best Oviedo fare that lands at Hannover. No bus.",
        ),
        opt(
            24, "OVD", "HAJ", ["2026-12-18", "2026-12-21"], 114, "Vueling / Vueling, Iberia", 1, "BCN",
            "10h25", "23:00–09:25+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE4agcIARIDT1ZEcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            extra_links=[{"date": "2026-12-21", "gf_url": gf("2026-12-21", "OVD", "HAJ", 1)}],
            note="18 December slightly beats same-day Frankfurt €116 and lands at home.",
        ),
        opt(
            25, "OVD", "HAJ", ["2026-12-30"], 124, "Vueling", 1, "BCN",
            "10h25", "23:00–09:25+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTMwagcIARIDT1ZEcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Above Frankfurt €62 that day; lands at home.",
        ),
        opt(
            26, "OVD", "HAJ", ["2026-12-28"], 145, "Vueling", 1, "BCN",
            "10h25", "23:00–09:25+1",
            "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTI4agcIARIDT1ZEcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
            note="Above Frankfurt €62; lands at home.",
        ),
    ]

    fra_given = {
        "2026-12-17": "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE3agcIARIDT1ZEcgcIARIDRlJBQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
        "2026-12-21": "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIxagcIARIDT1ZEcgcIARIDRlJBQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
        "2026-12-24": "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTI0agcIARIDT1ZEcgcIARIDRlJBQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
    }
    ovd_fra = []
    fra_days = [
        ("2026-12-17", 91, "Air Europa"),
        ("2026-12-18", 116, "Air Europa"),
        ("2026-12-19", 116, "Air Europa"),
        ("2026-12-20", 116, "Air Europa"),
        ("2026-12-21", 71, "Iberia"),
        ("2026-12-22", 116, "Air Europa"),
    ]
    for d in [f"2026-12-{n:02d}" for n in range(23, 32)]:
        fra_days.append((d, 62, "Air Europa"))
    for date, price, airline in fra_days:
        ovd_fra.append(cal_row("OVD", "FRA", date, price, airline, gf, fra_given.get(date)))

    haj_given = {
        "2026-12-18": "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTE4agcIARIDT1ZEcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
        "2026-12-23": "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTIzagcIARIDT1ZEcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
        "2026-12-28": "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTI4agcIARIDT1ZEcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
        "2026-12-30": "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTEyLTMwagcIARIDT1ZEcgcIARIDSEFKQAFIAXABggELCP___________wGYAQI&curr=EUR&hl=en",
    }
    ovd_haj = []
    for date, price, airline in [
        ("2026-12-18", 114, "Vueling / Vueling, Iberia"),
        ("2026-12-21", 114, "Vueling / Vueling, Iberia"),
        ("2026-12-23", 104, "Vueling"),
        ("2026-12-28", 145, "Vueling"),
        ("2026-12-30", 124, "Vueling"),
    ]:
        ovd_haj.append(cal_row("OVD", "HAJ", date, price, airline, gf, haj_given.get(date)))

    return {
        "checked": "2026-11-27",
        "window_start": "2026-12-17",
        "window_end": "2027-01-04",
        "options": options,
        "calendar": {"ovd_fra": ovd_fra, "ovd_haj": ovd_haj},
        "cheapest_by_airport": [
            {
                "airport": "DUS",
                "name": "Düsseldorf",
                "price_eur": 50,
                "from": "BIO",
                "verified": True,
                "note": "Eurowings nonstop, 21 Dec 15:40–17:35. From Oviedo: €59 several dates (best 24 Dec 10:35–17:45). ICE about 2h25.",
            },
            {
                "airport": "AMS",
                "name": "Amsterdam",
                "price_eur": 55,
                "from": "OVD",
                "verified": True,
                "note": "Air Europa via Madrid, 19 Dec 21:05–09:40+1. ICE International typically 4–4.5h. Cheap flight, long day after.",
            },
            {
                "airport": "HAM",
                "name": "Hamburg",
                "price_eur": 60,
                "from": "OVD",
                "verified": True,
                "note": "Vueling/Iberia via Barcelona, 24 Dec 23:00–10:35+1. Also €80 on 20 Dec, €93 on 17 Dec (short 5h20). ICE about 1h15 after S-Bahn.",
            },
            {
                "airport": "FRA",
                "name": "Frankfurt",
                "price_eur": 62,
                "from": "OVD",
                "verified": True,
                "note": "Air Europa via Madrid, 23–31 Dec (7h20 morning on several dates). ICE about 2h20 from Flughafen Fernbahnhof.",
            },
            {
                "airport": "BER",
                "name": "Berlin",
                "price_eur": 67,
                "from": "OVD",
                "verified": True,
                "note": "Vueling/Iberia via Barcelona, 24 Dec. Also €68 on 21 Dec, €72 on 17 Dec in 5h45. ICE about 2h50 plus airport transfer.",
            },
            {
                "airport": "HAJ",
                "name": "Hannover",
                "price_eur": 88,
                "from": "BIO",
                "verified": True,
                "note": "Vueling/Iberia via Barcelona, 23 Dec (add bus). From Oviedo: €104 on 23 Dec, €114 on 18 and 21 Dec. S5 about 15–18 min. No bus if she flies Oviedo.",
            },
            {
                "airport": "BRE",
                "name": "Bremen",
                "price_eur": 231,
                "from": "OVD",
                "verified": True,
                "note": "Opened 20 Dec, Air Europa+KLM, 2 stops Madrid+Amsterdam — not useful next to Hamburg/Düsseldorf. Bilbao calendar from €141, itinerary not opened.",
            },
            {
                "airport": "CGN",
                "name": "Cologne",
                "price_eur": None,
                "from": "BIO",
                "verified": False,
                "note": "Calendar only, from €195 Bilbao / €355 Oviedo — not competitive. ICE about 2h33.",
            },
            {
                "airport": "EIN",
                "name": "Eindhoven",
                "price_eur": None,
                "from": "BIO",
                "verified": False,
                "note": "Bilbao calendar from €70 on 22/24/25 Dec — itinerary not opened (Google Oops). Unverified as a bookable itinerary. Long overland, often 4.5–6h.",
            },
        ],
        "buses": {
            "sdr": "Santander Airport about €20–23 and 3–4 hours from Gijón. Not live-verified for the exact mid-December day.",
            "bio": "Bilbao Airport about €31–50 and 4.5–6 hours from Gijón (coach to Bilbao Intermodal plus Bizkaibus A3247, about 15–20 min). Not live-verified for the exact mid-December day.",
        },
        "gaps": [
            "No December nonstop from Oviedo to Hannover, Frankfurt, Hamburg or Düsseldorf. Lufthansa’s Oviedo–Frankfurt nonstop starts March 2027. The one confirmed nonstop is Eurowings Bilbao–Düsseldorf.",
            "Oviedo–Hannover itineraries failed to load for 17 and 26 December (timeout) and 2–3 January (Google Oops). Calendar 17 Dec €346 — unattractive. 26 Dec had no stored calendar price.",
            "Bilbao–Eindhoven calendar from €70 was not opened. Bilbao–Frankfurt December calendar was incomplete (only 1–4 January priced, from €127) and is not a recommendation.",
            "Santander–Bremen calendar failed; Santander–Düsseldorf and Santander–Amsterdam calendars were incomplete and looked expensive where priced. Santander–Hannover calendar from €203, incomplete.",
            "Santiago (SCQ) was not fully scanned; Ryanair from Santander/Santiago does not fly these German/Dutch airports.",
            "Secondary airports Dortmund, Paderborn, Hahn, Weeze: no useful priced calendar days from Oviedo or Bilbao in this scrape.",
            "Other opened Hannover/Hamburg dates cost more (Oviedo–Hannover 20/22/24/25/27/31 Dec €196–300; 24 Dec Hannover is 34h25 — skip). Oviedo–Bremen 20 Dec €231 is not useful next to Hamburg/Düsseldorf.",
            "Fares move; this is a 27 November 2026 snapshot. Recheck before you pay.",
        ],
    }
