const state = {
  competitors: [],
  history: [],
  currentSection: "dashboard",
  resultsBySection: {},
  progressTimer: null,
  progress: 0,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const scoreLabels = {
  offer_score: "Оффер",
  differentiation_score: "Отличие от конкурентов",
  design_score: "Дизайн",
  trust_score: "Доверие",
  content_clarity: "Понятность контента",
  automation_focus: "Фокус на автоматизации",
  automation_relevance: "Релевантность автоматизации",
  conversion_potential: "Потенциал конверсии",
  animation_potential: "Потенциал анимации",
  visual_style_score: "Визуальный стиль",
  clarity_score: "Ясность",
  cta_score: "Призыв к действию",
};

const typeLabels = {
  text: "Текст",
  image: "Изображение",
  site: "Сайт",
  compare: "Сравнение",
};

function contextPayload() {
  return {
    niche: $("#niche").value,
    custom_niche: $("#customNiche").value || null,
    own_brand: $("#ownBrand").value || "NeiroBridge",
    own_site: $("#ownSite").value || null,
    target_audience: $("#targetAudience").value || null,
  };
}

function setLoading(isLoading, text = "Подготовка запроса...") {
  $("#loading").classList.toggle("hidden", !isLoading);
  $("#progressBox").classList.toggle("hidden", !isLoading);
  $$("button").forEach((button) => {
    button.disabled = isLoading;
  });

  if (isLoading) {
    state.progress = 8;
    updateProgress(state.progress, text);
    state.progressTimer = window.setInterval(() => {
      state.progress = Math.min(92, state.progress + Math.max(1, Math.round((95 - state.progress) / 8)));
      const currentText = state.progress < 35
        ? "Собираю данные..."
        : state.progress < 70
          ? "Отправляю данные в AI..."
          : "Формирую структурированный отчет...";
      updateProgress(state.progress, currentText);
    }, 900);
  } else {
    window.clearInterval(state.progressTimer);
    updateProgress(100, "Готово");
    window.setTimeout(() => {
      $("#progressBox").classList.add("hidden");
      $("#progressBar").style.width = "0%";
      $("#progressValue").textContent = "0%";
    }, 500);
  }
}

function updateProgress(value, text) {
  $("#progressBar").style.width = `${value}%`;
  $("#progressValue").textContent = `${value}%`;
  $("#progressText").textContent = text;
}

function showResultPanel() {
  $("#resultPanel").classList.remove("hidden");
}

function hideResultPanel() {
  $("#resultPanel").classList.add("hidden");
}

function renderList(title, items = []) {
  if (!items.length) return "";
  return `<h3>${title}</h3><ul>${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
}

function scoreLabel(key) {
  return scoreLabels[key] || key.replaceAll("_", " ");
}

function renderComparison(data) {
  showResultPanel();
  const scores = data.scores || {};
  const scoreHtml = Object.entries(scores)
    .map(
      ([key, value]) => `
        <div class="score">
          <span>${scoreLabel(key)}</span>
          <strong>${value} / 10</strong>
        </div>
      `,
    )
    .join("");
  const cardsHtml = (data.competitor_cards || [])
    .map(
      (card) => `
        <article class="comparison-card">
          <div class="comparison-card-head">
            <h3>${card.name || "Конкурент"}</h3>
            <span class="threat ${card.threat_level || "средний"}">Угроза: ${card.threat_level || "средний"}</span>
          </div>
          <p>${card.positioning || "Позиционирование не указано"}</p>
          ${renderList("Сильные стороны", card.strengths)}
          ${renderList("Слабые стороны", card.weaknesses)}
          ${renderList("Что можно перенять", card.what_to_learn)}
        </article>
      `,
    )
    .join("");
  const tableHtml = (data.comparison_table || [])
    .map(
      (row) => `
        <tr>
          <th>${row.criterion || "Критерий"}</th>
          <td>${row.own_brand || "Нет данных"}</td>
          <td>${(row.competitors || [])
            .map((item) => `<strong>${item.name}:</strong> ${item.value}`)
            .join("<br>")}</td>
          <td>${row.recommendation || "Нет рекомендации"}</td>
        </tr>
      `,
    )
    .join("");

  $("#result").classList.remove("empty");
  $("#result").innerHTML = `
    <h3>Краткий вывод по сравнению</h3>
    <p>${data.summary || "Сравнение выполнено."}</p>
    ${scoreHtml ? `<div class="score-grid">${scoreHtml}</div>` : ""}
    <h3>Карточки конкурентов</h3>
    <div class="comparison-grid">${cardsHtml || "<p>Карточки конкурентов не сформированы.</p>"}</div>
    <h3>Сравнительная таблица</h3>
    <div class="table-wrap">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Критерий</th>
            <th>Мой бренд</th>
            <th>Конкуренты</th>
            <th>Что улучшить</th>
          </tr>
        </thead>
        <tbody>${tableHtml}</tbody>
      </table>
    </div>
    ${renderList("Рекомендации для моего бренда", data.brand_recommendations)}
    ${renderList("Быстрые улучшения", data.quick_wins)}
    ${renderList("Стратегические шаги", data.strategic_moves)}
    ${renderList("Риски", data.risks)}
  `;
}

function renderResult(data) {
  showResultPanel();
  const result = data.analysis || data;
  if (result.type === "comparison" || result.comparison_table || result.competitor_cards) {
    renderComparison(result);
    return;
  }
  const parsed = data.parsed;
  const scores = result.scores || {};
  const scoreHtml = Object.entries(scores)
    .map(
      ([key, value]) => `
        <div class="score">
          <span>${scoreLabel(key)}</span>
          <strong>${value} / 10</strong>
        </div>
      `,
    )
    .join("");

  $("#result").classList.remove("empty");
  $("#result").innerHTML = `
    ${parsed ? `<p><strong>URL:</strong> ${parsed.url}</p><p><strong>Заголовок страницы:</strong> ${parsed.title || "не найден"}</p>` : ""}
    <h3>Краткий вывод</h3>
    <p>${result.summary || result.description || "Нет краткого вывода"}</p>
    ${scoreHtml ? `<div class="score-grid">${scoreHtml}</div>` : ""}
    ${renderList("Сильные стороны", result.strengths)}
    ${renderList("Слабые стороны", result.weaknesses)}
    ${renderList("УТП / уникальные предложения", result.unique_offers)}
    ${renderList("Маркетинговые инсайты", result.marketing_insights)}
    ${result.visual_style_analysis ? `<h3>Визуальный стиль</h3><p>${result.visual_style_analysis}</p>` : ""}
    ${result.animation_potential ? `<h3>Потенциал анимации</h3><p>${result.animation_potential}</p>` : ""}
    ${renderList("Разрыв в позиционировании", result.positioning_gap)}
    ${renderList("Рекомендации", result.recommendations)}
    ${renderList("План действий", result.action_plan)}
  `;
}

async function api(path, options = {}, progressText = "Подготовка запроса...") {
  const section = state.currentSection;
  setLoading(true, progressText);
  try {
    const response = await fetch(path, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Ошибка запроса");
    state.resultsBySection[section] = data;
    renderResult(data);
    return data;
  } catch (error) {
    showResultPanel();
    $("#result").innerHTML = `<p class="error">${error.message}</p>`;
  } finally {
    setLoading(false);
  }
}

async function loadHealth() {
  try {
    const response = await fetch("/health");
    const data = await response.json();
    $("#healthStatus").textContent = data.ai_provider === "not configured"
      ? "Нужен PROXY_API_KEY"
      : `API готов: ${data.ai_provider}`;
  } catch {
    $("#healthStatus").textContent = "API недоступен";
  }
}

async function loadCompetitors() {
  const response = await fetch("/competitors");
  const saved = localStorage.getItem("rivalscope_competitors");
  state.competitors = saved ? JSON.parse(saved) : await response.json();
  renderCompetitors();
}

function saveCompetitors() {
  localStorage.setItem("rivalscope_competitors", JSON.stringify(state.competitors));
}

function renderCompetitors() {
  $("#competitorCards").innerHTML = state.competitors
    .map((item, index) => `
        <article class="competitor-card">
          <span>${item.role === "own_brand" ? "мой бренд" : "конкурент"}</span>
          <h3>${item.name}</h3>
          <p>${item.positioning}</p>
          <div class="card-actions">
            <button class="secondary analyze-demo" data-url="${item.url}">Анализ сайта</button>
            <button class="secondary danger-btn remove-competitor" data-index="${index}">Удалить</button>
          </div>
        </article>
      `,
    )
    .join("");

  $$(".analyze-demo").forEach((button) => {
    button.addEventListener("click", () => {
      $("#siteUrl").value = button.dataset.url;
      showSection("site");
      analyzeSite();
    });
  });

  $$(".remove-competitor").forEach((button) => {
    button.addEventListener("click", () => {
      state.competitors.splice(Number(button.dataset.index), 1);
      saveCompetitors();
      renderCompetitors();
    });
  });
}

function addCompetitor() {
  const name = $("#competitorName").value.trim();
  const url = $("#competitorUrl").value.trim();
  const note = $("#competitorNote").value.trim();
  if (!name || !url) {
    showResultPanel();
    $("#result").innerHTML = `<p class="error">Укажите название и URL конкурента.</p>`;
    return;
  }

  state.competitors.push({
    name,
    url,
    role: "competitor",
    positioning: note || "Пользовательский конкурент",
  });
  saveCompetitors();
  renderCompetitors();
  $("#competitorName").value = "";
  $("#competitorUrl").value = "";
  $("#competitorNote").value = "";
}

function showSection(id) {
  state.currentSection = id;
  $$(".section").forEach((section) => section.classList.remove("active"));
  $(`#${id}`).classList.add("active");
  $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.section === id));

  const savedResult = state.resultsBySection[id];
  if (id === "dashboard" || !savedResult) {
    hideResultPanel();
    return;
  }
  renderResult(savedResult);
}

async function analyzeSite() {
  await api("/parse_demo", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url: $("#siteUrl").value,
      use_selenium: $("#useSelenium").checked,
      context: contextPayload(),
    }),
  }, "Открываю сайт и собираю данные...");
}

async function analyzeText() {
  await api("/analyze_text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: $("#textInput").value,
      context: contextPayload(),
    }),
  }, "Анализирую текст конкурента...");
}

async function analyzeImage() {
  const file = $("#imageInput").files[0];
  if (!file) {
    showResultPanel();
    $("#result").innerHTML = `<p class="error">Выберите изображение.</p>`;
    return;
  }
  const form = new FormData();
  form.append("file", file);
  form.append("context_json", JSON.stringify(contextPayload()));
  await api("/analyze_image", {
    method: "POST",
    body: form,
  }, "Загружаю изображение и отправляю в Vision...");
}

async function compareCompetitors() {
  const competitors = state.competitors.filter((item) => item.role !== "own_brand");
  if (competitors.length < 2) {
    showResultPanel();
    $("#result").innerHTML = `<p class="error">Добавьте минимум двух конкурентов для сравнения.</p>`;
    return;
  }

  await api("/compare_competitors", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      competitors: competitors.map((item) => ({
        name: item.name,
        url: item.url,
        note: item.positioning,
      })),
      context: contextPayload(),
    }),
  }, "Сравниваю конкурентов...");
}

async function loadHistory() {
  const response = await fetch("/history");
  const data = await response.json();
  state.history = data.items;
  $("#historyList").innerHTML = data.items.length
    ? data.items
        .map(
          (item, index) => `
            <button class="history-item" data-index="${index}">
              <strong>${typeLabels[item.type] || item.type}</strong>
              <span>${item.title}</span>
              <small>${new Date(item.created_at).toLocaleString("ru-RU")}</small>
            </button>
          `,
        )
        .join("")
    : "История пока пустая.";

  $$(".history-item").forEach((button) => {
    button.addEventListener("click", () => renderHistoryItem(Number(button.dataset.index)));
  });
}

function renderHistoryItem(index) {
  const item = state.history[index];
  if (!item) return;
  const payload = item.payload || {};
  const data = payload.analysis
    ? { parsed: payload.parsed, analysis: payload.analysis }
    : payload.result || payload;
  state.resultsBySection.history = data;
  renderResult(data);
  $("#result").scrollIntoView({ behavior: "smooth", block: "start" });
}

$$(".nav-item").forEach((item) => item.addEventListener("click", () => showSection(item.dataset.section)));
$("#addCompetitorBtn").addEventListener("click", addCompetitor);
$("#analyzeSiteBtn").addEventListener("click", analyzeSite);
$("#analyzeTextBtn").addEventListener("click", analyzeText);
$("#analyzeImageBtn").addEventListener("click", analyzeImage);
$("#compareBtn").addEventListener("click", compareCompetitors);
$("#refreshHistoryBtn").addEventListener("click", loadHistory);

loadHealth();
loadCompetitors();
loadHistory();
