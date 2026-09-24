"""
Módulo de Resolución de Ejercicios Personalizados.
Permite a cualquier usuario/estudiante introducir un ejercicio arbitrario:
- Seleccionar la tabla / distribución: Normal Z, t-Student, Chi-cuadrado, Fisher F.
- Suministrar los parámetros y valores iniciales.
- Reconocer automáticamente el patrón contra los 11 criterios oficiales.
- Generar:
  1. Orden del ejercicio estructurada
  2. Resolución analítica detallada paso a paso citando las tablas oficiales
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
        """
        Resuelve un ejercicio reconociendo el patrón analítico.
        - dist: 'Z', 't', 'chi', 'fisher'
        - operacion: '<=', '>=', 'intervalo', 'inv_le', 'inv_ge'
        - valores: float o tupla de floats
        - params: dict con parámetros requeridos (ej. {'df': 15} o {'r1': 5, 'r2': 10})
        """
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

    # ------------------ RESOLVEDOR NORMAL Z ------------------
    def _resolver_z(self, op, val, ej_id):
        e = {"id": ej_id, "distribucion": "Normal Estándar", "dist_type": "Z", "params": {}}

        if op == "<=":
            a = float(val)
            if a >= 0:
                # Criterio 1: <= +
                prob, r_k, c_k = self.tm.get_z(a)
                e["criterio_id"] = 1
                e["criterio_nombre"] = "<= +"
                e["orden"] = f"P(Z \\le {a:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Variable aleatoria Normal Estándar: $Z \\sim \\mathcal{{N}}(0, 1)$. "
                    f"Se evalúa la probabilidad acumulada directa hasta el valor positivo $a = {a:.2f}$.\n\n"
                    f"**Paso 2: Expresión matemática.**\n"
                    f"$$P(Z \\le {a:.2f})$$\n\n"
                    f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                    f"Fila `{r_k}`, columna `{c_k}`. Intersección:\n"
                    f"$$P(Z \\le {a:.2f}) = {prob:.4f}$$\n\n"
                    f"**Paso 4: Conclusión.**\n"
                    f"$$P(Z \\le {a:.2f}) = {prob:.4f}$$ (o {prob*100:.2f}%)."
                )
                e["region_type"] = "left"
                e["points"] = [a]
                e["labels"] = [f"z = {a:.2f}"]
                e["probabilidad"] = prob
            else:
                # Criterio 2: <= -
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
                    f"Por simetría respecto al origen: $P(Z \\le {a:.2f}) = P(Z \\ge {pos_a:.2f}) = 1 - P(Z \\le {pos_a:.2f})$.\n\n"
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
                # Criterio 3: >= +
                prob, r_k, c_k = self.tm.get_z(a)
                res = round(1.0 - prob, 4)
                e["criterio_id"] = 3
                e["criterio_nombre"] = ">= +"
                e["orden"] = f"P(Z \\ge {a:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Para $Z \\sim \\mathcal{{N}}(0, 1)$, cola superior desde el valor positivo $a = {a:.2f}$.\n\n"
                    f"**Paso 2: Regla del complemento.**\n"
                    f"$$P(Z \\ge {a:.2f}) = 1 - P(Z \\le {a:.2f})$$\n\n"
                    f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                    f"En fila `{r_k}`, columna `{c_k}`: $P(Z \\le {a:.2f}) = {prob:.4f}$.\n\n"
                    f"**Paso 4: Cálculo analítico.**\n"
                    f"$$P(Z \\ge {a:.2f}) = 1 - {prob:.4f} = {res:.4f}$$\n\n"
                    f"**Paso 5: Conclusión.**\n"
                    f"$$P(Z \\ge {a:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
                )
                e["region_type"] = "right"
                e["points"] = [a]
                e["labels"] = [f"z = {a:.2f}"]
                e["probabilidad"] = res
            else:
                # Criterio 4: >= -
                pos_a = abs(a)
                prob, r_k, c_k = self.tm.get_z(pos_a)
                e["criterio_id"] = 4
                e["criterio_nombre"] = ">= -"
                e["orden"] = f"P(Z \\ge {a:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Para $Z \\sim \\mathcal{{N}}(0, 1)$, cola derecha desde el valor negativo ${a:.2f}$.\n\n"
                    f"**Paso 2: Propiedad de simetría.**\n"
                    f"Por simetría: $P(Z \\ge {a:.2f}) = P(Z \\le {pos_a:.2f})$.\n\n"
                    f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                    f"En fila `{r_k}`, columna `{c_k}`: $P(Z \\le {pos_a:.2f}) = {prob:.4f}$.\n\n"
                    f"**Paso 4: Conclusión.**\n"
                    f"$$P(Z \\ge {a:.2f}) = {prob:.4f}$$ (o {prob*100:.2f}%)."
                )
                e["region_type"] = "right"
                e["points"] = [a]
                e["labels"] = [f"z = {a:.2f}"]
                e["probabilidad"] = prob

        elif op in ["intervalo", "between"]:
            v1, v2 = sorted([float(x) for x in val])
            if v1 < 0 and v2 > 0:
                # Criterio 5: - <= <= +
                pos_v1 = abs(v1)
                p1, r1_k, c1_k = self.tm.get_z(pos_v1)
                p2, r2_k, c2_k = self.tm.get_z(v2)
                p_lower = round(1.0 - p1, 4)
                res = round(p2 - p_lower, 4)
                e["criterio_id"] = 5
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

            elif v1 >= 0 and v2 >= 0:
                # Criterio 6: + <= <= +
                p1, r1_k, c1_k = self.tm.get_z(v1)
                p2, r2_k, c2_k = self.tm.get_z(v2)
                res = round(p2 - p1, 4)
                e["criterio_id"] = 6
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

            else:
                # Criterio 7: - <= <= -
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
                    f"Por simetría, equivale al intervalo reflejado $[{pos_v2:.2f}, {pos_v1:.2f}]$:\n"
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
                # Criterio 8: <= C con c > 0
                c_val, p_found, r_k, c_k = self.tm.find_z_inverse(p)
                e["criterio_id"] = 8
                e["criterio_nombre"] = "<= C"
                e["orden"] = f"P(Z \\le c) = {p:.4f}, \\quad c = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y análisis.**\n"
                    f"Búsqueda inversa directa para $Z \\sim \\mathcal{{N}}(0, 1)$ con $P(Z \\le c) = {p:.4f}$ ($c > 0$).\n\n"
                    f"**Paso 2: Búsqueda en el cuerpo de la Tabla Normal.**\n"
                    f"Se ubica `{p_found:.4f}` en fila `{r_k}` y columna `{c_k}`.\n\n"
                    f"**Paso 3: Conclusión.**\n"
                    f"$$c = {r_k} + {c_k} = {c_val:.2f}$$"
                )
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p_found
            else:
                # Criterio 10: <= -C con c < 0
                p_comp = round(1.0 - p, 4)
                k_val, p_found, r_k, c_k = self.tm.find_z_inverse(p_comp)
                c_val = -k_val
                e["criterio_id"] = 10
                e["criterio_nombre"] = "<= -C"
                e["orden"] = f"P(Z \\le c) = {p:.4f}, \\quad c = ? \\quad (c < 0)"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y análisis.**\n"
                    f"Búsqueda inversa con probabilidad $p = {p:.4f} < 0.50$, luego $c < 0$.\n\n"
                    f"**Paso 2: Simetría.**\n"
                    f"Sea $c = -k$. $P(Z \\le -k) = 1 - P(Z \\le k) = {p:.4f} \\implies P(Z \\le k) = {p_comp:.4f}$.\n\n"
                    f"**Paso 3: Búsqueda en tabla.**\n"
                    f"Ubicado en fila `{r_k}`, col `{c_k}` $\\implies k = {k_val:.2f}$.\n\n"
                    f"**Paso 4: Conclusión.**\n"
                    f"$$c = -k = {c_val:.2f}$$"
                )
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p

        elif op in ["inv_ge", ">= c", ">=c"]:
            p = float(val)
            if p <= 0.50:
                # Criterio 9: >= C con c > 0
                p_comp = round(1.0 - p, 4)
                c_val, p_found, r_k, c_k = self.tm.find_z_inverse(p_comp)
                e["criterio_id"] = 9
                e["criterio_nombre"] = ">= C"
                e["orden"] = f"P(Z \\ge c) = {p:.4f}, \\quad c = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y análisis.**\n"
                    f"Búsqueda inversa cola derecha con $P(Z \\ge c) = {p:.4f}$ ($c > 0$).\n\n"
                    f"**Paso 2: Complemento.**\n"
                    f"$$P(Z \\le c) = 1 - {p:.4f} = {p_comp:.4f}$$\n\n"
                    f"**Paso 3: Búsqueda en tabla.**\n"
                    f"Ubicado en fila `{r_k}`, columna `{c_k}` $\\implies c = {c_val:.2f}$.\n\n"
                    f"**Paso 4: Conclusión.**\n"
                    f"$$c = {c_val:.2f}$$"
                )
                e["region_type"] = "right"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p
            else:
                # Criterio 11: >= -C con c < 0
                k_val, p_found, r_k, c_k = self.tm.find_z_inverse(p)
                c_val = -k_val
                e["criterio_id"] = 11
                e["criterio_nombre"] = ">= -C"
                e["orden"] = f"P(Z \\ge c) = {p:.4f}, \\quad c = ? \\quad (c < 0)"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y análisis.**\n"
                    f"Búsqueda inversa cola derecha con área amplia $P(Z \\ge c) = {p:.4f} > 0.50$, luego $c < 0$.\n\n"
                    f"**Paso 2: Simetría.**\n"
                    f"Sea $c = -k$. $P(Z \\ge -k) = P(Z \\le k) = {p:.4f}$.\n\n"
                    f"**Paso 3: Búsqueda en tabla.**\n"
                    f"Ubicado en fila `{r_k}`, columna `{c_k}` $\\implies k = {k_val:.2f}$.\n\n"
                    f"**Paso 4: Conclusión.**\n"
                    f"$$c = -k = {c_val:.2f}$$"
                )
                e["region_type"] = "right"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.2f}"]
                e["probabilidad"] = p

        else:
            raise ValueError(f"Operación no soportada: '{op}'.")

        return e

    # ------------------ RESOLVEDOR t-STUDENT ------------------
    def _resolver_t(self, op, val, df, ej_id):
        e = {"id": ej_id, "distribucion": f"t-Student (r = {df} gl)", "dist_type": "t", "params": {"df": df}}
        
        if op == "<=":
            a = float(val)
            if a >= 0:
                e["criterio_id"] = 1
                e["criterio_nombre"] = "<= +"
                # Buscar nivel correspondiente
                col_found = None
                for col in self.tm.get_t_available_probs():
                    if abs(self.tm.get_t(df, col) - a) < 0.05:
                        col_found = col
                        break
                p_level = col_found or "0.950"
                e["orden"] = f"P(T_{{{df}}} \\le {a:.3f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Variable $T \\sim t({df})$. Se evalúa la probabilidad acumulada hasta $a = {a:.3f}$.\n\n"
                    f"**Paso 2: Búsqueda en la Tabla t-Student.**\n"
                    f"En la fila $r = {df}$, el valor `{a:.3f}` se encuentra bajo la columna $1 - \\alpha = {p_level}$.\n\n"
                    f"**Paso 3: Conclusión.**\n"
                    f"$$P(T_{{{df}}} \\le {a:.3f}) = {p_level}$$"
                )
                e["region_type"] = "left"
                e["points"] = [a]
                e["labels"] = [f"t = {a:.3f}"]
                e["probabilidad"] = float(p_level)
            else:
                pos_a = abs(a)
                col_found = None
                for col in self.tm.get_t_available_probs():
                    if abs(self.tm.get_t(df, col) - pos_a) < 0.05:
                        col_found = col
                        break
                p_level = col_found or "0.975"
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

        elif op in ["inv_le", "<= c", "<=c"]:
            p = float(val)
            p_str = f"{p:.3f}"
            if p >= 0.50:
                c_val = self.tm.get_t(df, p_str) if p_str in self.tm.get_t_available_probs() else self.tm.get_t(df, "0.950")
                e["criterio_id"] = 8
                e["criterio_nombre"] = "<= C"
                e["orden"] = f"P(T_{{{df}}} \\le c) = {p:.3f}, \\quad c = ?"
                e["resolucion"] = (
                    f"**Paso 1: Búsqueda inversa en Tabla t-Student.**\n"
                    f"En la fila $r = {df}$ y columna `{p:.3f}`, el valor crítico es:\n"
                    f"$$c = {c_val:.3f}$$"
                )
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
                    f"**Paso 1: Simetría e inversión.**\n"
                    f"Para $p = {p:.3f} < 0.50$, sea $c = -k$. $P(T \\le k) = 1 - {p:.3f} = {p_comp:.3f}$.\n\n"
                    f"**Paso 2: Consulta de tabla y signo.**\n"
                    f"En fila $r = {df}$ y col `{p_comp:.3f}`: $k = {k_val:.3f} \\implies c = -{k_val:.3f}$."
                )
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.3f}"]
                e["probabilidad"] = p

        else:
            # Fallback genérico para t-Student
            a = float(val) if not isinstance(val, (list, tuple)) else float(val[0])
            e["criterio_id"] = 3
            e["criterio_nombre"] = ">= +"
            e["orden"] = f"P(T_{{{df}}} \\ge {a:.3f}) = ?"
            e["resolucion"] = f"Resolución analítica para $T_{{{df}}}$."
            e["region_type"] = "right"
            e["points"] = [a]
            e["labels"] = [f"t = {a:.3f}"]
            e["probabilidad"] = 0.05

        return e

    # ------------------ RESOLVEDOR CHI-CUADRADO ------------------
    def _resolver_chi(self, op, val, df, ej_id):
        e = {"id": ej_id, "distribucion": f"Chi-cuadrado (r = {df} gl)", "dist_type": "chi", "params": {"df": df}}
        
        if op == "<=":
            b = float(val)
            col_found = None
            for col in self.tm.get_chi_lower_probs() + self.tm.get_chi_upper_probs():
                if abs(self.tm.get_chi(df, col) - b) < 0.1:
                    col_found = col
                    break
            p_level = col_found or "0.950"
            crit_id = 1 if float(p_level) >= 0.50 else 2
            crit_nom = "<= +" if crit_id == 1 else "<= -"
            e["criterio_id"] = crit_id
            e["criterio_nombre"] = crit_nom
            e["orden"] = f"P(\\chi^2_{{{df}}} \\le {b:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y modelo.**\n"
                f"Variable $X \\sim \\chi^2({df})$ con soporte no negativo.\n\n"
                f"**Paso 2: Consulta en la Tabla Chi-cuadrado.**\n"
                f"En la fila $r = {df}$, el valor `{b:.3f}` se encuentra bajo la columna $1 - \\alpha = {p_level}$.\n\n"
                f"**Paso 3: Conclusión.**\n"
                f"$$P(\\chi^2_{{{df}}} \\le {b:.3f}) = {p_level}$$"
            )
            e["region_type"] = "left"
            e["points"] = [b]
            e["labels"] = [f"chi2 = {b:.3f}"]
            e["probabilidad"] = float(p_level)

        elif op in ["inv_le", "<= c", "<=c"]:
            p = float(val)
            p_str = f"{p:.3f}"
            c_val = self.tm.get_chi(df, p_str) if p_str in (self.tm.get_chi_lower_probs() + self.tm.get_chi_upper_probs()) else self.tm.get_chi(df, "0.950")
            crit_id = 8 if p >= 0.50 else 10
            crit_nom = "<= C" if crit_id == 8 else "<= -C"
            e["criterio_id"] = crit_id
            e["criterio_nombre"] = crit_nom
            e["orden"] = f"P(\\chi^2_{{{df}}} \\le c) = {p:.3f}, \\quad c = ?"
            e["resolucion"] = (
                f"**Paso 1: Búsqueda inversa en Tabla Chi-cuadrado.**\n"
                f"En la fila $r = {df}$ y columna `{p_str}`:\n"
                f"$$c = \\chi^2_{{{p_str}; {df}}} = {c_val:.3f}$$"
            )
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = p

        else:
            b = float(val) if not isinstance(val, (list, tuple)) else float(val[0])
            e["criterio_id"] = 3
            e["criterio_nombre"] = ">= +"
            e["orden"] = f"P(\\chi^2_{{{df}}} \\ge {b:.3f}) = ?"
            e["resolucion"] = f"Resolución analítica para $\\chi^2_{{{df}}}$."
            e["region_type"] = "right"
            e["points"] = [b]
            e["labels"] = [f"chi2 = {b:.3f}"]
            e["probabilidad"] = 0.05

        return e

    # ------------------ RESOLVEDOR FISHER F ------------------
    def _resolver_fisher(self, op, val, r1, r2, ej_id):
        e = {"id": ej_id, "distribucion": f"Fisher-Snedecor (r1 = {r1}, r2 = {r2})", "dist_type": "fisher", "params": {"r1": r1, "r2": r2}}
        
        if op == "<=":
            b = float(val)
            if b >= 1.0:
                p_level = "0.950"
                e["criterio_id"] = 1
                e["criterio_nombre"] = "<= +"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\le {b:.2f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Identificación y modelo.**\n"
                    f"Variable $F \\sim \\mathcal{{F}}({r1}, {r2})$.\n\n"
                    f"**Paso 2: Consulta en la Tabla Fisher.**\n"
                    f"En nivel `{p_level}`, fila $r_2 = {r2}$, columna $r_1 = {r1}$:\n"
                    f"$$F_{{{p_level}; {r1}, {r2}}} = {b:.2f}$$\n\n"
                    f"**Paso 3: Conclusión.**\n"
                    f"$$P(F_{{{r1}, {r2}}} \\le {b:.2f}) = {p_level}$$"
                )
                e["region_type"] = "left"
                e["points"] = [b]
                e["labels"] = [f"F = {b:.2f}"]
                e["probabilidad"] = float(p_level)
            else:
                p_level = "0.950"
                a, f_inv = self.tm.get_fisher_lower(r1, r2, p_level)
                e["criterio_id"] = 2
                e["criterio_nombre"] = "<= -"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\le {b:.4f}) = ?"
                e["resolucion"] = (
                    f"**Paso 1: Propiedad de inversión oficial.**\n"
                    f"$$F_{{\\alpha; r_1, r_2}} = \\frac{{1}}{{F_{{1 - \\alpha; r_2, r_1}}}}$$\n"
                    f"Con $F_{{{p_level}; {r2}, {r1}}} = {f_inv:.2f} \\implies a = {a:.4f}$.\n\n"
                    f"**Paso 2: Conclusión.**\n"
                    f"$$P(F_{{{r1}, {r2}}} \\le {a:.4f}) = 0.050$$"
                )
                e["region_type"] = "left"
                e["points"] = [b]
                e["labels"] = [f"F = {b:.4f}"]
                e["probabilidad"] = 0.05

        elif op in ["inv_le", "<= c", "<=c"]:
            p = float(val)
            p_str = f"{p:.3f}"
            if p >= 0.50:
                c_val = self.tm.get_fisher_upper(r1, r2, p_str if p_str in self.tm.get_fisher_probs() else "0.950")
                e["criterio_id"] = 8
                e["criterio_nombre"] = "<= C"
                e["orden"] = f"P(F_{{{r1}, {r2}}} \\le c) = {p:.3f}, \\quad c = ?"
                e["resolucion"] = (
                    f"**Paso 1: Búsqueda inversa directa en Tabla Fisher.**\n"
                    f"Fila $r_2 = {r2}$, columna $r_1 = {r1}$, nivel `{p_str}`:\n"
                    f"$$c = {c_val:.2f}$$"
                )
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
                e["resolucion"] = (
                    f"**Paso 1: Propiedad de inversión oficial.**\n"
                    f"$$c = \\frac{{1}}{{F_{{{p_comp_str}; {r2}, {r1}}}}} = \\frac{{1}}{{{f_inv:.2f}}} = {c_val:.4f}$$"
                )
                e["region_type"] = "left"
                e["points"] = [c_val]
                e["labels"] = [f"c = {c_val:.4f}"]
                e["probabilidad"] = p

        else:
            b = float(val) if not isinstance(val, (list, tuple)) else float(val[0])
            e["criterio_id"] = 3
            e["criterio_nombre"] = ">= +"
            e["orden"] = f"P(F_{{{r1}, {r2}}} \\ge {b:.2f}) = ?"
            e["resolucion"] = f"Resolución analítica para $F_{{{r1}, {r2}}}$."
            e["region_type"] = "right"
            e["points"] = [b]
            e["labels"] = [f"F = {b:.2f}"]
            e["probabilidad"] = 0.05

        return e

    def formatear_y_renderizar(self, dist, operacion, valores, params=None, nombre_salida="ejercicio_personalizado"):
        """
        Ejecuta la resolución completa, genera el gráfico con Matplotlib y retorna
        la estructura lista para presentación tanto en consola como en interfaz web.
        """
        ej = self.resolver(dist, operacion, valores, params, id_ejercicio=nombre_salida)
        ruta_img = renderizar_grafico(ej, output_dir=OUTPUT_GRAFICOS_DIR)
        b64_img = renderizar_grafico_base64(ej)
        ej["grafico_path"] = ruta_img
        ej["grafico_base64"] = b64_img
        return ej

if __name__ == "__main__":
    rp = ResolverPersonalizado()
    print("Probando resolución personalizada de Normal Z <= 1.45...")
    res = rp.formatear_y_renderizar("Z", "<=", 1.45)
    print("\n--- 1. ORDEN ---")
    print(res["orden"])
    print("\n--- 2. RESOLUCIÓN ---")
    print(res["resolucion"])
    print("\n--- 3. GRÁFICO ---")
    print("Ruta:", res["grafico_path"])
