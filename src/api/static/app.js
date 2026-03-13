const recipeSelect = document.getElementById("recipe-select");
const dateInput = document.getElementById("date-input");
const quoteForm = document.getElementById("quote-form");
const submitButton = document.getElementById("submit-button");
const formMessage = document.getElementById("form-message");
const resultPanel = document.getElementById("result-panel");
const resultTitle = document.getElementById("result-title");
const resultDate = document.getElementById("result-date");
const totalArs = document.getElementById("total-ars");
const totalUsd = document.getElementById("total-usd");
const fxRate = document.getElementById("fx-rate");
const ingredientsBody = document.getElementById("ingredients-body");
const instructions = document.getElementById("instructions");

function formatMoney(value, prefix = "") {
  return `${prefix}${Number(value).toFixed(2)}`;
}

function setMessage(message, type = "") {
  formMessage.textContent = message;
  formMessage.className = `form-message ${type}`.trim();
}

function setDateBounds() {
  const today = new Date();
  const minDate = new Date(today);
  minDate.setDate(today.getDate() - 30);

  dateInput.max = today.toISOString().slice(0, 10);
  dateInput.min = minDate.toISOString().slice(0, 10);
  dateInput.value = today.toISOString().slice(0, 10);
}

async function loadRecipes() {
  try {
    const response = await fetch("/api/recetas");
    if (!response.ok) {
      throw new Error("No se pudieron cargar las recetas.");
    }

    const data = await response.json();
    recipeSelect.innerHTML = "";

    for (const recipe of data.recetas) {
      const option = document.createElement("option");
      option.value = recipe;
      option.textContent = recipe;
      recipeSelect.appendChild(option);
    }

    setMessage("");
  } catch (error) {
    recipeSelect.innerHTML = '<option value="">No se pudieron cargar</option>';
    setMessage(error.message, "error");
  }
}

function renderQuote(quote) {
  resultTitle.textContent = quote.receta;
  resultDate.textContent = quote.fecha;
  totalArs.textContent = formatMoney(quote.total_ars, "ARS ");
  totalUsd.textContent = formatMoney(quote.total_usd, "USD ");
  fxRate.textContent = quote.cotizacion_usd_ars;
  instructions.textContent = quote.instrucciones;

  ingredientsBody.innerHTML = "";
  for (const ingredient of quote.ingredientes) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${ingredient.nombre_producto}</td>
      <td>${ingredient.cantidad_receta_gramos} g</td>
      <td>${ingredient.cantidad_compra_gramos} g</td>
      <td>ARS ${formatMoney(ingredient.precio_kg_ars)}</td>
      <td>ARS ${formatMoney(ingredient.subtotal_ars)}</td>
    `;
    ingredientsBody.appendChild(row);
  }

  resultPanel.classList.remove("hidden");
}

async function submitQuote(event) {
  event.preventDefault();
  setMessage("");
  submitButton.disabled = true;
  submitButton.textContent = "Cotizando...";

  const params = new URLSearchParams({
    receta: recipeSelect.value,
    fecha: dateInput.value,
  });

  try {
    const response = await fetch(`/api/cotizacion?${params.toString()}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "No se pudo obtener la cotizacion.");
    }

    renderQuote(data.cotizacion);
  } catch (error) {
    resultPanel.classList.add("hidden");
    setMessage(error.message, "error");
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Cotizar receta";
  }
}

setDateBounds();
loadRecipes();
quoteForm.addEventListener("submit", submitQuote);
