#!/usr/bin/env python3
"""
Servidor Web Local (Flask) - Sistema Estadístico Interactivo.
Proporciona la interfaz web accesible desde cualquier navegador:
- Generador de lotes de ejercicios personalizados (filtra por distribución, criterio y cantidad).
- Resolvedor de ejercicios propios con soporte para generar solo la gráfica, solo la solución o todo junto.
- Explorador interactivo de las tablas oficiales (Z, t-Student, Chi-cuadrado, Fisher).
- Compilación y descarga dinámica de guías en PDF.

Uso:
  .venv/bin/python app.py
"""
import os
import sys
import tempfile
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify, send_file

# Asegurar importación de src
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.generador_ejercicios import GeneradorEjercicios
from src.generador_graficos import renderizar_grafico_base64, renderizar_grafico
from src.resolver_personalizado import ResolverPersonalizado
from src.compilar_documento import compilar_guia_pdf, generar_nombre_salida, RESULTADOS_DIR
from src.tablas_manager import TablasManager

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"), static_folder=os.path.join(BASE_DIR, "static"))

gen_engine = GeneradorEjercicios()
resolver_engine = ResolverPersonalizado()
tablas_manager = TablasManager()

def abrir_navegador_predeterminado(url):
    """Abre el navegador por defecto configurado en el sistema operativo (Windows, Linux, Mac)."""
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Aviso: No se pudo abrir el navegador automáticamente ({e}). Accede manualmente a {url}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generar", methods=["POST"])
def api_generar():
    try:
        data = request.get_json() or {}
        dist = data.get("dist", "z")
        criterios = data.get("criterios", list(range(1, 12)))
        # Se interpreta como cantidad de ejercicios por cada tipo/criterio (tandas)
        cantidad_por_tipo = int(data.get("cantidad_por_tipo", data.get("cantidad", 1)))
        params = data.get("params", {})

        dist_list = [dist] if dist != "all" else ["z", "t", "chi", "fisher"]
        ejercicios = gen_engine.generar_lote_personalizado(dist_list, criterios, repeticiones_por_tipo=cantidad_por_tipo, params=params)

        # Generar imagen base64 para cada ejercicio en memoria
        for ej in ejercicios:
            ej["grafico_base64"] = renderizar_grafico_base64(ej)

        return jsonify({"ejercicios": ejercicios, "total": len(ejercicios)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/resolver", methods=["POST"])
def api_resolver():
    try:
        data = request.get_json() or {}
        dist = data.get("dist", "z")
        op = data.get("op", "<=")
        val = data.get("val", 1.45)
        modo = data.get("modo", "full")
        
        params = {
            "df": data.get("df", 10),
            "r1": data.get("r1", 5),
            "r2": data.get("r2", 10)
        }

        ej = resolver_engine.formatear_y_renderizar(dist, op, val, params=params)
        ej["modo"] = modo
        return jsonify(ej)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tablas/<dist>", methods=["GET"])
def api_tabla(dist):
    try:
        dist = dist.lower()
        if dist in ["z", "normal"]:
            return jsonify(tablas_manager.tabla_z)
        elif dist in ["t", "tstudent"]:
            return jsonify(tablas_manager.tabla_t)
        elif dist in ["chi", "chi2"]:
            return jsonify(tablas_manager.tabla_chi)
        elif dist in ["f", "fisher"]:
            return jsonify(tablas_manager.tabla_fisher)
        else:
            return jsonify({"error": "Tabla no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/exportar-pdf", methods=["POST"])
def api_exportar_pdf():
    try:
        data = request.get_json() or {}
        ejercicios = data.get("ejercicios", [])
        if not ejercicios:
            return jsonify({"error": "No hay ejercicios para compilar"}), 400

        # Detectar distribución predominante para la etiqueta del archivo
        dist_tags = set(ej.get("dist_type", "VARIADO") for ej in ejercicios)
        dist_label = list(dist_tags)[0] if len(dist_tags) == 1 else "VARIADO"
        es_completo = len(ejercicios) >= 176

        # Ruta organizada y enumerada dentro de Resultados/
        ruta_pdf = generar_nombre_salida(es_completo, dist=dist_label, cantidad=len(ejercicios))

        compilar_guia_pdf(
            ejercicios,
            nombre_archivo=ruta_pdf,
            titulo="GUÍA DE EJERCICIOS PERSONALIZADA",
            subtitulo=f"Lote de {len(ejercicios)} Ejercicios Resueltos y Graficados",
            dist_tag=dist_label
        )

        nombre_descarga = os.path.basename(ruta_pdf)
        return send_file(
            ruta_pdf,
            as_attachment=True,
            download_name=nombre_descarga,
            mimetype="application/pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generar-guia-completa", methods=["POST"])
def api_generar_guia_completa():
    """Genera y descarga la guía oficial completa de 176 ejercicios (4 tandas x 11 criterios) con muestreo aleatorio."""
    try:
        gen_engine.reiniciar_rastreo()
        ejercicios = gen_engine.generar_lote_personalizado(
            ["z", "t", "chi", "fisher"],
            list(range(1, 12)),
            repeticiones_por_tipo=4
        )

        ruta_pdf = generar_nombre_salida(es_completo=True, cantidad=176)
        compilar_guia_pdf(
            ejercicios,
            nombre_archivo=ruta_pdf,
            titulo="GUÍA COMPLETA DE EJERCICIOS RESUELTOS DE PROBABILIDAD Y ESTADÍSTICA",
            subtitulo="Resolución Analítica Integral y Documentación Gráfica de 176 Problemas"
        )

        nombre_descarga = os.path.basename(ruta_pdf)
        return send_file(
            ruta_pdf,
            as_attachment=True,
            download_name=nombre_descarga,
            mimetype="application/pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    url = f"http://127.0.0.1:{port}"
    print("=" * 70)
    print(f" Servidor Estadístico Iniciado con Éxito")
    print(f" Acceso: {url}")
    print(" Abriendo automáticamente en tu navegador predeterminado...")
    print("=" * 70)
    
    # Abrir el navegador por defecto del sistema automáticamente tras un retardo de 1 segundo
    Timer(1.2, abrir_navegador_predeterminado, args=[url]).start()
    app.run(host="127.0.0.1", port=port, debug=False)
