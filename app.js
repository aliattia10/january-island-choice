(function () {
  const shortNames = {
    palma: "Palma",
    maspalomas: "Maspalomas",
    laspalmas: "Las Palmas",
    malaga: "Málaga",
    barcelona: "Barcelona"
  };

  const navLinks = document.querySelectorAll(".dest-nav a");
  const sections = Array.prototype.map.call(navLinks, function (link) {
    return document.querySelector(link.getAttribute("href"));
  }).filter(Boolean);

  function setCurrent() {
    let current = sections[0];
    const y = window.scrollY + 120;
    sections.forEach(function (section) {
      if (section.offsetTop <= y) current = section;
    });
    navLinks.forEach(function (link) {
      const on = current && link.getAttribute("href") === "#" + current.id;
      if (on) link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
    });
  }

  window.addEventListener("scroll", setCurrent, { passive: true });
  setCurrent();

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

  function fareKnown(flight) {
    if (!flight) return false;
    if (flight.currency === "USD") return false;
    if (flight.price_status === "check_live") return false;
    return flight.price_eur != null;
  }

  function displayPlan(plan) {
    if (plan.total_complete && plan.total_eur != null) return euro(plan.total_eur);
    const notes = [];
    if (plan.together_missing) notes.push("plus the shared flight home (check live)");
    if (plan.hotel_missing) notes.push("plus the private room (check live)");
    if (!plan.fra_known) notes.push("plus her flight to Frankfurt");
    const base = plan.subtotal_eur != null ? plan.subtotal_eur : plan.partial_eur;
    if (base != null) return euro(base) + (notes.length ? " " + notes.join(" ") : "");
    return "check live";
  }

  function cheapestPlan(plans, nights) {
    const pool = (plans || []).filter(function (plan) {
      return plan.headline && Number(plan.nights) === nights;
    });
    if (!pool.length) return null;
    const complete = pool.filter(function (plan) {
      return plan.total_complete && plan.total_eur != null;
    });
    const use = complete.length ? complete : pool.filter(function (plan) {
      return plan.subtotal_eur != null;
    });
    if (!use.length) return null;
    const key = complete.length ? "total_eur" : "subtotal_eur";
    return {
      plan: use.slice().sort(function (a, b) { return a[key] - b[key]; })[0],
      complete: Boolean(complete.length)
    };
  }

  function bestValueForDest(plans, dest) {
    const pool = (plans || []).filter(function (plan) {
      return plan.headline && plan.dest === dest && plan.subtotal_eur != null;
    });
    if (!pool.length) return null;
    return pool.slice().sort(function (a, b) { return a.subtotal_eur - b.subtotal_eur; })[0];
  }

  function cheapestTrip(plans) {
    const complete = (plans || []).filter(function (plan) {
      return plan.headline && plan.total_complete && plan.total_eur != null;
    });
    if (complete.length) {
      return complete.slice().sort(function (a, b) { return a.total_eur - b.total_eur; })[0];
    }
    const subs = (plans || []).filter(function (plan) {
      return plan.headline && plan.subtotal_eur != null;
    });
    if (!subs.length) return null;
    return subs.slice().sort(function (a, b) { return a.subtotal_eur - b.subtotal_eur; })[0];
  }

  function applyPrices(data) {
    const flights = indexById(data.flights);
    const hotels = indexById(data.hotels);
    const plans = indexById(data.plans);
    const bundles = indexById(data.bundles);
    const rate = Number(data.usd_to_eur) || 0.911;
    const snapshot = prettyDate(data.snapshot);
    const hotelsChecked = prettyDate(data.hotels_checked);
    const roomsChecked = prettyDate(data.rooms_checked);
    const c1 = cheapestPlan(data.plans || [], 1);
    const c2 = cheapestPlan(data.plans || [], 2);
    const c3 = cheapestPlan(data.plans || [], 3);
    const c7 = cheapestPlan(data.plans || [], 7);
    const tripWinner = cheapestTrip(data.plans || []);
    const cheapestByNights = { 1: c1, 2: c2, 3: c3, 7: c7 };

    function resolve(key) {
      if (key === "snapshot") return snapshot;
      if (key === "hotels_checked") return hotelsChecked;
      if (key === "rooms_checked") return roomsChecked;
      if (key === "cheapestHeadline") {
        const bits = [];
        if (tripWinner) {
          bits.push(
            "Cheapest trip: " + shortNames[tripWinner.dest] + " " + tripWinner.nights +
            " night" + (tripWinner.nights === 1 ? "" : "s") + " " +
            (tripWinner.total_complete ? euro(tripWinner.total_eur) + " including Frankfurt" : euro(tripWinner.subtotal_eur) + " before Frankfurt")
          );
        }
        [c1, c2, c3, c7].forEach(function (winner, i) {
          if (!winner) return;
          const n = [1, 2, 3, 7][i];
          bits.push(
            n + "n " + shortNames[winner.plan.dest] + " " +
            (winner.complete ? euro(winner.plan.total_eur) : euro(winner.plan.subtotal_eur) + " before Frankfurt")
          );
        });
        return bits.join(". ") + ".";
      }

      const parts = key.split(":");
      const kind = parts[0];
      const id = parts[1];
      const extra = parts[2];

      if (kind === "f") {
        const flight = flights[id];
        if (!flight) return null;
        if (flight.currency === "USD") return usd(flight.price_usd);
        if (!fareKnown(flight)) return "check live price";
        return euro(flight.price_eur);
      }
      if (kind === "h") {
        const hotel = hotels[id];
        if (!hotel) return null;
        if (hotel.price == null || hotel.price_status === "check_live") return "check live price";
        return hotel.currency === "USD" ? usd(hotel.price) : euro(hotel.price);
      }
      if (kind === "p") {
        const plan = plans[id];
        if (!plan) return null;
        if (extra === "sub") {
          if (plan.subtotal_eur != null) return euro(plan.subtotal_eur);
          if (plan.partial_eur != null) return euro(plan.partial_eur);
          return null;
        }
        if (extra === "display") return displayPlan(plan);
        if (extra === "alt") {
          if (plan.alt_total_eur != null) return euro(plan.alt_total_eur);
          if (plan.alt_subtotal_eur != null) return euro(plan.alt_subtotal_eur) + " plus her flight to Frankfurt";
          return null;
        }
        if (plan.total_complete && plan.total_eur != null) return euro(plan.total_eur);
        return displayPlan(plan);
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

    document.querySelectorAll("[data-if-cheapest]").forEach(function (el) {
      const spec = el.getAttribute("data-if-cheapest") || "";
      const bits = spec.split(":");
      const dest = bits[0];
      const nights = Number(bits[1]);
      const winner = cheapestByNights[nights];
      el.hidden = !(winner && winner.plan && winner.plan.dest === dest);
    });
    document.querySelectorAll("[data-if-best-value]").forEach(function (el) {
      const spec = el.getAttribute("data-if-best-value") || "";
      const bits = spec.split(":");
      const dest = bits[0];
      const nights = Number(bits[1]);
      const winner = bestValueForDest(data.plans || [], dest);
      el.hidden = !(winner && winner.nights === nights);
    });
    document.querySelectorAll("[data-if-cheapest-trip]").forEach(function (el) {
      const spec = el.getAttribute("data-if-cheapest-trip") || "";
      const bits = spec.split(":");
      const dest = bits[0];
      const nights = Number(bits[1]);
      el.hidden = !(tripWinner && tripWinner.dest === dest && Number(tripWinner.nights) === nights);
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
