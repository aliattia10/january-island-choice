(function () {
  const destInputs = document.querySelectorAll('input[name="dest"]');
  const nightInputs = document.querySelectorAll('input[name="nights"]');
  const live = document.getElementById("choice-live");

  const labels = {
    palma: "Palma, Mallorca",
    maspalomas: "Maspalomas, Gran Canaria south",
    laspalmas: "Las Palmas, Gran Canaria city"
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

  function writeHash() {
    const dest = selected("dest");
    const nights = selected("nights");
    if (!dest || !nights) return;
    const next = "#" + dest + "/" + nights;
    if (location.hash !== next) {
      history.replaceState(null, "", next);
    }
  }

  function readHash() {
    const raw = location.hash.replace(/^#/, "");
    const parts = raw.split("/");
    const dest = parts[0];
    const nights = parts[1];
    const destEl = dest && document.getElementById("dest-" + dest);
    const nightEl = nights && document.getElementById("nights-" + nights);
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

  window.hallmarkSlots = function (map) {
    Object.entries(map).forEach(function (entry) {
      const slot = document.querySelector('[data-slot="' + entry[0] + '"]');
      if (!slot) return;
      const value = entry[1];
      const image = new Image();
      image.src = typeof value === "string" ? value : value.src;
      image.alt = (typeof value === "object" && value.alt) || slot.dataset.alt || "";
      slot.querySelectorAll(":scope > img").forEach(function (old) {
        old.remove();
      });
      slot.prepend(image);
    });
  };

  document.querySelectorAll("[data-slot] img").forEach(function (img) {
    if (img.complete && !img.naturalWidth) img.remove();
    else img.addEventListener("error", function () { img.remove(); }, { once: true });
  });
}());
