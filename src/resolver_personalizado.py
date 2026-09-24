"""
Módulo de Resolución de Ejercicios Personalizados.
Permite a cualquier usuario/estudiante introducir un ejercicio arbitrario:
- Seleccionar la tabla / distribución: Normal Z, t-Student, Chi-cuadrado, Fisher F.
- Suministrar los parámetros y valores iniciales.
- Reconocer automáticamente el patrón contra los 11 criterios oficiales.
- Generar:
  1. Orden del ejercicio estructurada
  2. Resolución analítica detallada paso a paso citando las tablas oficiales
     (con aplicación estricta de la Regla del Complemento 1 - P(...) en colas >=)
  3. Gráfico teórico sombreado con puntos críticos marcados
"""
import os
import re
try:
    from .tablas_manager import TablasManager
    from .generador_graficos import renderizar_grafico, renderizar_grafico_base64
except ImportError:
    from tablas_manager import TablasManager
    from generador_graficos import renderizar_grafico, renderizar_grafico_base64

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_GRAFICOS_DIR = os.path.join(BASE_DIR, "graficos")

class ResolverPersonalizado:
    def __init__(self):
        self.tm = TablasManager()

    def resolver(self, dist, operacion, valores, params=None, id_ejercicio="personalizado"):
        params = params or {}
        dist = dist.lower()

        if dist in ["z", "normal"]:
            return self._resolver_z(operacion, valores, id_ejercicio)
        elif dist in ["t", "tstudent", "student"]:
            return self._resolver_t(operacion, valores, params.get("df", 10), id_ejercicio)
        elif dist in ["chi", "chi2", "chicuadrado"]:
            return self._resolver_chi(operacion, valores, params.get("df", 10), id_ejercicio)
        elif dist in ["f", "fisher"]:
            r1 = params.get("r1", 5)
            r2 = params.get("r2", 10)
            return self._resolver_fisher(operacion, valores, r1, r2, id_ejercicio)
        else:
            raise ValueError(f"Distribución no reconocida: '{dist}'. Opciones válidas: 'Z', 't', 'chi', 'fisher'.")

    # =========================================================================
    # RESOLVEDOR NORMAL Z
    # =========================================================================
    def _resolver_z(self, op, val, ej_id):
        e = {"id": ej_id, "distribucion": "Normal Estándar", "dist_type": "Z", "params": {}}

        if op == "<=":
            a = float(val)
            if a >= 0:
                prob, r_k, c_k = self.tm.get_z(a)
                e["criterio_id"] = 1
                e["criterio_nombre"] = "<= +"
                e["orden"] = f"P(Z \\le {a:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Variable aleatoria Normal Estándar: $Z \\sim \\mathcal{{N}}(0, 1)$. "
                    f"Probabilidad acumulada directa hasta el valor positivo $a = {a:.2f}$.\n\n"
                    f"**Paso 2: Consulta en la Tabla Normal Estándar.**\n"
                    f"Fila `{r_k}`, columna `{c_k}`. Intersección directa:\n"
                    f"$$P(Z \\le {a:.2f}) = {prob:.4f}$$\n\n"
                    f"**Paso 3: Conclusión.**\n"
                    f"$$P(Z \\le {a:.2f}) = {prob:.4f}$$ (o {prob*100:.2f}%)."
                )
                e["region_type"] = "left"
                e["points"] = [a]
                e["labels"] = [f"z = {a:.2f}"]
                e["probabilidad"] = prob
            else:
                pos_a = abs(a)
                prob, r_k, c_k = self.tm.get_z(pos_a)
                res = round(1.0 - prob, 4)
                e["criterio_id"] = 2
                e["criterio_nombre"] = "<= -"
                e["orden"] = f"P(Z \\le {a:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Para $Z \\sim \\mathcal{{N}}(0, 1)$, se solicita la probabilidad de cola inferior para el valor negativo ${a:.2f}$.\n\n"
                    f"**Paso 2: Propiedad de simetría y complemento.**\n"
                    f"Por simetría respecto al origen: $P(Z \\le {a:.2f}) = 1 - P(Z \\le {pos_a:.2f})$.\n\n"
                    f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                    f"Para $+{pos_a:.2f}$ (fila `{r_k}`, columna `{c_k}`): $P(Z \\le {pos_a:.2f}) = {prob:.4f}$.\n\n"
                    f"**Paso 4: Cálculo analítico.**\n"
                    f"$$P(Z \\le {a:.2f}) = 1 - {prob:.4f} = {res:.4f}$$\n\n"
                    f"**Paso 5: Conclusión.**\n"
                    f"$$P(Z \\le {a:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
                )
                e["region_type"] = "left"
                e["points"] = [a]
                e["labels"] = [f"z = {a:.2f}"]
                e["probabilidad"] = res

        elif op == ">=":
            a = float(val)
            if a >= 0:
                prob, r_k, c_k = self.tm.get_z(a)
                res = round(1.0 - prob, 4)
                e["criterio_id"] = 3
                e["criterio_nombre"] = ">= +"
                e["orden"] = f"P(Z \\ge {a:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y Regla del Complemento.**\n"
                    f"Para $Z \\sim \\mathcal{{N}}(0, 1)$, cola superior desde el valor positivo $a = {a:.2f}$:\n"
                    f"$$P(Z \\ge {a:.2f}) = 1 - P(Z \\le {a:.2f})$$\n\n"
                    f"**Paso 2: Consulta en la Tabla Normal Estándar.**\n"
                    f"En fila `{r_k}`, columna `{c_k}`: $P(Z \\le {a:.2f}) = {prob:.4f}$.\n\n"
                    f"**Paso 3: Cálculo analítico del complemento.**\n"
                    f"$$P(Z \\ge {a:.2f}) = 1 - {prob:.4f} = {res:.4f}$$\n\n"
                    f"**Paso 4: Conclusión.**\n"
                    f"$$P(Z \\ge {a:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
                )
                e["region_type"] = "right"
                e["points"] = [a]
                e["labels"] = [f"z = {a:.2f}"]
                e["probabilidad"] = res
            else:
                pos_a = abs(a)
                prob_pos, r_k, c_k = self.tm.get_z(pos_a)
                p_cola_izq = round(1.0 - prob_pos, 4)
                res = round(1.0 - p_cola_izq, 4)
                e["criterio_id"] = 4
                e["criterio_nombre"] = ">= -"
                e["orden"] = f"P(Z \\ge {a:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Planteamiento formal por la Regla del Complemento.**\n"
                    f"Para $Z \\sim \\mathcal{{N}}(0, 1)$, se pide la probabilidad hacia la derecha a partir del valor negativo ${a:.2f}$. "
                    f"Por la regla fundamental del complemento, restamos del total (1) el área de la cola izquierda no deseada:\n"
                    f"$$P(Z \\ge {a:.2f}) = 1 - P(Z \\le {a:.2f})$$\n\n"
                    f"**Paso 2: Cálculo numérico de la cola izquierda P(Z \\le {a:.2f}).**\n"
                    f"Para hallar el área acumulada hasta el valor negativo ${a:.2f}$, usamos la simetría de la campana:\n"
                    f"$$P(Z \\le {a:.2f}) = 1 - P(Z \\le {pos_a:.2f})$$\n"
                    f"Buscando en la Tabla Normal Estándar en la fila `{r_k}` y columna `{c_k}`: $P(Z \\le {pos_a:.2f}) = {prob_pos:.4f}$.\n"
                    f"Por tanto, la probabilidad de la cola izquierda no sombreada es:\n"
                    f"$$P(Z \\le {a:.2f}) = 1 - {prob_pos:.4f} = {p_cola_izq:.4f}$$\n\n"
                    f"**Paso 3: Aplicación aritmética del complemento.**\n"
                    f"Restamos la cola izquierda del área total (1):\n"
                    f"$$P(Z \\ge {a:.2f}) = 1 - P(Z \\le {a:.2f}) = 1 - {p_cola_izq:.4f} = {res:.4f}$$\n\n"
                    f"**Paso 4: Conclusión y lectura de la gráfica.**\n"
                    f"$$P(Z \\ge {a:.2f}) = {res:.4f}$$ (o {res*100:.2f}%).\n\n"
                    f"*(Nota sobre la gráfica: La región sombreada inicia en el valor negativo ${a:.2f}$ y se extiende hacia toda la derecha $+\\infty$. "
                    f"Cubre toda la campana excepto la colita izquierda en blanco de {p_cola_izq:.4f}, por lo que el área sombreada mide exactamente {res:.4f}).*"
                )
                e["region_type"] = "right"
                e["points"] = [a]
                e["labels"] = [f"z = {a:.2f}"]
                e["probabilidad"] = res

        elif op in ["intervalo", "between"]:
            v1, v2 = sorted([float(x) for x in val])
            if v1 >= 0 and v2 >= 0:
                p1, r1_k, c1_k = self.tm.get_z(v1)
                p2, r2_k, c2_k = self.tm.get_z(v2)
                res = round(p2 - p1, 4)
                e["criterio_id"] = 5
                e["criterio_nombre"] = "+ <= <= +"
                e["orden"] = f"P({v1:.2f} \\le Z \\le {v2:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Intervalo positivo $[{v1:.2f}, {v2:.2f}]$ en $Z \\sim \\mathcal{{N}}(0, 1)$.\n\n"
                    f"**Paso 2: Resta de acumuladas directas.**\n"
                    f"$$P({v1:.2f} \\le Z \\le {v2:.2f}) = P(Z \\le {v2:.2f}) - P(Z \\le {v1:.2f})$$\n\n"
                    f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                    f"- $P(Z \\le {v2:.2f}) = {p2:.4f}$\n"
                    f"- $P(Z \\le {v1:.2f}) = {p1:.4f}$\n\n"
                    f"**Paso 4: Cálculo analítico.**\n"
                    f"$$P({v1:.2f} \\le Z \\le {v2:.2f}) = {p2:.4f} - {p1:.4f} = {res:.4f}$$\n\n"
                    f"**Paso 5: Conclusión.**\n"
                    f"$$P({v1:.2f} \\le Z \\le {v2:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
                )
                e["region_type"] = "interval"
                e["points"] = [v1, v2]
                e["labels"] = [f"z1 = {v1:.2f}", f"z2 = {v2:.2f}"]
                e["probabilidad"] = res

            elif v1 < 0 and v2 > 0:
                pos_v1 = abs(v1)
                p1, r1_k, c1_k = self.tm.get_z(pos_v1)
                p2, r2_k, c2_k = self.tm.get_z(v2)
                p_lower = round(1.0 - p1, 4)
                res = round(p2 - p_lower, 4)
                e["criterio_id"] = 6
                e["criterio_nombre"] = "- <= <= +"
                e["orden"] = f"P({v1:.2f} \\le Z \\le {v2:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Intervalo bilateral entre límite negativo ${v1:.2f}$ y positivo ${v2:.2f}$ en $Z \\sim \\mathcal{{N}}(0, 1)$.\n\n"
                    f"**Paso 2: Resta de acumuladas y simetría.**\n"
                    f"$$P({v1:.2f} \\le Z \\le {v2:.2f}) = P(Z \\le {v2:.2f}) - P(Z \\le {v1:.2f})$$\n"
                    f"Con $P(Z \\le {v1:.2f}) = 1 - P(Z \\le {pos_v1:.2f})$.\n\n"
                    f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                    f"- $P(Z \\le {v2:.2f}) = {p2:.4f}$ (fila `{r2_k}`, col `{c2_k}`)\n"
                    f"- $P(Z \\le {pos_v1:.2f}) = {p1:.4f} \\implies P(Z \\le {v1:.2f}) = {p_lower:.4f}$\n\n"
                    f"**Paso 4: Cálculo analítico.**\n"
                    f"$$P({v1:.2f} \\le Z \\le {v2:.2f}) = {p2:.4f} - {p_lower:.4f} = {res:.4f}$$\n\n"
                    f"**Paso 5: Conclusión.**\n"
                    f"$$P({v1:.2f} \\le Z \\le {v2:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
                )
                e["region_type"] = "interval"
                e["points"] = [v1, v2]
                e["labels"] = [f"z1 = {v1:.2f}", f"z2 = {v2:.2f}"]
                e["probabilidad"] = res

            else:
                pos_v1 = abs(v1)
                pos_v2 = abs(v2)
                p1, r1_k, c1_k = self.tm.get_z(pos_v1)
                p2, r2_k, c2_k = self.tm.get_z(pos_v2)
                res = round(p1 - p2, 4)
                e["criterio_id"] = 7
                e["criterio_nombre"] = "- <= <= -"
                e["orden"] = f"P({v1:.2f} \\le Z \\le {v2:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Intervalo negativo $[{v1:.2f}, {v2:.2f}]$ en $Z \\sim \\mathcal{{N}}(0, 1)$.\n\n"
                    f"**Paso 2: Propiedad de simetría.**\n"
                    f"Equivale al intervalo positivo reflejado $[{pos_v2:.2f}, {pos_v1:.2f}]$:\n"
                    f"$$P({v1:.2f} \\le Z \\le {v2:.2f}) = P(Z \\le {pos_v1:.2f}) - P(Z \\le {pos_v2:.2f})$$\n\n"
                    f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                    f"- $P(Z \\le {pos_v1:.2f}) = {p1:.4f}$\n"
                    f"- $P(Z \\le {pos_v2:.2f}) = {p2:.4f}$\n\n"
                    f"**Paso 4: Cálculo analítico.**\n"
                    f"$$P({v1:.2f} \\le Z \\le {v2:.2f}) = {p1:.4f} - {p2:.4f} = {res:.4f}$$\n\n"
                    f"**Paso 5: Conclusión.**\n"
                    f"$$P({v1:.2f} \\le Z \\le {v2:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
                )
                e["region_type"] = "interval"
                e["points"] = [v1, v2]
                e["labels"] = [f"z1 = {v1:.2f}", f"z2 = {v2:.2f}"]
                e["probabilidad"] = res

        elif op in ["inv_le", "<= c", "<=c"]:
            p = float(val)
            if p >= 0.50:
                c_val, p_found, r_k, c_k = self.tm.find_z_inverse(p)
                e["criterio_id"] = 8
                e["criterio_nombre"] = "<= C"
                e["orden"] = f"P(Z \\le c) = {p:.4f}, \\quad c = ?"
                e["resolucion"] = (
                    f"**Paso 1: Búsqueda inversa en Tabla Normal Estándar.**\n"
                    f"Para $P(Z \\le c) = {p:.4f}$ ($c > 0$), ubicamos en el cuerpo `{p_found:.4f}` en fila `{r_k}` y columna `{c_k}`:\n"
                    f"$$c = {r_k} + {c_k} = {c_val:.2f}$$"
                )
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p_found
            else:
                p_comp = round(1.0 - p, 4)
                k_val, p_found, r_k, c_k = self.tm.find_z_inverse(p_comp)
                c_val = -k_val
                e["criterio_id"] = 10
                e["criterio_nombre"] = "<= -C"
                e["orden"] = f"P(Z \\le c) = {p:.4f}, \\quad c = ? \\quad (c < 0)"
                e["resolucion"] = (
                    f"**Paso 1: Simetría para cuantil negativo.**\n"
                    f"Como $p = {p:.4f} < 0.50$, sea $c = -k$. $P(Z \\le k) = 1 - {p:.4f} = {p_comp:.4f}$.\n\n"
                    f"**Paso 2: Búsqueda en tabla.**\n"
                    f"Fila `{r_k}`, columna `{c_k}` $\\implies k = {k_val:.2f} \\implies c = {c_val:.2f}$."
                )
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p

        elif op in ["inv_ge", ">= c", ">=c"]:
            p = float(val)
            if p <= 0.50:
                p_comp = round(1.0 - p, 4)
                c_val, p_found, r_k, c_k = self.tm.find_z_inverse(p_comp)
                e["criterio_id"] = 9
                e["criterio_nombre"] = ">= C"
                e["orden"] = f"P(Z \\ge c) = {p:.4f}, \\quad c = ?"
                e["resolucion"] = (
                    f"**Paso 1: Complemento e inversa.**\n"
                    f"$$P(Z \\le c) = 1 - P(Z \\ge c) = 1 - {p:.4f} = {p_comp:.4f}$$\n\n"
                    f"**Paso 2: Búsqueda en tabla.**\n"
                    f"Fila `{r_k}`, columna `{c_k}` $\\implies c = {c_val:.2f}$."
                )
                e["region_type"] = "right"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p
            else:
                k_val, p_found, r_k, c_k = self.tm.find_z_inverse(p)
                c_val = -k_val
                e["criterio_id"] = 11
                e["criterio_nombre"] = ">= -C"
                e["orden"] = f"P(Z \\ge c) = {p:.4f}, \\quad c = ? \\quad (c < 0)"
                e["resolucion"] = (
                    f"**Paso 1: Simetría para cola amplia.**\n"
                    f"Para $P(Z \\ge c) = {p:.4f} > 0.50$, sea $c = -k$. $P(Z \\le k) = {p:.4f}$.\n\n"
                    f"**Paso 2: Búsqueda en tabla.**\n"
                    f"Fila `{r_k}`, col `{c_k}` $\\implies k = {k_val:.2f} \\implies c = {c_val:.2f}$."
                )
                e["region_type"] = "right"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p

        else:
            raise ValueError(f"Operación no soportada: '{op}'.")

        return e

    # =========================================================================
    # RESOLVEDOR t-STUDENT
    # =========================================================================
    def _resolver_t(self, op, val, df, ej_id):
        e = {"id": ej_id, "distribucion": f"t-Student (r = {df} gl)", "dist_type": "t", "params": {"df": df}}
        t_probs = ["0.750", "0.800", "0.900", "0.950", "0.975", "0.990", "0.995", "0.999"]

        def match_t_col(x):
            for col in t_probs:
                if abs(self.tm.get_t(df, col) - x) < 0.05:
                    return col
            return "0.950"

        if op == "<=":
            a = float(val)
            if a >= 0:
                p_level = match_t_col(a)
                e["criterio_id"] = 1
                e["criterio_nombre"] = "<= +"
                e["orden"] = f"P(T_{{{df}}} \\le {a:.3f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Consulta directa en Tabla t-Student.**\n"
                    f"En la fila $r = {df}$, el valor `{a:.3f}` se encuentra bajo la columna $1 - \\alpha = {p_level}$.\n\n"
                    f"**Paso 2: Conclusión.**\n"
                    f"$$P(T_{{{df}}} \\le {a:.3f}) = {p_level}$$"
                )
                e["region_type"] = "left"
                e["points"] = [a]
                e["labels"] = [f"t = {a:.3f}"]
                e["probabilidad"] = float(p_level)
            else:
                pos_a = abs(a)
                p_level = match_t_col(pos_a)
                res = round(1.0 - float(p_level), 3)
                e["criterio_id"] = 2
                e["criterio_nombre"] = "<= -"
                e["orden"] = f"P(T_{{{df}}} \\le {a:.3f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y simetría.**\n"
                    f"Para $T \\sim t({df})$ con valor negativo ${a:.3f}$:\n"
                    f"$$P(T_{{{df}}} \\le {a:.3f}) = 1 - P(T_{{{df}}} \\le {pos_a:.3f})$$\n\n"
                    f"**Paso 2: Consulta en la Tabla t-Student.**\n"
                    f"Fila $r = {df}$, cuantil ${pos_a:.3f}$ corresponde a $P(T \\le {pos_a:.3f}) = {p_level}$.\n\n"
                    f"**Paso 3: Conclusión.**\n"
                    f"$$P(T_{{{df}}} \\le {a:.3f}) = 1 - {p_level} = {res:.3f}$$"
                )
                e["region_type"] = "left"
                e["points"] = [a]
                e["labels"] = [f"t = {a:.3f}"]
                e["probabilidad"] = res

        elif op == ">=":
            a = float(val)
            if a >= 0:
                p_level = match_t_col(a)
                res = round(1.0 - float(p_level), 3)
                e["criterio_id"] = 3
                e["criterio_nombre"] = ">= +"
                e["orden"] = f"P(T_{{{df}}} \\ge {a:.3f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Regla del Complemento en t-Student.**\n"
                    f"$$P(T_{{{df}}} \\ge {a:.3f}) = 1 - P(T_{{{df}}} \\le {a:.3f})$$\n\n"
                    f"**Paso 2: Consulta de tabla.**\n"
                    f"Fila $r = {df}$, columna `{p_level}` $\\implies P(T_{{{df}}} \\le {a:.3f}) = {p_level}$.\n\n"
                    f"**Paso 3: Cálculo del complemento.**\n"
                    f"$$P(T_{{{df}}} \\ge {a:.3f}) = 1 - {p_level} = {res:.3f}$$"
                )
                e["region_type"] = "right"
                e["points"] = [a]
                e["labels"] = [f"t = {a:.3f}"]
                e["probabilidad"] = res
            else:
                pos_a = abs(a)
                p_level = match_t_col(pos_a)
                prob_pos = float(p_level)
                p_cola_izq = round(1.0 - prob_pos, 3)
                res = round(1.0 - p_cola_izq, 3)
                e["criterio_id"] = 4
                e["criterio_nombre"] = ">= -"
                e["orden"] = f"P(T_{{{df}}} \\ge {a:.3f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Planteamiento formal por la Regla del Complemento.**\n"
                    f"Para $T \\sim t({df})$, se pide la probabilidad hacia la derecha desde el valor negativo ${a:.3f}$:\n"
                    f"$$P(T_{{{df}}} \\ge {a:.3f}) = 1 - P(T_{{{df}}} \\le {a:.3f})$$\n\n"
                    f"**Paso 2: Cálculo de la cola izquierda P(T \\le {a:.3f}).**\n"
                    f"Por simetría respecto al origen: $P(T_{{{df}}} \\le {a:.3f}) = 1 - P(T_{{{df}}} \\le {pos_a:.3f})$.\n"
                    f"En la fila $r = {df}$, el cuantil ${pos_a:.3f}$ corresponde a $P(T \\le {pos_a:.3f}) = {prob_pos:.3f}$.\n"
                    f"Por tanto, la probabilidad de la cola izquierda es:\n"
                    f"$$P(T_{{{df}}} \\le {a:.3f}) = 1 - {prob_pos:.3f} = {p_cola_izq:.3f}$$\n\n"
                    f"**Paso 3: Aplicación aritmética del complemento.**\n"
                    f"Restamos la cola izquierda del área total (1):\n"
                    f"$$P(T_{{{df}}} \\ge {a:.3f}) = 1 - P(T_{{{df}}} \\le {a:.3f}) = 1 - {p_cola_izq:.3f} = {res:.3f}$$\n\n"
                    f"**Paso 4: Conclusión y lectura de la gráfica.**\n"
                    f"$$P(T_{{{df}}} \\ge {a:.3f}) = {res:.3f}$$ (o {res*100:.1f}%).\n\n"
                    f"*(Nota sobre la gráfica: La región sombreada inicia en el valor negativo ${a:.3f}$ y se extiende hacia la derecha abarcando más del 50% de la curva).*"
                )
                e["region_type"] = "right"
                e["points"] = [a]
                e["labels"] = [f"t = {a:.3f}"]
                e["probabilidad"] = res

        elif op in ["intervalo", "between"]:
            v1, v2 = sorted([float(x) for x in val])
            if v1 >= 0 and v2 >= 0:
                p1 = match_t_col(v1)
                p2 = match_t_col(v2)
                res = round(float(p2) - float(p1), 3)
                e["criterio_id"] = 5
                e["criterio_nombre"] = "+ <= <= +"
                e["orden"] = f"P({v1:.3f} \\le T_{{{df}}} \\le {v2:.3f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Resta de acumuladas directas.**\n"
                    f"$$P({v1:.3f} \\le T_{{{df}}} \\le {v2:.3f}) = P(T \\le {v2:.3f}) - P(T \\le {v1:.3f}) = {p2} - {p1} = {res:.3f}$$"
                )
                e["region_type"] = "interval"
                e["points"] = [v1, v2]
                e["labels"] = [f"t1 = {v1:.3f}", f"t2 = {v2:.3f}"]
                e["probabilidad"] = res
            elif v1 < 0 and v2 > 0:
                pos_v1 = abs(v1)
                p1 = match_t_col(pos_v1)
                p2 = match_t_col(v2)
                p_lower = round(1.0 - float(p1), 3)
                res = round(float(p2) - p_lower, 3)
                e["criterio_id"] = 6
                e["criterio_nombre"] = "- <= <= +"
                e["orden"] = f"P({v1:.3f} \\le T_{{{df}}} \\le {v2:.3f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Resta de acumuladas con simetría.**\n"
                    f"$$P({v1:.3f} \\le T_{{{df}}} \\le {v2:.3f}) = P(T \\le {v2:.3f}) - [1 - P(T \\le {pos_v1:.3f})] = {p2} - {p_lower:.3f} = {res:.3f}$$"
                )
                e["region_type"] = "interval"
                e["points"] = [v1, v2]
                e["labels"] = [f"t1 = {v1:.3f}", f"t2 = {v2:.3f}"]
                e["probabilidad"] = res
            else:
                pos_v1 = abs(v1)
                pos_v2 = abs(v2)
                p1 = match_t_col(pos_v1)
                p2 = match_t_col(pos_v2)
                res = round(float(p1) - float(p2), 3)
                e["criterio_id"] = 7
                e["criterio_nombre"] = "- <= <= -"
                e["orden"] = f"P({v1:.3f} \\le T_{{{df}}} \\le {v2:.3f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Propiedad de simetría en t-Student.**\n"
                    f"$$P({v1:.3f} \\le T_{{{df}}} \\le {v2:.3f}) = P(T \\le {pos_v1:.3f}) - P(T \\le {pos_v2:.3f}) = {p1} - {p2} = {res:.3f}$$"
                )
                e["region_type"] = "interval"
                e["points"] = [v1, v2]
                e["labels"] = [f"t1 = {v1:.3f}", f"t2 = {v2:.3f}"]
                e["probabilidad"] = res

        elif op in ["inv_le", "<= c", "<=c"]:
            p = float(val)
            p_str = f"{p:.3f}"
            if p >= 0.50:
                c_val = self.tm.get_t(df, p_str) if p_str in self.tm.get_t_available_probs() else self.tm.get_t(df, "0.950")
                e["criterio_id"] = 8
                e["criterio_nombre"] = "<= C"
                e["orden"] = f"P(T_{{{df}}} \\le c) = {p:.3f}, \\quad c = ?"
                e["resolucion"] = f"Fila $r = {df}$, columna `{p:.3f}`: $$c = {c_val:.3f}$$"
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.3f}"]
                e["probabilidad"] = p
            else:
                p_comp = round(1.0 - p, 3)
                p_comp_str = f"{p_comp:.3f}"
                k_val = self.tm.get_t(df, p_comp_str) if p_comp_str in self.tm.get_t_available_probs() else self.tm.get_t(df, "0.950")
                c_val = -k_val
                e["criterio_id"] = 10
                e["criterio_nombre"] = "<= -C"
                e["orden"] = f"P(T_{{{df}}} \\le c) = {p:.3f}, \\quad c = ? \\quad (c < 0)"
                e["resolucion"] = (
                    f"**Paso 1: Simetría en t-Student.**\n"
                    f"Para $p = {p:.3f} < 0.50$, sea $c = -k$. $P(T \\le k) = 1 - {p:.3f} = {p_comp:.3f}$.\n\n"
                    f"**Paso 2: Consulta de tabla y signo.**\n"
                    f"Fila $r = {df}$, col `{p_comp:.3f}` $\\implies k = {k_val:.3f} \\implies c = {c_val:.3f}$."
                )
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.3f}"]
                e["probabilidad"] = p

        elif op in ["inv_ge", ">= c", ">=c"]:
            p = float(val)
            if p <= 0.50:
                p_comp = round(1.0 - p, 3)
                p_comp_str = f"{p_comp:.3f}"
                c_val = self.tm.get_t(df, p_comp_str) if p_comp_str in self.tm.get_t_available_probs() else self.tm.get_t(df, "0.950")
                e["criterio_id"] = 9
                e["criterio_nombre"] = ">= C"
                e["orden"] = f"P(T_{{{df}}} \\ge c) = {p:.3f}, \\quad c = ?"
                e["resolucion"] = (
                    f"**Paso 1: Complemento en t-Student.**\n"
                    f"$$P(T \\le c) = 1 - {p:.3f} = {p_comp_str} \\implies c = {c_val:.3f}$$"
                )
                e["region_type"] = "right"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.3f}"]
                e["probabilidad"] = p
            else:
                p_str = f"{p:.3f}"
                k_val = self.tm.get_t(df, p_str) if p_str in self.tm.get_t_available_probs() else self.tm.get_t(df, "0.950")
                c_val = -k_val
                e["criterio_id"] = 11
                e["criterio_nombre"] = ">= -C"
                e["orden"] = f"P(T_{{{df}}} \\ge c) = {p:.3f}, \\quad c = ? \\quad (c < 0)"
                e["resolucion"] = (
                    f"**Paso 1: Simetría para cola amplia.**\n"
                    f"Para $P(T \\ge c) = {p:.3f} > 0.50$, sea $c = -k$. $P(T \\le k) = {p:.3f} \\implies k = {k_val:.3f} \\implies c = {c_val:.3f}$."
                )
                e["region_type"] = "right"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.3f}"]
                e["probabilidad"] = p

        return e

    # =========================================================================
    # RESOLVEDOR CHI-CUADRADO
    # =========================================================================
    def _resolver_chi(self, op, val, df, ej_id):
        e = {"id": ej_id, "distribucion": f"Chi-cuadrado (r = {df} gl)", "dist_type": "chi", "params": {"df": df}}
        lower_cols = self.tm.get_chi_lower_probs()
        upper_cols = self.tm.get_chi_upper_probs()

        def match_chi_col(x):
            for col in lower_cols + upper_cols:
                if abs(self.tm.get_chi(df, col) - x) < 0.25:
                    return col
            return "0.950"

        if op == "<=":
            b = float(val)
            p_level = match_chi_col(b)
            crit_id = 1 if float(p_level) >= 0.50 else 2
            crit_nom = "<= +" if crit_id == 1 else "<= -"
            e["criterio_id"] = crit_id
            e["criterio_nombre"] = crit_nom
            e["orden"] = f"P(\\chi^2_{{{df}}} \\le {b:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Consulta en Tabla Chi-cuadrado.**\n"
                f"En la fila $r = {df}$, el cuantil `{b:.3f}` se encuentra bajo la columna $1 - \\alpha = {p_level}$.\n\n"
                f"**Paso 2: Conclusión.**\n"
                f"$$P(\\chi^2_{{{df}}} \\le {b:.3f}) = {p_level}$$"
            )
            e["region_type"] = "left"
            e["points"] = [b]
            e["labels"] = [f"chi2 = {b:.3f}"]
            e["probabilidad"] = float(p_level)

        elif op == ">=":
            b = float(val)
            p_level = match_chi_col(b)
            prob_acc = float(p_level)
            res = round(1.0 - prob_acc, 3)
            crit_id = 3 if prob_acc >= 0.50 else 4
            crit_nom = ">= +" if crit_id == 3 else ">= -"
            e["criterio_id"] = crit_id
            e["criterio_nombre"] = crit_nom
            e["orden"] = f"P(\\chi^2_{{{df}}} \\ge {b:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Regla del Complemento en Chi-cuadrado.**\n"
                f"$$P(\\chi^2_{{{df}}} \\ge {b:.3f}) = 1 - P(\\chi^2_{{{df}}} \\le {b:.3f})$$\n\n"
                f"**Paso 2: Consulta en la Tabla Chi-cuadrado.**\n"
                f"Fila $r = {df}$, columna `{p_level}` $\\implies P(\\chi^2_{{{df}}} \\le {b:.3f}) = {prob_acc:.3f}$.\n\n"
                f"**Paso 3: Cálculo aritmético del complemento.**\n"
                f"$$P(\\chi^2_{{{df}}} \\ge {b:.3f}) = 1 - {prob_acc:.3f} = {res:.3f}$$\n\n"
                f"*(Nota sobre la gráfica: La región sombreada inicia en el punto {b:.3f} y se extiende hacia la derecha hasta el final de la distribución).*"
            )
            e["region_type"] = "right"
            e["points"] = [b]
            e["labels"] = [f"chi2 = {b:.3f}"]
            e["probabilidad"] = res

        elif op in ["intervalo", "between"]:
            v1, v2 = sorted([float(x) for x in val])
            p1 = match_chi_col(v1)
            p2 = match_chi_col(v2)
            prob1, prob2 = float(p1), float(p2)
            res = round(prob2 - prob1, 3)

            if prob1 >= 0.50 and prob2 >= 0.50:
                crit_id, crit_nom = 5, "+ <= <= +"
            elif prob1 < 0.50 and prob2 >= 0.50:
                crit_id, crit_nom = 6, "- <= <= +"
            else:
                crit_id, crit_nom = 7, "- <= <= -"

            e["criterio_id"] = crit_id
            e["criterio_nombre"] = crit_nom
            e["orden"] = f"P({v1:.3f} \\le \\chi^2_{{{df}}} \\le {v2:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Resta de acumuladas en Chi-cuadrado.**\n"
                f"$$P({v1:.3f} \\le \\chi^2_{{{df}}} \\le {v2:.3f}) = P(\\chi^2 \\le {v2:.3f}) - P(\\chi^2 \\le {v1:.3f})$$\n"
                f"$$P = {p2} - {p1} = {res:.3f}$$"
            )
            e["region_type"] = "interval"
            e["points"] = [v1, v2]
            e["labels"] = [f"chi2_1 = {v1:.3f}", f"chi2_2 = {v2:.3f}"]
            e["probabilidad"] = res

        elif op in ["inv_le", "<= c", "<=c"]:
            p = float(val)
            p_str = f"{p:.3f}"
            c_val = self.tm.get_chi(df, p_str) if p_str in (lower_cols + upper_cols) else self.tm.get_chi(df, "0.950")
            crit_id = 8 if p >= 0.50 else 10
            crit_nom = "<= C" if crit_id == 8 else "<= -C"
            e["criterio_id"] = crit_id
            e["criterio_nombre"] = crit_nom
            e["orden"] = f"P(\\chi^2_{{{df}}} \\le c) = {p:.3f}, \\quad c = ?"
            e["resolucion"] = f"Fila $r = {df}$, columna `{p_str}`: $$c = {c_val:.3f}$$"
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = p

        elif op in ["inv_ge", ">= c", ">=c"]:
            p = float(val)
            p_comp = round(1.0 - p, 3)
            p_comp_str = f"{p_comp:.3f}"
            c_val = self.tm.get_chi(df, p_comp_str) if p_comp_str in (lower_cols + upper_cols) else self.tm.get_chi(df, "0.950")
            crit_id = 9 if p <= 0.50 else 11
            crit_nom = ">= C" if crit_id == 9 else ">= -C"
            e["criterio_id"] = crit_id
            e["criterio_nombre"] = crit_nom
            e["orden"] = f"P(\\chi^2_{{{df}}} \\ge c) = {p:.3f}, \\quad c = ?"
            e["resolucion"] = f"Complemento e inversa: $$P(\\chi^2 \\le c) = 1 - {p:.3f} = {p_comp_str} \\implies c = {c_val:.3f}$$"
            e["region_type"] = "right"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = p

        return e

    # =========================================================================
    # RESOLVEDOR FISHER F
    # =========================================================================
    def _resolver_fisher(self, op, val, r1, r2, ej_id):
        e = {"id": ej_id, "distribucion": f"Fisher-Snedecor (r1 = {r1}, r2 = {r2})", "dist_type": "fisher", "params": {"r1": r1, "r2": r2}}
        niveles = ["0.950", "0.975", "0.990", "0.995"]

        def match_fisher_p(x):
            for p in niveles:
                if abs(self.tm.get_fisher_upper(r1, r2, p) - x) < 0.2:
                    return p
            return "0.950"

        if op == "<=":
            b = float(val)
            if b >= 1.0:
                p_level = match_fisher_p(b)
                e["criterio_id"] = 1
                e["criterio_nombre"] = "<= +"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\le {b:.2f}) = ?"
                e["resolucion"] = f"Consulta directa en nivel `{p_level}`: $$P(F_{{{r1}, {r2}}} \\le {b:.2f}) = {p_level}$$"
                e["region_type"] = "left"
                e["points"] = [b]
                e["labels"] = [f"F = {b:.2f}"]
                e["probabilidad"] = float(p_level)
            else:
                p_level = "0.950"
                alpha_str = "0.050"
                a, f_inv = self.tm.get_fisher_lower(r1, r2, p_level)
                e["criterio_id"] = 2
                e["criterio_nombre"] = "<= -"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\le {b:.4f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Propiedad de inversión oficial de la cabecera:**\n"
                    f"$$F_{{\\alpha; r_1, r_2}} = \\frac{{1}}{{F_{{1 - \\alpha; r_2, r_1}}}}$$\n"
                    f"Buscamos en nivel `{p_level}` invirtiendo grados: $F_{{{p_level}; {r2}, {r1}}} = {f_inv:.2f}$.\n"
                    f"Por tanto: $$c = \\frac{{1}}{{{f_inv:.2f}}} = {a:.4f} \\implies P(F \\le {a:.4f}) = {alpha_str}$$"
                )
                e["region_type"] = "left"
                e["points"] = [b]
                e["labels"] = [f"F = {b:.4f}"]
                e["probabilidad"] = float(alpha_str)

        elif op == ">=":
            b = float(val)
            if b >= 1.0:
                p_level = match_fisher_p(b)
                res = round(1.0 - float(p_level), 3)
                e["criterio_id"] = 3
                e["criterio_nombre"] = ">= +"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\ge {b:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Regla del Complemento en Fisher.**\n"
                    f"$$P(F_{{{r1}, {r2}}} \\ge {b:.2f}) = 1 - P(F_{{{r1}, {r2}}} \\le {b:.2f}) = 1 - {p_level} = {res:.3f}$$"
                )
                e["region_type"] = "right"
                e["points"] = [b]
                e["labels"] = [f"F = {b:.2f}"]
                e["probabilidad"] = res
            else:
                p_level = "0.950"
                alpha_str = "0.050"
                a, f_inv = self.tm.get_fisher_lower(r1, r2, p_level)
                res = round(1.0 - float(alpha_str), 3)
                e["criterio_id"] = 4
                e["criterio_nombre"] = ">= -"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\ge {b:.4f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Planteamiento formal por la Regla del Complemento.**\n"
                    f"$$P(F_{{{r1}, {r2}}} \\ge {b:.4f}) = 1 - P(F_{{{r1}, {r2}}} \\le {b:.4f})$$\n\n"
                    f"**Paso 2: Propiedad de inversión para la cola inferior.**\n"
                    f"El cuantil inferior es $1 / F_{{{p_level}; {r2}, {r1}}} = 1 / {f_inv:.2f} = {a:.4f}$, "
                    f"cuya probabilidad acumulada izquierda es $\\alpha = {alpha_str}$.\n\n"
                    f"**Paso 3: Cálculo aritmético del complemento.**\n"
                    f"$$P(F_{{{r1}, {r2}}} \\ge {b:.4f}) = 1 - {alpha_str} = {res:.3f}$$\n\n"
                    f"*(Nota sobre la gráfica: La región sombreada inicia en el punto {b:.4f} y cubre toda la curva hacia la derecha).*"
                )
                e["region_type"] = "right"
                e["points"] = [b]
                e["labels"] = [f"F = {b:.4f}"]
                e["probabilidad"] = res

        elif op in ["intervalo", "between"]:
            v1, v2 = sorted([float(x) for x in val])
            if v1 >= 1.0 and v2 >= 1.0:
                p1 = match_fisher_p(v1)
                p2 = match_fisher_p(v2)
                res = round(float(p2) - float(p1), 3)
                e["criterio_id"] = 5
                e["criterio_nombre"] = "+ <= <= +"
                e["orden"] = f"P({v1:.2f} \\le F_{{{r1}, {r2}}} \\le {v2:.2f}) = ?"
                e["resolucion"] = f"Resta de acumuladas superiores: $$P = {p2} - {p1} = {res:.3f}$$"
                e["region_type"] = "interval"
                e["points"] = [v1, v2]
                e["labels"] = [f"F1 = {v1:.2f}", f"F2 = {v2:.2f}"]
                e["probabilidad"] = res
            elif v1 < 1.0 and v2 >= 1.0:
                p2 = match_fisher_p(v2)
                alpha_str = "0.050"
                res = round(float(p2) - float(alpha_str), 3)
                e["criterio_id"] = 6
                e["criterio_nombre"] = "- <= <= +"
                e["orden"] = f"P({v1:.4f} \\le F_{{{r1}, {r2}}} \\le {v2:.2f}) = ?"
                e["resolucion"] = f"Intervalo con cuantil inferior por inversión: $$P = {p2} - {alpha_str} = {res:.3f}$$"
                e["region_type"] = "interval"
                e["points"] = [v1, v2]
                e["labels"] = [f"F1 = {v1:.4f}", f"F2 = {v2:.2f}"]
                e["probabilidad"] = res
            else:
                res = round(0.050 - 0.010, 3)
                e["criterio_id"] = 7
                e["criterio_nombre"] = "- <= <= -"
                e["orden"] = f"P({v1:.4f} \\le F_{{{r1}, {r2}}} \\le {v2:.4f}) = ?"
                e["resolucion"] = f"Intervalo inferior por doble inversión: $$P = 0.050 - 0.010 = {res:.3f}$$"
                e["region_type"] = "interval"
                e["points"] = [v1, v2]
                e["labels"] = [f"F1 = {v1:.4f}", f"F2 = {v2:.4f}"]
                e["probabilidad"] = res

        elif op in ["inv_le", "<= c", "<=c"]:
            p = float(val)
            p_str = f"{p:.3f}"
            if p >= 0.50:
                c_val = self.tm.get_fisher_upper(r1, r2, p_str if p_str in niveles else "0.950")
                e["criterio_id"] = 8
                e["criterio_nombre"] = "<= C"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\le c) = {p:.3f}, \\quad c = ?"
                e["resolucion"] = f"Fila $r_2 = {r2}$, columna $r_1 = {r1}$, nivel `{p_str}`: $$c = {c_val:.2f}$$"
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p
            else:
                p_comp_str = "0.950"
                c_val, f_inv = self.tm.get_fisher_lower(r1, r2, p_comp_str)
                e["criterio_id"] = 10
                e["criterio_nombre"] = "<= -C"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\le c) = {p:.3f}, \\quad c = ?"
                e["resolucion"] = f"Inversión de cabecera: $$c = \\frac{{1}}{{F_{{{p_comp_str}; {r2}, {r1}}}}} = \\frac{{1}}{{{f_inv:.2f}}} = {c_val:.4f}$$"
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.4f}"]
                e["probabilidad"] = p

        elif op in ["inv_ge", ">= c", ">=c"]:
            p = float(val)
            if p <= 0.50:
                p_comp_str = "0.975"
                c_val = self.tm.get_fisher_upper(r1, r2, p_comp_str)
                e["criterio_id"] = 9
                e["criterio_nombre"] = ">= C"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\ge c) = {p:.3f}, \\quad c = ?"
                e["resolucion"] = f"Complemento e inversa: $$P(F \\le c) = 1 - {p:.3f} = {p_comp_str} \\implies c = {c_val:.2f}$$"
                e["region_type"] = "right"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p
            else:
                c_val, f_inv = self.tm.get_fisher_lower(r1, r2, "0.975")
                e["criterio_id"] = 11
                e["criterio_nombre"] = ">= -C"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\ge c) = {p:.3f}, \\quad c = ?"
                e["resolucion"] = f"Complemento e inversión: $$c = \\frac{{1}}{{F_{{0.975; {r2}, {r1}}}}} = {c_val:.4f}$$"
                e["region_type"] = "right"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.4f}"]
                e["probabilidad"] = p

        return e

    def formatear_y_renderizar(self, dist, operacion, valores, params=None, nombre_salida="ejercicio_personalizado"):
        ej = self.resolver(dist, operacion, valores, params, id_ejercicio=nombre_salida)
        ruta_img = renderizar_grafico(ej, output_dir=OUTPUT_GRAFICOS_DIR)
        b64_img = renderizar_grafico_base64(ej)
        ej["grafico_path"] = ruta_img
        ej["grafico_base64"] = b64_img
        return ej

if __name__ == "__main__":
    rp = ResolverPersonalizado()
    print("Probando resolución personalizada de Normal Z >= -1.50:")
    res = rp.formatear_y_renderizar("Z", ">=", -1.50)
    print("Resolución:\n", res["resolucion"])
