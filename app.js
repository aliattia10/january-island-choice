(function () {
  const destInputs = document.querySelectorAll('input[name="dest"]');
  const nightInputs = document.querySelectorAll('input[name="nights"]');
  const live = document.getElementById("choice-live");

  const labels = {
    palma: "Palma, Mallorca",
    maspalomas: "Maspalomas, Gran Canaria south",
    laspalmas: "Las Palmas, Gran Canaria city",
    malaga: "Málaga",
    barcelona: "Barcelona"
  };

  const shortNames = {
    palma: "Palma",
    maspalomas: "Maspalomas",
    laspalmas: "Las Palmas",
    malaga: "Málaga",
    barcelona: "Barcelona"
  };

  function selected(name) {
    const el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }

  function announce() {
    const dest = selected("dest");
    const nights = selected("nights");
    if (!live || !dest || !nights) return;
    live.textContent = labels[dest] + ", " + nights + " nights.";
  }

  function isChoiceHash(raw) {
    const parts = (raw || "").replace(/^#/, "").split("/");
    return Boolean(parts[0] && document.getElementById("dest-" + parts[0]));
  }

  function writeHash() {
    const dest = selected("dest");
    const nights = selected("nights");
    if (!dest || !nights) return;
    if (location.hash && !isChoiceHash(location.hash)) return;
    const next = "#" + dest + "/" + nights;
    if (location.hash !== next) history.replaceState(null, "", next);
  }

  function readHash() {
    const raw = location.hash.replace(/^#/, "");
    const parts = raw.split("/");
    const destEl = parts[0] && document.getElementById("dest-" + parts[0]);
    const nightEl = parts[1] && document.getElementById("nights-" + parts[1]);
    if (destEl) destEl.checked = true;
    if (nightEl) nightEl.checked = true;
  }

  destInputs.forEach(function (input) {
    input.addEventListener("change", function () {
      writeHash();
      announce();
    });
  });
  nightInputs.forEach(function (input) {
    input.addEventListener("change", function () {
      writeHash();
      announce();
    });
  });

  window.addEventListener("hashchange", function () {
    readHash();
    announce();
  });

  readHash();
  writeHash();
  announce();

  function euro(n) {
    return "€" + Math.round(Number(n));
  }

  function usd(n) {
    return "$" + Math.round(Number(n));
  }

  function prettyDate(iso) {
    if (!iso) return "";
    const parts = String(iso).split("-");
    if (parts.length !== 3) return iso;
    const months = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ];
    const month = months[Number(parts[1]) - 1];
    if (!month) return iso;
    return Number(parts[2]) + " " + month + " " + parts[0];
  }

  function indexById(list) {
    const out = {};
    (list || []).forEach(function (item) {
      out[item.id] = item;
    });
    return out;
  }

  function cheapestPlan(plans, nights) {
    const pool = plans.filter(function (plan) {
      return plan.headline && Number(plan.nights) === nights;
    });
    if (!pool.length) return null;
    return pool.slice().sort(function (a, b) {
      return a.total_eur - b.total_eur;
    })[0];
  }

  function applyPrices(data) {
    const flights = indexById(data.flights);
    const hotels = indexById(data.hotels);
    const plans = indexById(data.plans);
    const bundles = indexById(data.bundles);
    const rate = Number(data.usd_to_eur) || 0.86;
    const snapshot = prettyDate(data.snapshot);
    const hotelsChecked = prettyDate(data.hotels_checked);
    const c3 = cheapestPlan(data.plans || [], 3);
    const c7 = cheapestPlan(data.plans || [], 7);

    function resolve(key) {
      if (key === "snapshot") return snapshot;
      if (key === "hotels_checked") return hotelsChecked;
      if (key === "cheapestHeadline") {
        if (!c3 || !c7) return null;
        return "Headline cheapest: 3 nights " + shortNames[c3.dest] + " " + euro(c3.total_eur) + "; 7 nights " + shortNames[c7.dest] + " " + euro(c7.total_eur) + ".";
      }
      if (key === "winsLine") {
        if (!c3 || !c7) return null;
        return shortNames[c3.dest] + " still wins on money for three nights. " + shortNames[c7.dest] + " wins for a week. Barcelona is the Christmas-city option. Gran Canaria is the dunes-and-beach option, dearer once you stay seven nights.";
      }

      const parts = key.split(":");
      const kind = parts[0];
      const id = parts[1];
      const extra = parts[2];

      if (kind === "f") {
        const flight = flights[id];
        if (!flight) return null;
        if (flight.currency === "USD") return usd(flight.price_usd);
        return euro(flight.price_eur);
      }
      if (kind === "h") {
        const hotel = hotels[id];
        if (!hotel) return null;
        return hotel.currency === "USD" ? usd(hotel.price) : euro(hotel.price);
      }
      if (kind === "p") {
        const plan = plans[id];
        if (!plan) return null;
        if (extra === "alt") return euro(plan.alt_total_eur);
        return euro(plan.total_eur);
      }
      if (kind === "b") {
        const bundle = bundles[id];
        return bundle ? euro(bundle.total_eur) : null;
      }
      if (kind === "usd") {
        const hotel = hotels[id];
        const flight = flights[id];
        if (hotel) return usd(hotel.price);
        if (flight && flight.price_usd != null) return usd(flight.price_usd);
        return null;
      }
      if (kind === "usdapprox") {
        const hotel = hotels[id];
        if (!hotel) return null;
        return euro(Math.round(hotel.price * rate));
      }
      if (kind === "partial") {
        const value = (data.usd_partials || {})[id];
        return value == null ? null : usd(value);
      }
      return null;
    }

    document.querySelectorAll("[data-bind]").forEach(function (el) {
      const value = resolve(el.getAttribute("data-bind"));
      if (value == null || value === "") return;
      el.textContent = value;
    });

    document.querySelectorAll(".price-card .best-tag[data-badge]").forEach(function (el) {
      const nights = Number(el.getAttribute("data-badge"));
      const winner = nights === 7 ? c7 : c3;
      const card = el.closest(".price-card");
      const dest = card && card.getAttribute("data-highlight");
      el.hidden = !(winner && dest && winner.dest === dest);
    });

    document.querySelectorAll("[data-if-cheapest]").forEach(function (el) {
      const spec = el.getAttribute("data-if-cheapest") || "";
      const bits = spec.split(":");
      const dest = bits[0];
      const nights = Number(bits[1]);
      const winner = nights === 7 ? c7 : c3;
      el.hidden = !(winner && winner.dest === dest);
    });
  }

  fetch("./data/prices.json", { cache: "no-store" })
    .then(function (res) {
      if (!res.ok) throw new Error("prices.json " + res.status);
      return res.json();
    })
    .then(applyPrices)
    .catch(function () {
      // Keep the numbers already in the HTML.
    });
}());
