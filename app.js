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
}());
