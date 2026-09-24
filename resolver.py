#!/usr/bin/env python3
"""
RESOLVEDOR DE EJERCICIOS PERSONALIZADOS DE PROBABILIDAD Y ESTADÍSTICA
Permite resolver ejercicios propios seleccionando la distribución y parámetros iniciales.
Reconoce automáticamente el patrón analítico entre los 11 criterios oficiales, cita la tabla
oficial correspondiente y genera la orden, resolución analítica y gráfico sombreado.

Uso Interactivo:
  python resolver.py

Uso por Línea de Comandos (CLI):
  python resolver.py --dist Z --op "<=" --val 1.45
  python resolver.py --dist t --df 12 --op "<=" --val -1.782
  python resolver.py --dist chi --df 10 --op "intervalo" --val 3.940 18.307
  python resolver.py --dist fisher --r1 5 --r2 10 --op "<=" --val 3.33
  python resolver.py --dist Z --op "inv_le" --val 0.9505
"""
import sys
import os
import argparse

# Asegurar importación de src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.resolver_personalizado import ResolverPersonalizado

def limpiar_consola(texto):
    """Limpia etiquetas LaTeX para visualización limpia en consola."""
    t = texto.replace(r"\le", "≤").replace(r"\ge", "≥")
    t = t.replace(r"\chi^2", "χ²").replace(r"\chi", "χ")
    t = t.replace(r"\alpha", "α").replace(r"\Phi", "Φ")
    t = t.replace(r"\sim", "~")
    t = t.replace(r"\mathcal{N}", "N").replace(r"\mathcal{F}", "F")
    t = t.replace(r"\quad", "   ")
    t = t.replace("**", "").replace("$$", "").replace("$", "")
    t = t.replace(r"\le", "≤").replace(r"\ge", "≥")
    t = t.replace("{", "").replace("}", "").replace("\\", "")
    return t

def modo_interactivo():
    rp = ResolverPersonalizado()
    print("=" * 70)
    print("   RESOLVEDOR INTERACTIVO DE EJERCICIOS DE ESTADÍSTICA")
    print("   Basado en Tablas Oficiales (Z, t-Student, Chi-cuadrado, Fisher)")
    print("=" * 70)

    print("\n1. Selecciona la Distribución:")
    print("   [1] Normal Estándar  Z ~ N(0, 1)")
    print("   [2] t-Student        T ~ t(r)")
    print("   [3] Chi-cuadrado     X ~ χ²(r)")
    print("   [4] Fisher-Snedecor  F ~ F(r1, r2)")
    
    op_dist = input("\nElige una opción (1-4): ").strip()
    dist_map = {"1": "Z", "2": "t", "3": "chi", "4": "fisher"}
    dist = dist_map.get(op_dist, "Z")
    
    params = {}
    if dist in ["t", "chi"]:
        df_input = input("Ingresa los grados de libertad (r) [ej. 10]: ").strip()
        params["df"] = int(df_input) if df_input.isdigit() else 10
    elif dist == "fisher":
        r1_input = input("Ingresa grados de libertad del numerador (r1) [ej. 5]: ").strip()
        r2_input = input("Ingresa grados de libertad del denominador (r2) [ej. 10]: ").strip()
        params["r1"] = int(r1_input) if r1_input.isdigit() else 5
        params["r2"] = int(r2_input) if r2_input.isdigit() else 10

    print("\n2. Selecciona el Tipo de Problema:")
    print("   [1] Probabilidad de cola izquierda: P(X ≤ a)")
    print("   [2] Probabilidad de cola derecha:   P(X ≥ a)")
    print("   [3] Probabilidad en un intervalo:   P(a ≤ X ≤ b)")
    print("   [4] Búsqueda inversa cola izquierda: Dado P(X ≤ c) = p, hallar constante c")
    print("   [5] Búsqueda inversa cola derecha:   Dado P(X ≥ c) = p, hallar constante c")

    op_tipo = input("\nElige una opción (1-5): ").strip()
    
    if op_tipo == "1":
        val_str = input("Ingresa el valor de 'a' [ej. 1.45 o -0.84]: ").strip()
        valores = float(val_str)
        operacion = "<="
    elif op_tipo == "2":
        val_str = input("Ingresa el valor de 'a' [ej. 1.96 o -1.20]: ").strip()
        valores = float(val_str)
        operacion = ">="
    elif op_tipo == "3":
        v1_str = input("Ingresa el límite inferior 'a' [ej. -1.20 o 0.50]: ").strip()
        v2_str = input("Ingresa el límite superior 'b' [ej. 1.80 o 2.10]: ").strip()
        valores = (float(v1_str), float(v2_str))
        operacion = "intervalo"
    elif op_tipo == "4":
        p_str = input("Ingresa la probabilidad 'p' [ej. 0.9500 o 0.0500]: ").strip()
        valores = float(p_str)
        operacion = "inv_le"
    elif op_tipo == "5":
        p_str = input("Ingresa la probabilidad 'p' [ej. 0.0500 o 0.9750]: ").strip()
        valores = float(p_str)
        operacion = "inv_ge"
    else:
        print("Opción inválida. Se resolverá P(Z ≤ 1.25) por defecto.")
        valores = 1.25
        operacion = "<="

    print("\nProcesando y reconociendo patrón analítico...")
    res = rp.formatear_y_renderizar(dist, operacion, valores, params, nombre_salida="ejercicio_personalizado")

    print("\n" + "=" * 70)
    print(f" RESULTADO: {res['distribucion'].upper()} | CRITERIO {res['criterio_id']}: {res['criterio_nombre']}")
    print("=" * 70)
    
    print("\n--- 1. ORDEN DEL EJERCICIO ---")
    print(limpiar_consola(res["orden"]))
    
    print("\n--- 2. RESOLUCIÓN ANALÍTICA PASO A PASO ---")
    print(limpiar_consola(res["resolucion"]))
    
    print("\n--- 3. GRÁFICA DE LA DISTRIBUCIÓN ---")
    print(f"Archivo de imagen generado: {res['grafico_path']}")
    print("=" * 70)

def modo_cli(args):
    rp = ResolverPersonalizado()
    params = {}
    if args.df:
        params["df"] = args.df
    if args.r1:
        params["r1"] = args.r1
    if args.r2:
        params["r2"] = args.r2

    valores = args.val if len(args.val) > 1 else args.val[0]
    res = rp.formatear_y_renderizar(args.dist, args.op, valores, params, nombre_salida="ejercicio_personalizado")

    print("=" * 70)
    print(f" {res['distribucion'].upper()} | CRITERIO {res['criterio_id']}: {res['criterio_nombre']}")
    print("=" * 70)
    print("\n1. ORDEN DEL EJERCICIO:")
    print(" ", limpiar_consola(res["orden"]))
    print("\n2. RESOLUCIÓN ANALÍTICA:")
    print(limpiar_consola(res["resolucion"]))
    print("\n3. GRÁFICA:")
    print(f"  Guardada en: {res['grafico_path']}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolvedor de ejercicios de probabilidad con tablas oficiales.")
    parser.add_argument("--dist", type=str, help="Distribución: 'Z', 't', 'chi', 'fisher'")
    parser.add_argument("--op", type=str, help="Operación: '<=', '>=', 'intervalo', 'inv_le', 'inv_ge'")
    parser.add_argument("--val", type=float, nargs="+", help="Valor numérico o par de valores para intervalo")
    parser.add_argument("--df", type=int, help="Grados de libertad para t o chi-cuadrado")
    parser.add_argument("--r1", type=int, help="Grados de libertad r1 (numerador) para Fisher")
    parser.add_argument("--r2", type=int, help="Grados de libertad r2 (denominador) para Fisher")

    parsed_args = parser.parse_args()

    if parsed_args.dist and parsed_args.op and parsed_args.val:
        modo_cli(parsed_args)
    else:
        modo_interactivo()
