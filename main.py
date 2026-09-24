#!/usr/bin/env python3
"""
Orquestador Principal - Sistema de Probabilidad y Estadística
Permite:
- Iniciar la Interfaz Web Interactiva en el navegador (.venv/bin/python main.py --web)
- Ejecutar el Resolvedor Interactivo en consola (.venv/bin/python main.py --resolver)
- Generar el catálogo completo de 176 ejercicios en PDF (.venv/bin/python main.py --guia-completa)
"""
import sys
import os
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def lanzar_web():
    from app import app
    port = int(os.environ.get("PORT", 5000))
    print("=" * 70)
    print(" 🚀 INICIANDO INTERFAZ WEB INTERACTIVA")
    print(f" Abre en cualquier navegador: http://127.0.0.1:{port}")
    print(" Presiona Ctrl+C para detener el servidor.")
    print("=" * 70)
    app.run(host="127.0.0.1", port=port, debug=False)

def lanzar_resolver():
    from resolver import modo_interactivo
    modo_interactivo()

def compilar_guia_176():
    from src.generador_ejercicios import GeneradorEjercicios
    from src.compilar_documento import compilar_guia_pdf, generar_nombre_salida
    
    print("=" * 70)
    print(" COMPILANDO GUÍA COMPLETA DE 176 EJERCICIOS (4 TANDAS × 11 CRITERIOS)")
    print(" (Muestreo Aleatorio Único sobre Tablas Oficiales)")
    print("=" * 70)
    gen = GeneradorEjercicios()
    print("Generando catálogo analítico aleatorizado...")
    ejercicios = gen.generar_lote_personalizado(
        ["z", "t", "chi", "fisher"],
        list(range(1, 12)),
        repeticiones_por_tipo=4
    )
                
    pdf_out = generar_nombre_salida(es_completo=True, cantidad=176)
    print(f"Compilando documento unificado en '{pdf_out}'...")
    compilar_guia_pdf(
        ejercicios,
        nombre_archivo=pdf_out,
        titulo="GUÍA COMPLETA DE EJERCICIOS RESUELTOS DE PROBABILIDAD Y ESTADÍSTICA",
        subtitulo="Resolución Analítica Integral y Documentación Gráfica de 176 Problemas"
    )
    print(f"¡Guía compilada exitosamente! Archivo: {pdf_out}")

def main():
    parser = argparse.ArgumentParser(description="Plataforma de Probabilidad y Estadística.")
    parser.add_argument("--web", action="store_true", help="Lanza el servidor web interactivo.")
    parser.add_argument("--resolver", action="store_true", help="Lanza el resolvedor de ejercicios por consola.")
    parser.add_argument("--guia-completa", action="store_true", help="Compila la guía completa de 176 ejercicios en PDF.")

    args = parser.parse_args()

    if args.web:
        lanzar_web()
    elif args.resolver:
        lanzar_resolver()
    elif args.guia_completa:
        compilar_guia_176()
    else:
        # Menú interactivo rápido si se llama sin banderas
        print("=" * 70)
        print("   SISTEMA DE PROBABILIDAD Y ESTADÍSTICA • TABLAS OFICIALES")
        print("=" * 70)
        print("Elige cómo deseas utilizar el sistema:")
        print("  [1] Iniciar Interfaz Web Interactiva (Recomendado - Acceso desde navegador)")
        print("  [2] Resolver un ejercicio específico por terminal (Consola)")
        print("  [3] Compilar la guía completa de 176 ejercicios en PDF")
        print("  [0] Salir")
        
        op = input("\nSelecciona una opción (0-3) [por defecto 1]: ").strip()
        if op == "2":
            lanzar_resolver()
        elif op == "3":
            compilar_guia_176()
        elif op == "0":
            print("Hasta luego.")
        else:
            lanzar_web()

if __name__ == "__main__":
    main()
