document.addEventListener("DOMContentLoaded", function() {

  var SUPABASE_URL = "https://wteqinxdavkpvufsjjse.supabase.co";
  var ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0ZXFpbnhkYXZrcHZ1ZnNqanNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA4MjE0NzEsImV4cCI6MjA4NjM5NzQ3MX0.mREQi5l3U1SBv3rtayTu3oZCORBgJrTfTBY5Lu02sAQ";

  var section = document.body.getAttribute("data-vault-section");
  if (!section) return;

  var url = SUPABASE_URL + "/rest/v1/vault_entries?vault_section=eq." + section + "&select=id,artifact_id,excerpt,display_blurb,sort_order,featured,display_date,external_url,artifacts(title,primary_drawer,row_class,era)&order=sort_order.asc,curated_at.asc";

  fetch(url, {
    headers: {
      "apikey": ANON_KEY,
      "Authorization": "Bearer " + ANON_KEY,
      "Content-Type": "application/json"
    }
  })
  .then(function(response) { return response.json(); })
  .then(function(entries) {
    var container = document.getElementById("vault-entries");
    if (!container) return;

    if (!entries || entries.length === 0) {
      container.innerHTML = "<p>(No entries in this section yet.)</p>";
      return;
    }

    var html = "";
    entries.forEach(function(entry) {
      var artifact = entry.artifacts || {};
      var title = artifact.title || "Untitled";
      var blurb = entry.display_blurb || entry.excerpt || "";
      var date = entry.display_date ? entry.display_date : "";
      var featured = entry.featured ? " vault-featured" : "";

      var linkOpen, linkClose;
      if (entry.external_url) {
        linkOpen = '<a href="' + entry.external_url + '" target="_blank" rel="noopener">';
        linkClose = "</a>";
      } else {
        linkOpen = "<span>";
        linkClose = "</span>";
      }

      html += '<div class="vault-entry' + featured + '">';
      html += "<div class=\"vault-entry-title\">" + linkOpen + title + linkClose + "</div>";
      if (blurb) html += "<div class=\"vault-entry-blurb\">" + blurb + "</div>";
      if (date) html += "<div class=\"vault-entry-date\">" + date + "</div>";
      if (entry.external_url) html += "<div class=\"vault-entry-link\"><a href=\"" + entry.external_url + "\" target=\"_blank\" rel=\"noopener\">Read on Substack →</a></div>";
      html += "</div>";
    });

    container.innerHTML = html;
  })
  .catch(function(err) {
    var container = document.getElementById("vault-entries");
    if (container) container.innerHTML = "<p>Error loading entries.</p>";
    console.error("Vault load error:", err);
  });

});