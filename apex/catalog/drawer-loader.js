document.addEventListener("DOMContentLoaded", () => {

const params = new URLSearchParams(window.location.search);
const drawer = params.get("drawer");

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

const explanations = {
  dharma: "Dharma is the principle of right order and right action in Indian philosophy. It refers both to the structure of the cosmos and the path of conduct that sustains harmony within it.",
  logos: "Logos is a Greek philosophical concept describing the rational structure that makes the universe intelligible. It is the principle through which pattern, language, and meaning emerge.",
  maat: "Ma'at in ancient Egyptian thought represents truth, balance, justice, and cosmic order. It is the equilibrium that keeps both society and the universe in harmony.",
  dao: "The Dao is the underlying way or flow of reality in Chinese philosophy. It describes the natural unfolding of existence and the path of alignment with that spontaneous order.",
  rta: "Ṛta is a Vedic concept referring to the cosmic order that governs the movement of the universe. It represents the harmony between natural law, moral truth, and the rhythm of existence.",
  ayni: "Ayni is an Andean principle of sacred reciprocity. It expresses the understanding that balance in life is maintained through mutual exchange between people, community, and the living earth.",
  ubuntu: "Ubuntu is an African philosophy of relational humanity. It teaches that a person becomes a person through other people, emphasizing compassion, shared dignity, and collective existence.",
  "mitakuye-oyasin": "Mitákuye Oyás'iŋ is a Lakota phrase meaning 'all my relations.' It acknowledges the kinship of humans, animals, land, sky, and spirit as part of one living family.",
  "sumak-kawsay": "Sumak Kawsay is a Quechua concept meaning 'good living' or 'living well.' It describes a life lived in harmony with community and the natural world rather than through accumulation."
};

const drawerEraMap = {
  dharma: "indexed",
  logos: null,
  maat: null,
  dao: null,
  rta: null,
  ayni: null,
  ubuntu: null,
  "mitakuye-oyasin": null,
  "sumak-kawsay": null
};

document.getElementById("drawer-title").textContent = titles[drawer] || "Drawer";
document.getElementById("drawer-purpose").textContent = descriptions[drawer] || "";
document.getElementById("drawer-esoteric").textContent =
  (drawer || "").replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
document.getElementById("drawer-explanation").textContent = explanations[drawer] || "";

fetch("/apex/canon/thread-catalog.json")
  .then(response => response.json())
  .then(data => {
    const list = document.getElementById("artifact-list");
    if (!list) return;

    const era = drawerEraMap[drawer];

    const relevantCards = era
      ? data.threads.filter(card => card.era === era)
      : [];

    list.innerHTML = "";

    if (relevantCards.length === 0) {
      list.innerHTML = "<li>No entries in this drawer yet.</li>";
      return;
    }

   relevantCards.forEach(card => {
  const li = document.createElement("li");
  const cleanTitle = card.title.replace(/^[∞⟁]\s*/, "");
  const sigil = card.sealed ? "⟁ " : "∞ ";
  const a = document.createElement("a");
  a.href = "https://rodzaki.github.io/site_builder/thread/" + card.id;
  a.textContent = sigil + cleanTitle;
  a.style.color = "inherit";
  li.appendChild(a);
  list.appendChild(li);
});
  })
  .catch(err => console.error("Card index load error:", err));

});