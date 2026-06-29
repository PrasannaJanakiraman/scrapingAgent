"use strict";

const API_BASE = "http://127.0.0.1:8001";

async function fetchItems(category, status, country) {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  if (status) params.set("status", status);
  if (country) params.set("country", country);
  const query = params.toString();
  const url = API_BASE + "/api/items" + (query ? "?" + query : "");

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Server returned " + response.status);
    return await response.json();
  } catch (error) {
    throw error;
  }
}

async function fetchFilters() {
  try {
    const response = await fetch(API_BASE + "/api/filters");
    if (!response.ok) throw new Error("Server returned " + response.status);
    return await response.json();
  } catch (error) {
    throw error;
  }
}

function showLoading() {
  const feed = document.querySelector(".feed");
  feed.innerHTML = '<div class="loading">Loading...</div>';
}

function showError(message) {
  const feed = document.querySelector(".feed");
  feed.innerHTML = '<div class="error-banner">' + escapeHtml(message) + "</div>";
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

/* Modal logic */
let isUploading = false;

function openModal() {
  document.getElementById("manage-sources-modal").classList.remove("hidden");
  document.getElementById("scrape-file-input").value = "";
  var statusEl = document.getElementById("upload-status");
  statusEl.textContent = "";
  statusEl.className = "upload-status";
  loadSourceTable();
}

async function loadSourceTable() {
  var container = document.getElementById("source-table-container");
  try {
    var data = await fetchItems();
    var items = data.items;

    if (!items || items.length === 0) {
      container.innerHTML = '<div class="source-table-empty">No sources have been added yet.</div>';
      return;
    }

    var table = document.createElement("table");
    table.className = "source-table";

    var thead = document.createElement("thead");
    thead.innerHTML = "<tr><th>Source ID</th><th>Source Name</th><th>Status</th><th>Scrape Date</th></tr>";
    table.appendChild(thead);

    var tbody = document.createElement("tbody");
    items.forEach(function (item) {
      var tr = document.createElement("tr");

      var tdId = document.createElement("td");
      tdId.textContent = item.sourceId || "-";

      var tdName = document.createElement("td");
      tdName.textContent = item.sourceName || "Unknown";

      var tdStatus = document.createElement("td");
      tdStatus.textContent = item.status || "-";

      var tdDate = document.createElement("td");
      tdDate.textContent = item.scrapeDate ? new Date(item.scrapeDate).toLocaleString() : "-";

      tr.appendChild(tdId);
      tr.appendChild(tdName);
      tr.appendChild(tdStatus);
      tr.appendChild(tdDate);
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.innerHTML = "";
    container.appendChild(table);
  } catch (error) {
    container.innerHTML = '<div class="source-table-empty">Unable to load source data.</div>';
  }
}

function closeModal() {
  document.getElementById("manage-sources-modal").classList.add("hidden");
}

/* File upload */
async function uploadFile() {
  var fileInput = document.getElementById("scrape-file-input");
  var uploadBtn = document.getElementById("upload-btn");
  var statusEl = document.getElementById("upload-status");

  if (!fileInput.files || fileInput.files.length === 0) {
    statusEl.textContent = "Please select a file first.";
    statusEl.className = "upload-status error";
    return;
  }

  var file = fileInput.files[0];
  if (!file.name.endsWith(".xlsx")) {
    statusEl.textContent = "Only .xlsx files are accepted.";
    statusEl.className = "upload-status error";
    return;
  }

  isUploading = true;
  uploadBtn.disabled = true;
  statusEl.textContent = "Scraping in progress...";
  statusEl.className = "upload-status loading";

  try {
    var formData = new FormData();
    formData.append("file", file);
    var response = await fetch(API_BASE + "/scrape", { method: "POST", body: formData });

    if (!response.ok) {
      var errorData = await response.json().catch(function () { return {}; });
      throw new Error(errorData.detail || "Server returned " + response.status);
    }

    statusEl.textContent = "Scrape completed successfully!";
    statusEl.className = "upload-status success";
    loadSourceTable();
    applyFilters();
  } catch (error) {
    statusEl.textContent = error.message || "Upload failed. Please try again.";
    statusEl.className = "upload-status error";
  } finally {
    isUploading = false;
    uploadBtn.disabled = false;
  }
}

let selectedCategory = null;
let selectedStatus = null;
let selectedCountry = null;

async function populateFilters() {
  try {
    const data = await fetchFilters();
    const categorySelect = document.getElementById("category-filter");
    data.categories.forEach(function (cat) {
      const option = document.createElement("option");
      option.value = cat;
      option.textContent = cat;
      categorySelect.appendChild(option);
    });

    const countrySelect = document.getElementById("country-filter");
    (data.countries || []).forEach(function (c) {
      const option = document.createElement("option");
      option.value = c;
      option.textContent = c;
      countrySelect.appendChild(option);
    });

  } catch (error) {
    // Filters unavailable — dropdowns remain with just "All"
  }
}

async function applyFilters() {
  showLoading();
  try {
    const data = await fetchItems(selectedCategory, selectedStatus, selectedCountry);
    renderCards(data.items);
  } catch (error) {
    showError("Unable to connect to the server. Please try again later.");
  }
}

function renderCards(items) {
  const feed = document.querySelector(".feed");
  feed.innerHTML = "";

  if (!items || items.length === 0) {
    var hasFilters = selectedCategory || selectedStatus || selectedCountry;
    var message = hasFilters ? "No items match your filters." : "No items available.";
    feed.innerHTML = '<div class="empty-state">' + escapeHtml(message) + "</div>";
    return;
  }

  items.forEach(function (item) {
    const card = document.createElement("div");
    card.className = "card";

    const title = document.createElement("div");
    title.className = "card-title";
    title.textContent = item.sourceName || (item.url ? item.url.substring(0, 60) : "Untitled");

    const summary = document.createElement("div");
    summary.className = "card-summary";
    summary.textContent = item.summary || "No summary available";

    const breadcrumb = document.createElement("div");
    breadcrumb.className = "card-breadcrumb";
    var parts = [item.country, item.category, item.status].filter(function (p) { return p; });
    breadcrumb.textContent = parts.join(" > ") || "Unknown";

    card.appendChild(title);
    card.appendChild(summary);
    card.appendChild(breadcrumb);
    feed.appendChild(card);
  });
}

async function init() {
  showLoading();
  try {
    await populateFilters();
    const data = await fetchItems();
    renderCards(data.items);
  } catch (error) {
    showError("Unable to connect to the server. Please try again later.");
  }

  document.getElementById("category-filter").addEventListener("change", function () {
    selectedCategory = this.value || null;
    applyFilters();
  });

  document.getElementById("country-filter").addEventListener("change", function () {
    selectedCountry = this.value || null;
    applyFilters();
  });

  document.getElementById("clear-filters").addEventListener("click", function () {
    selectedCategory = null;
    selectedCountry = null;
    document.getElementById("category-filter").value = "";
    document.getElementById("country-filter").value = "";
    applyFilters();
  });

  document.getElementById("manage-sources-btn").addEventListener("click", openModal);

  document.getElementById("upload-btn").addEventListener("click", function () {
    if (!isUploading) uploadFile();
  });

  document.querySelector(".modal-close").addEventListener("click", closeModal);

  document.getElementById("manage-sources-modal").addEventListener("click", function (e) {
    if (e.target === this) closeModal();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });
}

document.addEventListener("DOMContentLoaded", init);
