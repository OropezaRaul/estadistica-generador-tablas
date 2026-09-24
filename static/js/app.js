/**
 * Lógica Frontend - Sistema Estadístico Web Interactivo
 * Gestión de pestañas, peticiones a la API y renderizado dinámico de tarjetas y gráficas.
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initGenerador();
  initResolver();
  initTablas();
});

// ==========================================================================
// 1. GESTIÓN DE PESTAÑAS
// ==========================================================================
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      
      tabBtns.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }

      // Si entra a la pestaña de tablas y está vacía, cargar Z por defecto
      if (targetId === "tab-tablas" && !document.getElementById("tabla-container").hasChildNodes()) {
        cargarTabla("z");
      }
    });
  });
}

// ==========================================================================
// 2. GENERADOR DE EJERCICIOS (TAB 1)
// ==========================================================================
let ejerciciosGeneradosActuales = [];

function initGenerador() {
  const distCards = document.querySelectorAll(".gen-dist-card");
  const dfGroup = document.getElementById("gen-param-df-group");
  const fisherGroup = document.getElementById("gen-param-fisher-group");

  // Selección de distribución
  distCards.forEach(card => {
    card.addEventListener("click", () => {
      distCards.forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      const radio = card.querySelector('input[type="radio"]');
      if (radio) radio.checked = true;

      const dist = radio.value;
      if (dist === "t" || dist === "chi") {
        dfGroup.style.display = "block";
        fisherGroup.style.display = "none";
      } else if (dist === "fisher") {
        dfGroup.style.display = "none";
        fisherGroup.style.display = "flex";
      } else {
        dfGroup.style.display = "none";
        fisherGroup.style.display = "none";
      }
    });
  });

  // Función para actualizar el cálculo dinámico del total de ejercicios
  function actualizarCalculoTotal() {
    const totalChips = document.querySelectorAll(".criterion-chip.active").length;
    const inputCant = document.getElementById("gen-cantidad");
    const cant = Math.max(1, parseInt(inputCant ? inputCant.value : 1) || 1);
    const calcEl = document.getElementById("gen-total-calc");
    if (calcEl) {
      calcEl.innerText = `Total: ${totalChips} tipo(s) seleccionados × ${cant} = ${totalChips * cant} ejercicios a generar`;
    }
  }

  // Filtros de criterios (Shortcuts)
  const chips = document.querySelectorAll(".criterion-chip");
  
  document.getElementById("btn-crit-all")?.addEventListener("click", () => {
    chips.forEach(c => c.classList.add("active"));
    actualizarCalculoTotal();
  });

  document.getElementById("btn-crit-tails")?.addEventListener("click", () => {
    chips.forEach(c => {
      const id = parseInt(c.getAttribute("data-id"));
      if (id >= 1 && id <= 4) c.classList.add("active");
      else c.classList.remove("active");
    });
    actualizarCalculoTotal();
  });

  document.getElementById("btn-crit-intervals")?.addEventListener("click", () => {
    chips.forEach(c => {
      const id = parseInt(c.getAttribute("data-id"));
      if (id >= 5 && id <= 7) c.classList.add("active");
      else c.classList.remove("active");
    });
    actualizarCalculoTotal();
  });

  document.getElementById("btn-crit-inverse")?.addEventListener("click", () => {
    chips.forEach(c => {
      const id = parseInt(c.getAttribute("data-id"));
      if (id >= 8 && id <= 11) c.classList.add("active");
      else c.classList.remove("active");
    });
    actualizarCalculoTotal();
  });

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chip.classList.toggle("active");
      actualizarCalculoTotal();
    });
  });

  document.getElementById("gen-cantidad")?.addEventListener("input", actualizarCalculoTotal);

  // Botón Generar Ejercicios
  document.getElementById("btn-generar")?.addEventListener("click", async () => {
    const distChecked = document.querySelector('input[name="gen-dist"]:checked');
    const dist = distChecked ? distChecked.value : "z";

    const criterios = [];
    document.querySelectorAll(".criterion-chip.active").forEach(c => {
      criterios.push(parseInt(c.getAttribute("data-id")));
    });

    if (criterios.length === 0) {
      alert("Por favor selecciona al menos un criterio analítico.");
      return;
    }

    const cantidad = parseInt(document.getElementById("gen-cantidad").value) || 5;
    const dfVal = parseInt(document.getElementById("gen-df").value) || null;
    const r1Val = parseInt(document.getElementById("gen-r1").value) || null;
    const r2Val = parseInt(document.getElementById("gen-r2").value) || null;

    const payload = {
      dist: dist,
      criterios: criterios,
      cantidad_por_tipo: cantidad,
      params: {
        df: dfVal,
        r1: r1Val,
        r2: r2Val
      }
    };

    const loadingBox = document.getElementById("gen-loading");
    const resultsContainer = document.getElementById("gen-results-list");
    const resultsPanel = document.getElementById("gen-results-panel");
    const emptyState = document.getElementById("gen-empty-state");

    loadingBox.style.display = "block";
    resultsContainer.innerHTML = "";
    if (emptyState) emptyState.style.display = "none";
    resultsPanel.style.display = "none";

    try {
      const res = await fetch("/api/generar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      
      loadingBox.style.display = "none";
      if (!res.ok) {
        alert("Error al generar ejercicios: " + (data.error || "Error de servidor"));
        return;
      }

      ejerciciosGeneradosActuales = data.ejercicios || [];
      renderizarResultadosGenerados(ejerciciosGeneradosActuales);
      resultsPanel.style.display = "block";

    } catch (err) {
      loadingBox.style.display = "none";
      alert("Error de conexión al generar ejercicios: " + err.message);
    }
  });

  // Botón Generar Guía Completa de 176 Ejercicios desde la Web
  const btnGuiaCompleta = document.getElementById("btn-guia-completa-web");
  btnGuiaCompleta?.addEventListener("click", async () => {
    const originalText = btnGuiaCompleta.innerHTML;
    btnGuiaCompleta.disabled = true;
    btnGuiaCompleta.innerHTML = `
      <span class="spinner" style="width: 14px; height: 14px; margin: 0; display: inline-block; vertical-align: middle; border-width: 2px;"></span>
      Compilando 176 ejercicios (~20 seg)...
    `;

    try {
      const res = await fetch("/api/generar-guia-completa", { method: "POST" });
      if (!res.ok) {
        alert("Error al generar la guía completa.");
        btnGuiaCompleta.disabled = false;
        btnGuiaCompleta.innerHTML = originalText;
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Guia_Completa_176_Ejercicios_Estadistica.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      
      btnGuiaCompleta.disabled = false;
      btnGuiaCompleta.innerHTML = originalText;
      alert("¡Guía completa de 176 ejercicios generada y descargada exitosamente! Se guardó una copia en la carpeta 'Resultados/'.");
    } catch (err) {
      btnGuiaCompleta.disabled = false;
      btnGuiaCompleta.innerHTML = originalText;
      alert("Error al compilar la guía: " + err.message);
    }
  });

  // Botón Descargar PDF personalizado
  document.getElementById("btn-descargar-pdf")?.addEventListener("click", async () => {
    if (ejerciciosGeneradosActuales.length === 0) return;

    try {
      const res = await fetch("/api/exportar-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ejercicios: ejerciciosGeneradosActuales })
      });

      if (!res.ok) {
        alert("Error al compilar el PDF");
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Guia_Personalizada_${ejerciciosGeneradosActuales.length}_Ejercicios.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert("Error al descargar PDF: " + e.message);
    }
  });
}

function renderizarResultadosGenerados(ejercicios) {
  const container = document.getElementById("gen-results-list");
  container.innerHTML = "";

  document.getElementById("gen-stats-text").innerText = 
    `Se generaron ${ejercicios.length} ejercicios analíticos con sus gráficas:`;

  ejercicios.forEach(ej => {
    const card = document.createElement("div");
    card.className = "exercise-card";

    // Formatear resolución con saltos y negritas
    const resolucionHtml = formatearResolucionTexto(ej.resolucion);
    const ordenLimpia = limpiarFormula(ej.orden);

    card.innerHTML = `
      <div class="exercise-left">
        <div class="exercise-badge-row">
          <span class="badge-pill">${ej.distribucion}</span>
          <span class="badge-pill crit">Caso: ${ej.criterio_nombre}</span>
        </div>

        <div class="box-orden">
          <div class="box-orden-title">1. Orden del Ejercicio</div>
          <div class="box-orden-formula">${ordenLimpia}</div>
        </div>

        <div class="box-resolucion">
          <div class="box-resolucion-title">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
            2. Resolución Analítica Paso a Paso
          </div>
          <div class="box-resolucion-body">${resolucionHtml}</div>
        </div>
      </div>

      <div class="exercise-right">
        <div class="box-orden-title" style="align-self: flex-start;">3. Gráfica de la Distribución</div>
        <img class="plot-img" src="${ej.grafico_base64}" alt="Curva de densidad">
        <div class="plot-actions">
          <a class="btn-download-img" href="${ej.grafico_base64}" download="ejercicio_${ej.id}.png">
            <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
            Descargar Gráfica PNG
          </a>
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}

// ==========================================================================
// 3. RESOLVEDOR PERSONALIZADO (TAB 2)
// ==========================================================================
function initResolver() {
  const distSelect = document.getElementById("res-dist");
  const dfGroup = document.getElementById("res-df-group");
  const r1Group = document.getElementById("res-r1-group");
  const r2Group = document.getElementById("res-r2-group");
  const opSelect = document.getElementById("res-op");
  const valGroup1 = document.getElementById("res-val1-group");
  const valGroup2 = document.getElementById("res-val2-group");
  const val1Label = document.getElementById("res-val1-label");

  // Cambio de distribución
  distSelect?.addEventListener("change", () => {
    const dist = distSelect.value;
    if (dist === "t" || dist === "chi") {
      dfGroup.style.display = "block";
      r1Group.style.display = "none";
      r2Group.style.display = "none";
    } else if (dist === "fisher") {
      dfGroup.style.display = "none";
      r1Group.style.display = "block";
      r2Group.style.display = "block";
    } else {
      dfGroup.style.display = "none";
      r1Group.style.display = "none";
      r2Group.style.display = "none";
    }
  });

  // Cambio de operación
  opSelect?.addEventListener("change", () => {
    const op = opSelect.value;
    if (op === "intervalo") {
      val1Label.innerText = "Límite inferior 'a':";
      valGroup2.style.display = "block";
    } else if (op.startsWith("inv_")) {
      val1Label.innerText = "Probabilidad 'p' (entre 0 y 1):";
      valGroup2.style.display = "none";
    } else {
      val1Label.innerText = "Punto crítico 'a':";
      valGroup2.style.display = "none";
    }
  });

  // Botón Resolver
  document.getElementById("btn-resolver")?.addEventListener("click", async () => {
    const dist = distSelect.value;
    const op = opSelect.value;
    const modoSalida = document.querySelector('input[name="res-modo"]:checked')?.value || "full";
    const v1 = parseFloat(document.getElementById("res-val1").value);
    
    let valores = v1;
    if (op === "intervalo") {
      const v2 = parseFloat(document.getElementById("res-val2").value);
      if (isNaN(v1) || isNaN(v2)) {
        alert("Por favor ingresa ambos límites para el intervalo.");
        return;
      }
      valores = [v1, v2];
    } else if (isNaN(v1)) {
      alert("Por favor ingresa un valor numérico válido.");
      return;
    }

    const payload = {
      dist: dist,
      op: op,
      val: valores,
      modo: modoSalida,
      df: parseInt(document.getElementById("res-df").value) || 10,
      r1: parseInt(document.getElementById("res-r1").value) || 5,
      r2: parseInt(document.getElementById("res-r2").value) || 10
    };

    const container = document.getElementById("res-result-card");
    container.style.display = "none";

    try {
      const res = await fetch("/api/resolver", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      
      if (!res.ok) {
        alert("Error al resolver: " + (data.error || "Datos inválidos"));
        return;
      }

      renderizarResultadoPuntual(data, modoSalida);
      container.style.display = "grid";
      container.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
      alert("Error de conexión: " + err.message);
    }
  });
}

function renderizarResultadoPuntual(ej, modo) {
  const container = document.getElementById("res-result-card");
  const ordenLimpia = limpiarFormula(ej.orden);
  const resolucionHtml = formatearResolucionTexto(ej.resolucion);

  let leftContent = `
    <div class="exercise-badge-row">
      <span class="badge-pill">${ej.distribucion}</span>
      <span class="badge-pill crit">Caso: ${ej.criterio_nombre}</span>
    </div>

    <div class="box-orden">
      <div class="box-orden-title">1. Orden del Ejercicio</div>
      <div class="box-orden-formula">${ordenLimpia}</div>
    </div>
  `;

  if (modo !== "grafico") {
    leftContent += `
      <div class="box-resolucion">
        <div class="box-resolucion-title">2. Resolución Analítica</div>
        <div class="box-resolucion-body">${resolucionHtml}</div>
      </div>
    `;
  }

  let rightContent = "";
  if (modo !== "resolucion") {
    rightContent = `
      <div class="exercise-right">
        <div class="box-orden-title" style="align-self: flex-start;">3. Gráfica de la Distribución</div>
        <img class="plot-img" src="${ej.grafico_base64}" alt="Gráfica">
        <div class="plot-actions">
          <a class="btn-download-img" href="${ej.grafico_base64}" download="grafica_personalizada.png">
            Descargar Gráfica PNG
          </a>
        </div>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="exercise-left">${leftContent}</div>
    ${rightContent}
  `;
}

// ==========================================================================
// 4. EXPLORADOR DE TABLAS OFICIALES (TAB 3)
// ==========================================================================
function initTablas() {
  const btns = document.querySelectorAll(".btn-tbl-tab");
  btns.forEach(btn => {
    btn.addEventListener("click", () => {
      btns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const dist = btn.getAttribute("data-tbl");
      cargarTabla(dist);
    });
  });
}

async function cargarTabla(dist) {
  const container = document.getElementById("tabla-container");
  container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--text-muted);">Cargando tabla oficial...</div>';

  try {
    const res = await fetch(`/api/tablas/${dist}`);
    const data = await res.json();

    if (!res.ok) {
      container.innerHTML = `<div style="padding: 2rem; color: var(--accent);">Error al cargar tabla: ${data.error}</div>`;
      return;
    }

    renderizarMatrizHTML(dist, data, container);
  } catch (err) {
    container.innerHTML = `<div style="padding: 2rem; color: var(--accent);">Error de conexión: ${err.message}</div>`;
  }
}

function renderizarMatrizHTML(dist, data, container) {
  let html = '<div class="table-responsive-container"><table class="data-table">';

  if (dist === "z") {
    html += '<thead><tr><th>z</th>';
    for (let j = 0; j < 10; j++) {
      html += `<th>+0.0${j}</th>`;
    }
    html += '</tr></thead><tbody>';

    for (const [row, cols] of Object.entries(data)) {
      html += `<tr><td>${row}</td>`;
      for (const val of Object.values(cols)) {
        html += `<td>${val.toFixed(4)}</td>`;
      }
      html += '</tr>';
    }
    html += '</tbody></table></div>';

  } else if (dist === "t" || dist === "chi") {
    const firstRow = Object.values(data)[0] || {};
    html += `<thead><tr><th>gl (r)</th>`;
    for (const colName of Object.keys(firstRow)) {
      html += `<th>${colName}</th>`;
    }
    html += '</tr></thead><tbody>';

    for (const [r, cols] of Object.entries(data)) {
      html += `<tr><td>${r}</td>`;
      for (const val of Object.values(cols)) {
        html += `<td>${typeof val === 'number' ? val.toFixed(3) : val}</td>`;
      }
      html += '</tr>';
    }
    html += '</tbody></table></div>';

  } else if (dist === "fisher") {
    html += `
      <div style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap;">
        <span style="color: var(--primary); font-weight: 600;">Seleccionar Nivel (1 - α):</span>
        <button class="btn-filter-shortcut btn-f-nivel active" data-lvl="0.950">0.950 (95%)</button>
        <button class="btn-filter-shortcut btn-f-nivel" data-lvl="0.975">0.975 (97.5%)</button>
        <button class="btn-filter-shortcut btn-f-nivel" data-lvl="0.990">0.990 (99%)</button>
        <button class="btn-filter-shortcut btn-f-nivel" data-lvl="0.995">0.995 (99.5%)</button>
      </div>
      <div id="fisher-table-body"></div>
    `;
    container.innerHTML = html;

    const renderFisherNivel = (lvl) => {
      const targetDiv = document.getElementById("fisher-table-body");
      const nivel = data[lvl] || {};
      const firstR2 = Object.values(nivel)[0] || {};
      let tHtml = '<div class="table-responsive-container"><table class="data-table">';
      tHtml += `<thead><tr><th>r₂ \\ r₁</th>`;
      for (const r1 of Object.keys(firstR2)) {
        tHtml += `<th>${r1}</th>`;
      }
      tHtml += '</tr></thead><tbody>';
      for (const [r2, r1_dict] of Object.entries(nivel)) {
        tHtml += `<tr><td>${r2}</td>`;
        for (const val of Object.values(r1_dict)) {
          tHtml += `<td>${typeof val === 'number' ? val.toFixed(2) : val}</td>`;
        }
        tHtml += '</tr>';
      }
      tHtml += '</tbody></table></div>';
      targetDiv.innerHTML = tHtml;
    };

    renderFisherNivel("0.950");

    document.querySelectorAll(".btn-f-nivel").forEach(b => {
      b.addEventListener("click", () => {
        document.querySelectorAll(".btn-f-nivel").forEach(btn => btn.classList.remove("active"));
        b.classList.add("active");
        renderFisherNivel(b.getAttribute("data-lvl"));
      });
    });
    return;
  }

  container.innerHTML = html;
}

// ==========================================================================
// UTILIDADES DE FORMATO
// ==========================================================================
function limpiarFormula(eq) {
  if (!eq) return "";
  return eq
    .replace(/\\le/g, "≤")
    .replace(/\\ge/g, "≥")
    .replace(/\\chi\^2/g, "χ²")
    .replace(/\\chi/g, "χ")
    .replace(/\\alpha/g, "α")
    .replace(/\\sim/g, "~")
    .replace(/\\quad/g, " &nbsp; ")
    .replace(/_\{([^}]+)\}/g, "<sub>$1</sub>")
    .replace(/_([0-9a-zA-Z])/g, "<sub>$1</sub>")
    .replace(/\^\{([^}]+)\}/g, "<sup>$1</sup>")
    .replace(/\^([0-9a-zA-Z])/g, "<sup>$1</sup>")
    .replace(/\{|\}|\\/g, "");
}

function formatearResolucionTexto(texto) {
  if (!texto) return "";
  let t = texto
    .replace(/\\le/g, "≤")
    .replace(/\\ge/g, "≥")
    .replace(/\\chi\^2/g, "χ²")
    .replace(/\\chi/g, "χ")
    .replace(/\\alpha/g, "α")
    .replace(/\\Phi/g, "Φ")
    .replace(/\\sim/g, "~")
    .replace(/\\mathcal\{N\}/g, "N")
    .replace(/\\mathcal\{F\}/g, "F")
    .replace(/_\{([^}]+)\}/g, "<sub>$1</sub>")
    .replace(/_([0-9a-zA-Z])/g, "<sub>$1</sub>")
    .replace(/\^\{([^}]+)\}/g, "<sup>$1</sup>")
    .replace(/\^([0-9a-zA-Z])/g, "<sup>$1</sup>")
    .replace(/\{|\}|\\/g, "");

  // Markdown bold
  t = t.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  t = t.replace(/\$\$(.*?)\$\$/g, '<div style="margin: 0.4rem 0; font-weight: 700; color: #38bdf8;">$1</div>');
  t = t.replace(/\$(.*?)\$/g, '<em style="color: #cbd5e1;">$1</em>');
  t = t.replace(/\n\n/g, "<br/><br/>").replace(/\n/g, "<br/>");
  return t;
}
