"""
Módulo de generación de gráficos de alta calidad estética con Matplotlib.
Renderiza las curvas de densidad teóricas, sombrea exactamente la región de probabilidad
evaluada y resalta los puntos críticos con líneas discontinuas, puntos y anotaciones.
Soporta exportación a disco (PNG) y generación en memoria (Base64) para consumo web directo.
"""
import os
import io
import base64
import matplotlib
matplotlib.use("Agg")  # Backend no interactivo para máxima velocidad y estabilidad
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_GRAFICOS_DIR = os.path.join(BASE_DIR, "graficos")

def _crear_figura(ejercicio):
    dist_type = ejercicio["dist_type"]
    params = ejercicio.get("params", {})
    region_type = ejercicio["region_type"]
    points = ejercicio["points"]
    prob = ejercicio.get("probabilidad", 0.0)
    crit_nom = ejercicio.get("criterio_nombre", "")
    ej_id = ejercicio.get("id", 1)

    fig, ax = plt.subplots(figsize=(6.2, 3.2), dpi=150)
    
    # ------------------ DEFINICIÓN DE CURVAS Y DOMINIOS ------------------
    if dist_type == "Z":
        x_min, x_max = -4.0, 4.0
        x = np.linspace(x_min, x_max, 1000)
        y = stats.norm.pdf(x)
        dist_label = "Z ~ N(0, 1)"
        pdf_func = stats.norm.pdf
        var_sym = "z"

    elif dist_type == "t":
        df = params.get("df", 10)
        x_min, x_max = -4.2, 4.2
        x = np.linspace(x_min, x_max, 1000)
        y = stats.t.pdf(x, df)
        dist_label = f"T ~ t(r={df})"
        pdf_func = lambda val: stats.t.pdf(val, df)
        var_sym = "t"

    elif dist_type == "chi":
        df = params.get("df", 10)
        max_pt = max(points) if points else 25
        x_max = max(df * 2.5, max_pt * 1.25, 20.0)
        x = np.linspace(0.001, x_max, 1000)
        y = stats.chi2.pdf(x, df)
        dist_label = f"X ~ χ²(r={df})"
        pdf_func = lambda val: stats.chi2.pdf(val, df)
        var_sym = "χ²"

    elif dist_type == "fisher":
        r1 = params.get("r1", 5)
        r2 = params.get("r2", 10)
        max_pt = max(points) if points else 5
        x_max = max(5.0, max_pt * 1.35)
        x = np.linspace(0.001, x_max, 1000)
        y = stats.f.pdf(x, r1, r2)
        dist_label = f"F ~ F(r₁={r1}, r₂={r2})"
        pdf_func = lambda val: stats.f.pdf(val, r1, r2)
        var_sym = "F"

    # Colorimetría moderna y armónica
    curve_color = "#1d3557"     # Azul marino profundo
    fill_color = "#457b9d"      # Azul medio elegante
    highlight_color = "#e63946" # Rojo coral para puntos críticos

    # Trazado de la curva teórica
    ax.plot(x, y, color=curve_color, lw=2.2, label=dist_label)

    # ------------------ SOMBREADO DE LA REGIÓN ------------------
    mask = np.zeros_like(x, dtype=bool)
    if region_type == "left":
        cutoff = points[0]
        mask = (x <= cutoff)
    elif region_type == "right":
        cutoff = points[0]
        mask = (x >= cutoff)
    elif region_type == "interval":
        p1, p2 = sorted(points)
        mask = (x >= p1) & (x <= p2)

    ax.fill_between(x, 0, y, where=mask, color=fill_color, alpha=0.35,
                    label=f"Área = {prob:.4f}")

    # ------------------ MARCADO DE PUNTOS CRÍTICOS ------------------
    for pt in points:
        y_pt = float(pdf_func(pt))
        ax.vlines(pt, 0, y_pt, colors=highlight_color, linestyles="--", lw=1.6, alpha=0.85)
        ax.scatter([pt], [y_pt], color=highlight_color, s=42, zorder=6, edgecolors="white", lw=1.2)
        ax.annotate(f"{pt:.2f}", (pt, 0), textcoords="offset points", xytext=(0, -15),
                    ha="center", fontsize=8.5, fontweight="bold", color=highlight_color)

    # Configuración de estética y títulos
    titulo_txt = f"{dist_label}" + (f" | Caso: {crit_nom}" if crit_nom else "")
    if ej_id and str(ej_id) != "personalizado":
        titulo_txt = f"Ejercicio {ej_id}: " + titulo_txt

    ax.set_title(titulo_txt, fontsize=10.5, fontweight="bold", color="#1d3557", pad=10)
    ax.set_xlabel(f"Variable {var_sym}", fontsize=9.5)
    ax.set_ylabel("Densidad f(x)", fontsize=9.5)
    
    ax.set_ylim(bottom=0, top=max(y) * 1.15)
    if dist_type in ["chi", "fisher"]:
        ax.set_xlim(left=0, right=x_max)
    else:
        ax.set_xlim(left=x_min, right=x_max)

    ax.grid(True, linestyle=":", alpha=0.45, color="#8d99ae")
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.92, facecolor="#f8f9fa", edgecolor="#ced4da")
    
    for spine in ax.spines.values():
        spine.set_color("#6c757d")
        spine.set_linewidth(0.8)

    plt.tight_layout()
    return fig

def renderizar_grafico(ejercicio, output_dir=DEFAULT_GRAFICOS_DIR):
    """Guarda el gráfico en un archivo PNG en el directorio especificado."""
    os.makedirs(output_dir, exist_ok=True)
    ej_id = ejercicio.get("id", "personalizado")
    fig = _crear_figura(ejercicio)
    
    img_filename = f"ejercicio_{ej_id:03d}.png" if isinstance(ej_id, int) else f"{ej_id}.png"
    img_path = os.path.join(output_dir, img_filename)
    fig.savefig(img_path, dpi=150)
    plt.close(fig)
    return img_path

def renderizar_grafico_base64(ejercicio):
    """Renderiza el gráfico directamente en memoria y retorna string base64 para HTML/Web."""
    fig = _crear_figura(ejercicio)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    b64_data = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{b64_data}"

def generar_todos_los_graficos(ejercicios, output_dir=DEFAULT_GRAFICOS_DIR):
    os.makedirs(output_dir, exist_ok=True)
    rutas = []
    for i, ej in enumerate(ejercicios):
        ruta = renderizar_grafico(ej, output_dir)
        rutas.append(ruta)
    return rutas
