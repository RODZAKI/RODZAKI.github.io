document.addEventListener("DOMContentLoaded", function() {

  var SUPABASE_URL = "https://wteqinxdavkpvufsjjse.supabase.co";
  var ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0ZXFpbnhkYXZrcHZ1ZnNqanNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA4MjE0NzEsImV4cCI6MjA4NjM5NzQ3MX0.mREQi5l3U1SBv3rtayTu3oZCORBgJrTfTBY5Lu02sAQ";

  var params = new URLSearchParams(window.location.search);
  var drawer = params.get("drawer");

  var titles = {
    "dharma": "Canonical Root",
    "logos": "Artifact Catalog",
    "maat": "Canon / Protocol",
    "dao": "Publications",
    "rta": "Works / Core",
    "ayni": "Serial",
    "ubuntu": "Essays",
    "mitakuye-oyasin": "Notes",
    "sumak-kawsay": "Resolving"
  };

  var descriptions = {
    "dharma": "Foundational primitives, invariants, axioms, and definitions the entire system depends on.",
    "logos": "Indexes, mappings, registries, and lookup structures that organize and point to artifacts.",
    "maat": "Rules, constraints, enforcement logic, lifecycle definitions, and allowed operations.",
    "dao": "Externally consumable, composed outputs. Finished expressions intended for reading as a whole.",
    "rta": "Primary internal constructions — systems, models, architectures, and core builds still active.",
    "ayni": "Sequential, interdependent artifacts where order matters. Iterations and chained evolution.",
    "ubuntu": "Coherent, reflective, discursive pieces centered on a single idea or perspective.",
    "mitakuye-oyasin": "Loose, incomplete, exploratory, or associative material. Fragments and working thoughts.",
    "sumak-kawsay": "Artifacts still active, unresolved, or awaiting classification. The intake drawer."
  };

  var explanations = {
    "dharma": "Dharma is the principle of right order and right action in Indian philosophy. It refers both to the structure of the cosmos and the path of conduct that sustains harmony within it.",
    "logos": "Logos is a Greek philosophical concept describing the rational structure that makes the universe intelligible. It is the principle through which pattern, language, and meaning emerge.",
    "maat": "Ma'at in ancient Egyptian thought represents truth, balance, justice, and cosmic order. It is the equilibrium that keeps both society and the universe in harmony.",
    "dao": "The Dao is the underlying way or flow of reality in Chinese philosophy. It describes the natural unfolding of existence and the path of alignment with that spontaneous order.",
    "rta": "Rta is a Vedic concept referring to the cosmic order that governs the movement of the universe. It represents the harmony between natural law, moral truth, and the rhythm of existence.",
    "ayni": "Ayni is an Andean principle of sacred reciprocity. It expresses the understanding that balance in life is maintained through mutual exchange between people, community, and the living earth.",
    "ubuntu": "Ubuntu is an African philosophy of relational humanity. It teaches that a person becomes a person through other people, emphasizing compassion, shared dignity, and collective existence.",
    "mitakuye-oyasin": "Mitakuye Oyasin is a Lakota phrase meaning all my relations. It acknowledges the kinship of humans, animals, land, sky, and spirit as part of one living family.",
    "sumak-kawsay": "Sumak Kawsay is a Quechua concept meaning good living or living well. It describes a life lived in harmony with community and the natural world rather than through accumulation."
  };

  document.getElementById("drawer-title").textContent = titles[drawer] || "Drawer";
  document.getElementById("drawer-purpose").textContent = descriptions[drawer] || "";
  document.getElementById("drawer-esoteric").textContent = (drawer || "").replace(/-/g, " ").replace(/\b\w/g, function(c) { return c.toUpperCase(); });
  document.getElementById("drawer-explanation").textContent = explanations[drawer] || "";

  var url = SUPABASE_URL + "/rest/v1/artifacts?primary_drawer=eq." + drawer + "&state=eq.LIVE&select=id,title,era,row_class,confidence,primary_drawer&order=created_at.asc";

  fetch(url, {
    headers: {
      "apikey": ANON_KEY,
      "Authorization": "Bearer " + ANON_KEY,
      "Content-Type": "application/json"
    }
  })
  .then(function(response) { return response.json(); })
  .then(function(artifacts) {
    var list = document.getElementById("artifact-list");
    if (!list) return;

    list.innerHTML = "";

    if (!artifacts || artifacts.length === 0) {
      list.innerHTML = "<li>No entries in this drawer yet.</li>";
      return;
    }

    artifacts.forEach(function(artifact) {
      var li = document.createElement("li");
      li.style.marginBottom = "0.75em";

      var title = document.createElement("span");
      title.textContent = artifact.title;
      title.style.fontWeight = "600";

      var meta = document.createElement("span");
      var conf = artifact.confidence != null ? " · confidence " + parseFloat(artifact.confidence).toFixed(2) : "";
      var rc = artifact.row_class ? " · " + artifact.row_class : "";
      var era = artifact.era ? " · " + artifact.era : "";
      meta.textContent = conf + rc + era;
      meta.style.fontSize = "0.8em";
      meta.style.opacity = "0.6";
      meta.style.marginLeft = "0.5em";

      li.appendChild(title);
      li.appendChild(meta);
      list.appendChild(li);
    });
  })
  .catch(function(err) {
    var list = document.getElementById("artifact-list");
    if (list) list.innerHTML = "<li>Error loading artifacts.</li>";
    console.error("Supabase fetch error:", err);
  });

});