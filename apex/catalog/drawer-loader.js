const path = window.location.pathname;
const parts = path.split("/");

const drawer = parts[parts.length - 2];

const titles = {
  dharma: "Master Index",
  logos: "Artifact Catalog",
  maat: "Canon / Protocol",
  dao: "Publications",
  rta: "Works / Core",
  ayni: "Serial",
  ubuntu: "Essays",
  "mitakuye-oyasin": "Notes",
  "sumak-kawsay": "Backlog"
};

const descriptions = {
  dharma: "Governing memory and canonical entry points.",
  logos: "Structural catalog of all versioned artifacts.",
  maat: "Rules, protocols, and governing frameworks.",
  dao: "Published materials and formal releases.",
  rta: "Core operational works.",
  ayni: "Serialized material streams.",
  ubuntu: "Essay and reflection layer.",
  "mitakuye-oyasin": "Working notes and fragments.",
  "sumak-kawsay": "Backlog and future development."
};

document.getElementById("drawer-title").textContent =
  titles[drawer] || "Drawer";

document.getElementById("drawer-description").textContent =
  descriptions[drawer] || "Archive artifacts belonging to this structural layer.";