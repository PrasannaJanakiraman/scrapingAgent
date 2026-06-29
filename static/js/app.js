"use strict";

const API_BASE = (location.hostname === "localhost" || location.hostname === "127.0.0.1")
  ? "http://127.0.0.1:8001"
  : "https://scrapingagent-c6f0c9c6fzd0hmhk.eastus2-01.azurewebsites.net";
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

function openDetailModal(item) {
  document.getElementById("detail-title").textContent = item.sourceName || "Untitled";
  document.getElementById("detail-category").textContent = item.category || "";
  document.getElementById("detail-country").textContent = item.country || "";
  document.getElementById("detail-summary").textContent = item.summary || "No summary available";
  document.getElementById("detail-scraped").textContent = item.scrapedData || "No content available";
  document.getElementById("detail-modal").classList.remove("hidden");
}

function closeDetailModal() {
  document.getElementById("detail-modal").classList.add("hidden");
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
let currentPage = 1;
const PAGE_SIZE = 5;
let allItems = [];

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
    allItems = data.items || [];
    currentPage = 1;
    renderPage();
  } catch (error) {
    showError("Unable to connect to the server. Please try again later.");
  }
}

function renderPage() {
  var totalPages = Math.max(1, Math.ceil(allItems.length / PAGE_SIZE));
  if (currentPage > totalPages) currentPage = totalPages;
  var start = (currentPage - 1) * PAGE_SIZE;
  var pageItems = allItems.slice(start, start + PAGE_SIZE);
  renderCards(pageItems);
  renderPagination(totalPages);
}

function renderPagination(totalPages) {
  var existing = document.querySelector(".pagination");
  if (existing) existing.remove();

  if (allItems.length <= PAGE_SIZE) return;

  var feed = document.querySelector(".feed");
  var pag = document.createElement("div");
  pag.className = "pagination";

  var prevBtn = document.createElement("button");
  prevBtn.className = "pagination-btn";
  prevBtn.textContent = "Previous";
  prevBtn.disabled = currentPage <= 1;
  prevBtn.addEventListener("click", function () {
    if (currentPage > 1) { currentPage--; renderPage(); }
  });

  var info = document.createElement("span");
  info.className = "pagination-info";
  info.textContent = "Page " + currentPage + " of " + totalPages;

  var nextBtn = document.createElement("button");
  nextBtn.className = "pagination-btn";
  nextBtn.textContent = "Next";
  nextBtn.disabled = currentPage >= totalPages;
  nextBtn.addEventListener("click", function () {
    if (currentPage < totalPages) { currentPage++; renderPage(); }
  });

  pag.appendChild(prevBtn);
  pag.appendChild(info);
  pag.appendChild(nextBtn);
  feed.appendChild(pag);
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
    [item.category, item.country].forEach(function (val) {
      if (!val) return;
      var tag = document.createElement("span");
      tag.className = "detail-tag";
      tag.textContent = val;
      breadcrumb.appendChild(tag);
    });

    var viewBtn = document.createElement("button");
    viewBtn.className = "view-btn";
    viewBtn.textContent = "View";
    viewBtn.addEventListener("click", function () { openDetailModal(item); });

    var cardFooter = document.createElement("div");
    cardFooter.className = "card-footer";
    cardFooter.appendChild(breadcrumb);
    cardFooter.appendChild(viewBtn);

    card.appendChild(title);
    card.appendChild(summary);
    card.appendChild(cardFooter);
    feed.appendChild(card);
  });
}

async function init() {
  showLoading();
  try {
    await populateFilters();
    const data = await fetchItems();
    allItems = data.items || [];
    currentPage = 1;
    renderPage();
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

  document.getElementById("detail-modal-close").addEventListener("click", closeDetailModal);

  document.getElementById("detail-modal").addEventListener("click", function (e) {
    if (e.target === this) closeDetailModal();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeModal();
      closeDetailModal();
    }
  });
}

document.addEventListener("DOMContentLoaded", init);
