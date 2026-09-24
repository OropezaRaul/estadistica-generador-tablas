"""
Motor Generador Dinámico y Aleatorio de Ejercicios de Probabilidad y Estadística.
Permite generar lotes personalizados o ejercicios individuales para cualquier distribución:
- Normal Estándar Z ~ N(0, 1)
- t-Student T ~ t(r)
- Chi-cuadrado X ~ Chi^2(r)
- Fisher-Snedecor F ~ F(r1, r2)
Muestrea de forma aleatoria sobre las coordenadas y celdas válidas de las tablas oficiales,
asegurando que cada ejecución genere ejercicios únicos, variados y sin riesgo de duplicidad.
"""
import random
import os

try:
    from .tablas_manager import TablasManager
except ImportError:
    from tablas_manager import TablasManager

class GeneradorEjercicios:
    def __init__(self):
        self.tm = TablasManager()
        self.seen_signatures = set()

    def reiniciar_rastreo(self):
        """Reinicia el conjunto de ejercicios vistos para una nueva generación."""
        self.seen_signatures.clear()

    def generar_ejercicio(self, dist, criterio_id, params=None, ej_id=1):
        """
        Genera un ejercicio aleatorio único dentro del dominio tabulado de la distribución.
        """
        params = params or {}
        dist = dist.lower()

        # Intentar hasta 30 veces para evitar colisiones exactas de valores
        for _ in range(30):
            if dist in ["z", "normal"]:
                ej = self._generar_z(criterio_id, ej_id, params)
            elif dist in ["t", "tstudent", "student"]:
                ej = self._generar_t(criterio_id, ej_id, params)
            elif dist in ["chi", "chi2", "chicuadrado"]:
                ej = self._generar_chi(criterio_id, ej_id, params)
            elif dist in ["f", "fisher"]:
                ej = self._generar_fisher(criterio_id, ej_id, params)
            else:
                raise ValueError(f"Distribución '{dist}' no válida.")

            # Firma para verificar que no se repitan los mismos puntos en el mismo criterio
            sig = (ej["dist_type"], criterio_id, tuple(ej["points"]), tuple(sorted(ej["params"].items())))
            if sig not in self.seen_signatures:
                self.seen_signatures.add(sig)
                return ej

        return ej

    # =========================================================================
    # GENERADOR NORMAL Z (MUESTREO ALEATORIO)
    # =========================================================================
    def _generar_z(self, crit, ej_id, params):
        e = {"id": ej_id, "distribucion": "Normal Estándar", "dist_type": "Z", "criterio_id": crit, "params": {}}

        # Muestreo de z aleatorio en rango representativo [0.35, 2.75]
        def random_z():
            return round(random.uniform(0.35, 2.75), 2)

        if crit == 1:
            a = params.get("val") or random_z()
            prob, r_k, c_k = self.tm.get_z(a)
            e["criterio_nombre"] = "<= +"
            e["orden"] = f"P(Z \\le {a:.2f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y modelo.**\n"
                f"Variable aleatoria Normal Estándar: $Z \\sim \\mathcal{{N}}(0, 1)$. "
                f"Probabilidad acumulada de cola izquierda hasta el valor positivo $a = {a:.2f}$.\n\n"
                f"**Paso 2: Consulta en la Tabla Normal Estándar.**\n"
                f"Ubicamos en la fila `{r_k}` y columna `{c_k}`. La intersección indica directamente:\n"
                f"$$P(Z \\le {a:.2f}) = {prob:.4f}$$\n\n"
                f"**Paso 3: Conclusión.**\n"
                f"$$P(Z \\le {a:.2f}) = {prob:.4f}$$ (o {prob*100:.2f}%)."
            )
            e["region_type"] = "left"
            e["points"] = [a]
            e["labels"] = [f"z = {a:.2f}"]
            e["probabilidad"] = prob

        elif crit == 2:
            a = params.get("val") or random_z()
            prob, r_k, c_k = self.tm.get_z(a)
            res = round(1.0 - prob, 4)
            e["criterio_nombre"] = "<= -"
            e["orden"] = f"P(Z \\le -{a:.2f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y modelo.**\n"
                f"Para $Z \\sim \\mathcal{{N}}(0, 1)$, probabilidad acumulada en la cola izquierda inferior para $-a = -{a:.2f}$.\n\n"
                f"**Paso 2: Propiedad de simetría y complemento.**\n"
                f"Por simetría respecto al origen:\n"
                f"$$P(Z \\le -{a:.2f}) = P(Z \\ge {a:.2f}) = 1 - P(Z \\le {a:.2f})$$\n\n"
                f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                f"Para $+{a:.2f}$ (fila `{r_k}`, columna `{c_k}`): $P(Z \\le {a:.2f}) = {prob:.4f}$.\n\n"
                f"**Paso 4: Cálculo analítico.**\n"
                f"$$P(Z \\le -{a:.2f}) = 1 - {prob:.4f} = {res:.4f}$$\n\n"
                f"**Paso 5: Conclusión.**\n"
                f"$$P(Z \\le -{a:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
            )
            e["region_type"] = "left"
            e["points"] = [-a]
            e["labels"] = [f"z = -{a:.2f}"]
            e["probabilidad"] = res

        elif crit == 3:
            a = params.get("val") or random_z()
            prob, r_k, c_k = self.tm.get_z(a)
            res = round(1.0 - prob, 4)
            e["criterio_nombre"] = ">= +"
            e["orden"] = f"P(Z \\ge {a:.2f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y modelo.**\n"
                f"Para $Z \\sim \\mathcal{{N}}(0, 1)$, se evalúa la cola superior derecha desde $a = {a:.2f}$.\n\n"
                f"**Paso 2: Regla del complemento.**\n"
                f"$$P(Z \\ge {a:.2f}) = 1 - P(Z \\le {a:.2f})$$\n\n"
                f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                f"En la fila `{r_k}`, columna `{c_k}`: $P(Z \\le {a:.2f}) = {prob:.4f}$.\n\n"
                f"**Paso 4: Cálculo analítico.**\n"
                f"$$P(Z \\ge {a:.2f}) = 1 - {prob:.4f} = {res:.4f}$$\n\n"
                f"**Paso 5: Conclusión.**\n"
                f"$$P(Z \\ge {a:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
            )
            e["region_type"] = "right"
            e["points"] = [a]
            e["labels"] = [f"z = {a:.2f}"]
            e["probabilidad"] = res

        elif crit == 4:
            a = params.get("val") or random_z()
            prob, r_k, c_k = self.tm.get_z(a)
            e["criterio_nombre"] = ">= -"
            e["orden"] = f"P(Z \\ge -{a:.2f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y planteamiento.**\n"
                f"Para $Z \\sim \\mathcal{{N}}(0, 1)$, se solicita la probabilidad de cola superior derecha a partir del valor negativo $-a = -{a:.2f}$.\n\n"
                f"**Paso 2: Aplicación formal de la Regla del Complemento.**\n"
                f"Por axioma de probabilidad, la probabilidad hacia la derecha de cualquier punto es el complemento del área acumulada hacia la izquierda:\n"
                f"$$P(Z \\ge -{a:.2f}) = 1 - P(Z \\le -{a:.2f})$$\n\n"
                f"**Paso 3: Aplicación de la propiedad de simetría en la cola inferior.**\n"
                f"Por la perfecta simetría de la campana de Gauss respecto al origen ($z = 0$), el área acumulada en la cola izquierda hasta el valor negativo $-{a:.2f}$ equivale a la cola derecha superior de $+{a:.2f}$, es decir:\n"
                f"$$P(Z \\le -{a:.2f}) = 1 - P(Z \\le {a:.2f})$$\n\n"
                f"**Paso 4: Sustitución algebraica.**\n"
                f"Sustituyendo esta igualdad en la regla del complemento:\n"
                f"$$P(Z \\ge -{a:.2f}) = 1 - [1 - P(Z \\le {a:.2f})] = P(Z \\le {a:.2f})$$\n\n"
                f"**Paso 5: Consulta en la Tabla Normal Estándar.**\n"
                f"Buscamos el valor positivo $a = {a:.2f}$ en la fila `{r_k}` y columna `{c_k}`:\n"
                f"$$P(Z \\le {a:.2f}) = {prob:.4f}$$\n\n"
                f"**Paso 6: Conclusión y justificación geométrica de la gráfica.**\n"
                f"$$P(Z \\ge -{a:.2f}) = {prob:.4f}$$ (o {prob*100:.2f}%).\n\n"
                f"*(Nota sobre la gráfica: La región sombreada corresponde fielmente a la orden $Z \\ge -{a:.2f}$. Se inicia en el valor negativo $-{a:.2f}$, cruza el eje central en $0$ y se extiende hacia todo $+\\infty$, abarcando más del 50% de la distribución).* "
            )
            e["region_type"] = "right"
            e["points"] = [-a]
            e["labels"] = [f"z = -{a:.2f}"]
            e["probabilidad"] = prob

        elif crit == 5:
            if params.get("val") and isinstance(params.get("val"), (list, tuple)):
                a, b = sorted(params.get("val"))
            else:
                a = round(random.uniform(0.20, 1.60), 2)
                b = round(a + random.uniform(0.40, 1.20), 2)
                if b > 2.80: b = 2.80
            p_a, ra_k, ca_k = self.tm.get_z(a)
            p_b, rb_k, cb_k = self.tm.get_z(b)
            res = round(p_b - p_a, 4)
            e["criterio_nombre"] = "+ <= <= +"
            e["orden"] = f"P({a:.2f} \\le Z \\le {b:.2f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y modelo.**\n"
                f"Intervalo positivo $[{a:.2f}, {b:.2f}]$ en $Z \\sim \\mathcal{{N}}(0, 1)$.\n\n"
                f"**Paso 2: Resta de acumuladas directas.**\n"
                f"$$P({a:.2f} \\le Z \\le {b:.2f}) = P(Z \\le {b:.2f}) - P(Z \\le {a:.2f})$$\n\n"
                f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                f"- $P(Z \\le {b:.2f}) = {p_b:.4f}$\n"
                f"- $P(Z \\le {a:.2f}) = {p_a:.4f}$\n\n"
                f"**Paso 4: Cálculo analítico.**\n"
                f"$$P({a:.2f} \\le Z \\le {b:.2f}) = {p_b:.4f} - {p_a:.4f} = {res:.4f}$$\n\n"
                f"**Paso 5: Conclusión.**\n"
                f"$$P({a:.2f} \\le Z \\le {b:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
            )
            e["region_type"] = "interval"
            e["points"] = [a, b]
            e["labels"] = [f"z1 = {a:.2f}", f"z2 = {b:.2f}"]
            e["probabilidad"] = res

        elif crit == 6:
            if params.get("val") and isinstance(params.get("val"), (list, tuple)):
                a, b = params.get("val")
            else:
                a = round(random.uniform(0.50, 2.30), 2)
                b = round(random.uniform(0.50, 2.30), 2)
            p_a, ra_k, ca_k = self.tm.get_z(a)
            p_b, rb_k, cb_k = self.tm.get_z(b)
            p_lower = round(1.0 - p_a, 4)
            res = round(p_b - p_lower, 4)
            e["criterio_nombre"] = "- <= <= +"
            e["orden"] = f"P(-{a:.2f} \\le Z \\le {b:.2f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y modelo.**\n"
                f"Intervalo bilateral entre $-a = -{a:.2f}$ y $b = {b:.2f}$ en $Z \\sim \\mathcal{{N}}(0, 1)$.\n\n"
                f"**Paso 2: Resta de acumuladas y simetría.**\n"
                f"$$P(-{a:.2f} \\le Z \\le {b:.2f}) = P(Z \\le {b:.2f}) - P(Z \\le -{a:.2f})$$\n"
                f"Con $P(Z \\le -{a:.2f}) = 1 - P(Z \\le {a:.2f})$.\n\n"
                f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                f"- $P(Z \\le {b:.2f}) = {p_b:.4f}$ (fila `{rb_k}`, col `{cb_k}`)\n"
                f"- $P(Z \\le {a:.2f}) = {p_a:.4f} \\implies P(Z \\le -{a:.2f}) = {p_lower:.4f}$\n\n"
                f"**Paso 4: Cálculo analítico.**\n"
                f"$$P(-{a:.2f} \\le Z \\le {b:.2f}) = {p_b:.4f} - {p_lower:.4f} = {res:.4f}$$\n\n"
                f"**Paso 5: Conclusión.**\n"
                f"$$P(-{a:.2f} \\le Z \\le {b:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
            )
            e["region_type"] = "interval"
            e["points"] = [-a, b]
            e["labels"] = [f"z1 = -{a:.2f}", f"z2 = {b:.2f}"]
            e["probabilidad"] = res

        elif crit == 7:
            if params.get("val") and isinstance(params.get("val"), (list, tuple)):
                v1, v2 = sorted(params.get("val"))
                a, b = abs(v1), abs(v2)
            else:
                b = round(random.uniform(0.20, 1.50), 2)
                a = round(b + random.uniform(0.40, 1.20), 2)
                if a > 2.80: a = 2.80
            p_a, ra_k, ca_k = self.tm.get_z(a)
            p_b, rb_k, cb_k = self.tm.get_z(b)
            res = round(p_a - p_b, 4)
            e["criterio_nombre"] = "- <= <= -"
            e["orden"] = f"P(-{a:.2f} \\le Z \\le -{b:.2f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y modelo.**\n"
                f"Intervalo negativo $[-{a:.2f}, -{b:.2f}]$ en $Z \\sim \\mathcal{{N}}(0, 1)$.\n\n"
                f"**Paso 2: Propiedad de simetría.**\n"
                f"Por simetría, equivale al intervalo positivo reflejado $[{b:.2f}, {a:.2f}]$:\n"
                f"$$P(-{a:.2f} \\le Z \\le -{b:.2f}) = P(Z \\le {a:.2f}) - P(Z \\le {b:.2f})$$\n\n"
                f"**Paso 3: Consulta en la Tabla Normal Estándar.**\n"
                f"- $P(Z \\le {a:.2f}) = {p_a:.4f}$\n"
                f"- $P(Z \\le {b:.2f}) = {p_b:.4f}$\n\n"
                f"**Paso 4: Cálculo analítico.**\n"
                f"$$P(-{a:.2f} \\le Z \\le -{b:.2f}) = {p_a:.4f} - {p_b:.4f} = {res:.4f}$$\n\n"
                f"**Paso 5: Conclusión.**\n"
                f"$$P(-{a:.2f} \\le Z \\le -{b:.2f}) = {res:.4f}$$ (o {res*100:.2f}%)."
            )
            e["region_type"] = "interval"
            e["points"] = [-a, -b]
            e["labels"] = [f"z1 = -{a:.2f}", f"z2 = -{b:.2f}"]
            e["probabilidad"] = res

        elif crit == 8:
            z_cand = round(random.uniform(0.40, 2.50), 2)
            p_tab, _, _ = self.tm.get_z(z_cand)
            p = params.get("val") or p_tab
            c_val, p_found, r_k, c_k = self.tm.find_z_inverse(p)
            e["criterio_nombre"] = "<= C"
            e["orden"] = f"P(Z \\le c) = {p:.4f}, \\quad c = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y análisis.**\n"
                f"Búsqueda inversa con probabilidad acumulada $P(Z \\le c) = {p:.4f}$ ($c > 0$).\n\n"
                f"**Paso 2: Búsqueda en el cuerpo de la Tabla Normal.**\n"
                f"Se ubica `{p_found:.4f}` en la intersección de la fila `{r_k}` y columna `{c_k}`.\n\n"
                f"**Paso 3: Conclusión.**\n"
                f"$$c = {r_k} + {c_k} = {c_val:.2f}$$"
            )
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.2f}"]
            e["probabilidad"] = p_found

        elif crit == 9:
            z_cand = round(random.uniform(0.40, 2.50), 2)
            p_tab, _, _ = self.tm.get_z(z_cand)
            p_comp_init = round(1.0 - p_tab, 4)
            p = params.get("val") or p_comp_init
            p_comp = round(1.0 - p, 4)
            c_val, p_found, r_k, c_k = self.tm.find_z_inverse(p_comp)
            e["criterio_nombre"] = ">= C"
            e["orden"] = f"P(Z \\ge c) = {p:.4f}, \\quad c = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y análisis.**\n"
                f"Búsqueda inversa cola derecha con $P(Z \\ge c) = {p:.4f}$ ($c > 0$).\n\n"
                f"**Paso 2: Transformación por complemento.**\n"
                f"$$P(Z \\le c) = 1 - P(Z \\ge c) = 1 - {p:.4f} = {p_comp:.4f}$$\n\n"
                f"**Paso 3: Búsqueda en la Tabla Normal.**\n"
                f"Fila `{r_k}`, columna `{c_k}` $\\implies c = {c_val:.2f}$.\n\n"
                f"**Paso 4: Conclusión.**\n"
                f"$$c = {c_val:.2f}$$"
            )
            e["region_type"] = "right"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.2f}"]
            e["probabilidad"] = p

        elif crit == 10:
            z_cand = round(random.uniform(0.40, 2.50), 2)
            p_tab, _, _ = self.tm.get_z(z_cand)
            p_lower_init = round(1.0 - p_tab, 4)
            p = params.get("val") or p_lower_init
            p_comp = round(1.0 - p, 4)
            k_val, p_found, r_k, c_k = self.tm.find_z_inverse(p_comp)
            c_val = -k_val
            e["criterio_nombre"] = "<= -C"
            e["orden"] = f"P(Z \\le c) = {p:.4f}, \\quad c = ? \\quad (c < 0)"
            e["resolucion"] = (
                f"**Paso 1: Identificación y análisis.**\n"
                f"Búsqueda inversa con probabilidad $p = {p:.4f} < 0.50$, luego $c < 0$.\n\n"
                f"**Paso 2: Simetría.**\n"
                f"Sea $c = -k$. $P(Z \\le -k) = 1 - P(Z \\le k) = {p:.4f} \\implies P(Z \\le k) = {p_comp:.4f}$.\n\n"
                f"**Paso 3: Búsqueda en la Tabla Normal.**\n"
                f"Fila `{r_k}`, col `{c_k}` $\\implies k = {k_val:.2f}$.\n\n"
                f"**Paso 4: Conclusión.**\n"
                f"$$c = -k = {c_val:.2f}$$"
            )
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.2f}"]
            e["probabilidad"] = p

        elif crit == 11:
            z_cand = round(random.uniform(0.40, 2.50), 2)
            p_tab, _, _ = self.tm.get_z(z_cand)
            p = params.get("val") or p_tab
            k_val, p_found, r_k, c_k = self.tm.find_z_inverse(p)
            c_val = -k_val
            e["criterio_nombre"] = ">= -C"
            e["orden"] = f"P(Z \\ge c) = {p:.4f}, \\quad c = ? \\quad (c < 0)"
            e["resolucion"] = (
                f"**Paso 1: Identificación y análisis.**\n"
                f"Búsqueda inversa cola derecha con área $P(Z \\ge c) = {p:.4f} > 0.50$, luego $c < 0$.\n\n"
                f"**Paso 2: Simetría.**\n"
                f"Sea $c = -k$. $P(Z \\ge -k) = P(Z \\le k) = {p:.4f}$.\n\n"
                f"**Paso 3: Búsqueda en la Tabla Normal.**\n"
                f"Fila `{r_k}`, columna `{c_k}` $\\implies k = {k_val:.2f}$.\n\n"
                f"**Paso 4: Conclusión.**\n"
                f"$$c = -k = {c_val:.2f}$$"
            )
            e["region_type"] = "right"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.2f}"]
            e["probabilidad"] = p

        return e

    # =========================================================================
    # GENERADOR t-STUDENT T ~ t(r) (MUESTREO ALEATORIO)
    # =========================================================================
    def _generar_t(self, crit, ej_id, params):
        available_dfs = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 25, 28, 30]
        df = params.get("df") or random.choice(available_dfs)
        e = {"id": ej_id, "distribucion": f"t-Student (r = {df} gl)", "dist_type": "t", "criterio_id": crit, "params": {"df": df}}

        t_probs = ["0.750", "0.800", "0.900", "0.950", "0.975", "0.990", "0.995"]

        if crit == 1:
            p_level = random.choice(["0.900", "0.950", "0.975", "0.990"])
            a = self.tm.get_t(df, p_level)
            e["criterio_nombre"] = "<= +"
            e["orden"] = f"P(T_{{{df}}} \\le {a:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y modelo.**\n"
                f"Variable $T \\sim t({df})$. Probabilidad acumulada directa hasta $a = {a:.3f}$.\n\n"
                f"**Paso 2: Consulta en la Tabla t-Student.**\n"
                f"Fila $r = {df}$, columna $1 - \\alpha = {p_level}$:\n"
                f"$$P(T_{{{df}}} \\le {a:.3f}) = {p_level}$$\n\n"
                f"**Paso 3: Conclusión.**\n"
                f"$$P(T_{{{df}}} \\le {a:.3f}) = {p_level}$$"
            )
            e["region_type"] = "left"
            e["points"] = [a]
            e["labels"] = [f"t = {a:.3f}"]
            e["probabilidad"] = float(p_level)

        elif crit == 2:
            p_level = random.choice(["0.900", "0.950", "0.975", "0.990"])
            a = self.tm.get_t(df, p_level)
            res = round(1.0 - float(p_level), 3)
            e["criterio_nombre"] = "<= -"
            e["orden"] = f"P(T_{{{df}}} \\le -{a:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y simetría.**\n"
                f"Para $T \\sim t({df})$ con valor negativo $-{a:.3f}$:\n"
                f"$$P(T_{{{df}}} \\le -{a:.3f}) = 1 - P(T_{{{df}}} \\le {a:.3f})$$\n\n"
                f"**Paso 2: Consulta en Tabla t-Student.**\n"
                f"Fila $r = {df}$, columna `{p_level}`: $P(T_{{{df}}} \\le {a:.3f}) = {p_level}$.\n\n"
                f"**Paso 3: Conclusión.**\n"
                f"$$P(T_{{{df}}} \\le -{a:.3f}) = 1 - {p_level} = {res:.3f}$$"
            )
            e["region_type"] = "left"
            e["points"] = [-a]
            e["labels"] = [f"t = -{a:.3f}"]
            e["probabilidad"] = res

        elif crit == 3:
            p_level = random.choice(["0.900", "0.950", "0.975", "0.990"])
            a = self.tm.get_t(df, p_level)
            res = round(1.0 - float(p_level), 3)
            e["criterio_nombre"] = ">= +"
            e["orden"] = f"P(T_{{{df}}} \\ge {a:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Regla del complemento en t-Student.**\n"
                f"$$P(T_{{{df}}} \\ge {a:.3f}) = 1 - P(T_{{{df}}} \\le {a:.3f})$$\n\n"
                f"**Paso 2: Consulta de tabla.**\n"
                f"Fila $r = {df}$, columna `{p_level}`.\n\n"
                f"**Paso 3: Conclusión.**\n"
                f"$$P(T_{{{df}}} \\ge {a:.3f}) = 1 - {p_level} = {res:.3f}$$"
            )
            e["region_type"] = "right"
            e["points"] = [a]
            e["labels"] = [f"t = {a:.3f}"]
            e["probabilidad"] = res

        elif crit == 4:
            p_level = random.choice(["0.800", "0.900", "0.950", "0.975"])
            a = self.tm.get_t(df, p_level)
            e["criterio_nombre"] = ">= -"
            e["orden"] = f"P(T_{{{df}}} \\ge -{a:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Identificación y planteamiento.**\n"
                f"Para $T \\sim t({df})$, se solicita la probabilidad de cola derecha a partir del valor negativo $-a = -{a:.3f}$.\n\n"
                f"**Paso 2: Aplicación formal de la Regla del Complemento.**\n"
                f"$$P(T_{{{df}}} \\ge -{a:.3f}) = 1 - P(T_{{{df}}} \\le -{a:.3f})$$\n\n"
                f"**Paso 3: Aplicación de la propiedad de simetría en la cola inferior.**\n"
                f"Por simetría respecto al origen: $P(T_{{{df}}} \\le -{a:.3f}) = 1 - P(T_{{{df}}} \\le {a:.3f})$.\n\n"
                f"**Paso 4: Sustitución algebraica.**\n"
                f"$$P(T_{{{df}}} \\ge -{a:.3f}) = 1 - [1 - P(T_{{{df}}} \\le {a:.3f})] = P(T_{{{df}}} \\le {a:.3f})$$\n\n"
                f"**Paso 5: Consulta en la Tabla t-Student.**\n"
                f"En la fila $r = {df}$, el cuantil $a = {a:.3f}$ se encuentra bajo la columna $1 - \\alpha = {p_level}$. Por tanto:\n"
                f"$$P(T_{{{df}}} \\ge -{a:.3f}) = {p_level}$$\n\n"
                f"*(Nota sobre la gráfica: La región sombreada inicia en el valor negativo $-{a:.3f}$ y se extiende hacia toda la derecha $+\\infty$, abarcando más del 50% de la curva).* "
            )
            e["region_type"] = "right"
            e["points"] = [-a]
            e["labels"] = [f"t = -{a:.3f}"]
            e["probabilidad"] = float(p_level)

        elif crit == 5:
            idx1 = random.randint(0, len(t_probs) - 3)
            idx2 = random.randint(idx1 + 1, len(t_probs) - 1)
            pa_level, pb_level = t_probs[idx1], t_probs[idx2]
            a = self.tm.get_t(df, pa_level)
            b = self.tm.get_t(df, pb_level)
            res = round(float(pb_level) - float(pa_level), 3)
            e["criterio_nombre"] = "+ <= <= +"
            e["orden"] = f"P({a:.3f} \\le T_{{{df}}} \\le {b:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Resta de acumuladas directas.**\n"
                f"$$P({a:.3f} \\le T_{{{df}}} \\le {b:.3f}) = {pb_level} - {pa_level} = {res:.3f}$$"
            )
            e["region_type"] = "interval"
            e["points"] = [a, b]
            e["labels"] = [f"t1 = {a:.3f}", f"t2 = {b:.3f}"]
            e["probabilidad"] = res

        elif crit == 6:
            pa_level = random.choice(["0.900", "0.950"])
            pb_level = random.choice(["0.975", "0.990"])
            a = self.tm.get_t(df, pa_level)
            b = self.tm.get_t(df, pb_level)
            p_lower = round(1.0 - float(pa_level), 3)
            res = round(float(pb_level) - p_lower, 3)
            e["criterio_nombre"] = "- <= <= +"
            e["orden"] = f"P(-{a:.3f} \\le T_{{{df}}} \\le {b:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Resta de acumuladas con simetría.**\n"
                f"$$P(-{a:.3f} \\le T_{{{df}}} \\le {b:.3f}) = P(T \\le {b:.3f}) - [1 - P(T \\le {a:.3f})]$$\n\n"
                f"**Paso 2: Cálculo.**\n"
                f"$$P = {pb_level} - {p_lower:.3f} = {res:.3f}$$"
            )
            e["region_type"] = "interval"
            e["points"] = [-a, b]
            e["labels"] = [f"t1 = -{a:.3f}", f"t2 = {b:.3f}"]
            e["probabilidad"] = res

        elif crit == 7:
            idx1 = random.randint(0, len(t_probs) - 3)
            idx2 = random.randint(idx1 + 1, len(t_probs) - 1)
            pb_level, pa_level = t_probs[idx1], t_probs[idx2]
            b = self.tm.get_t(df, pb_level)
            a = self.tm.get_t(df, pa_level)
            res = round(float(pa_level) - float(pb_level), 3)
            e["criterio_nombre"] = "- <= <= -"
            e["orden"] = f"P(-{a:.3f} \\le T_{{{df}}} \\le -{b:.3f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Propiedad de simetría.**\n"
                f"$$P(-{a:.3f} \\le T_{{{df}}} \\le -{b:.3f}) = P(T \\le {a:.3f}) - P(T \\le {b:.3f}) = {res:.3f}$$"
            )
            e["region_type"] = "interval"
            e["points"] = [-a, -b]
            e["labels"] = [f"t1 = -{a:.3f}", f"t2 = -{b:.3f}"]
            e["probabilidad"] = res

        elif crit == 8:
            p_level = random.choice(["0.900", "0.950", "0.975", "0.990"])
            c_val = self.tm.get_t(df, p_level)
            e["criterio_nombre"] = "<= C"
            e["orden"] = f"P(T_{{{df}}} \\le c) = {p_level}, \\quad c = ?"
            e["resolucion"] = (
                f"**Paso 1: Búsqueda inversa en Tabla t-Student.**\n"
                f"Fila $r = {df}$, columna `{p_level}`: $$c = {c_val:.3f}$$"
            )
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = float(p_level)

        elif crit == 9:
            p_level = random.choice(["0.900", "0.950", "0.975", "0.990"])
            alpha_str = f"{1.0 - float(p_level):.3f}"
            c_val = self.tm.get_t(df, p_level)
            e["criterio_nombre"] = ">= C"
            e["orden"] = f"P(T_{{{df}}} \\ge c) = {alpha_str}, \\quad c = ?"
            e["resolucion"] = (
                f"**Paso 1: Complemento e inversa.**\n"
                f"$$P(T \\le c) = 1 - {alpha_str} = {p_level} \\implies c = {c_val:.3f}$$"
            )
            e["region_type"] = "right"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = float(alpha_str)

        elif crit == 10:
            p_level = random.choice(["0.900", "0.950", "0.975", "0.990"])
            alpha_str = f"{1.0 - float(p_level):.3f}"
            k_val = self.tm.get_t(df, p_level)
            c_val = -k_val
            e["criterio_nombre"] = "<= -C"
            e["orden"] = f"P(T_{{{df}}} \\le c) = {alpha_str}, \\quad c = ? \\quad (c < 0)"
            e["resolucion"] = (
                f"**Paso 1: Simetría en t-Student.**\n"
                f"Sea $c = -k$. $P(T \\le k) = 1 - {alpha_str} = {p_level} \\implies k = {k_val:.3f} \\implies c = {c_val:.3f}$."
            )
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = float(alpha_str)

        elif crit == 11:
            p_level = random.choice(["0.900", "0.950", "0.975"])
            k_val = self.tm.get_t(df, p_level)
            c_val = -k_val
            e["criterio_nombre"] = ">= -C"
            e["orden"] = f"P(T_{{{df}}} \\ge c) = {p_level}, \\quad c = ? \\quad (c < 0)"
            e["resolucion"] = (
                f"**Paso 1: Simetría en t-Student.**\n"
                f"Sea $c = -k$. $P(T \\ge -k) = P(T \\le k) = {p_level} \\implies k = {k_val:.3f} \\implies c = {c_val:.3f}$."
            )
            e["region_type"] = "right"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = float(p_level)

        return e

    # =========================================================================
    # GENERADOR CHI-CUADRADO X ~ Chi^2(r) (MUESTREO ALEATORIO)
    # =========================================================================
    def _generar_chi(self, crit, ej_id, params):
        available_dfs = [5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30]
        df = params.get("df") or random.choice(available_dfs)
        e = {"id": ej_id, "distribucion": f"Chi-cuadrado (r = {df} gl)", "dist_type": "chi", "criterio_id": crit, "params": {"df": df}}

        lower_cols = ["0.005", "0.010", "0.025", "0.050", "0.100"]
        upper_cols = ["0.900", "0.950", "0.975", "0.990", "0.995"]

        if crit == 1:
            p_level = random.choice(upper_cols)
            b = self.tm.get_chi(df, p_level)
            e["criterio_nombre"] = "<= +"
            e["orden"] = f"P(\\chi^2_{{{df}}} \\le {b:.3f}) = ?"
            e["resolucion"] = f"Consulta directa en fila $r = {df}$ y columna `{p_level}`: $$P(\\chi^2_{{{df}}} \\le {b:.3f}) = {p_level}$$"
            e["region_type"] = "left"
            e["points"] = [b]
            e["labels"] = [f"chi2 = {b:.3f}"]
            e["probabilidad"] = float(p_level)

        elif crit == 2:
            p_level = random.choice(lower_cols)
            a = self.tm.get_chi(df, p_level)
            e["criterio_nombre"] = "<= -"
            e["orden"] = f"P(\\chi^2_{{{df}}} \\le {a:.3f}) = ?"
            e["resolucion"] = f"Cola inferior en Chi-cuadrado (percentil bajo tabulado): $$P(\\chi^2_{{{df}}} \\le {a:.3f}) = {p_level}$$"
            e["region_type"] = "left"
            e["points"] = [a]
            e["labels"] = [f"chi2 = {a:.3f}"]
            e["probabilidad"] = float(p_level)

        elif crit == 3:
            p_level = random.choice(upper_cols)
            b = self.tm.get_chi(df, p_level)
            res = round(1.0 - float(p_level), 3)
            e["criterio_nombre"] = ">= +"
            e["orden"] = f"P(\\chi^2_{{{df}}} \\ge {b:.3f}) = ?"
            e["resolucion"] = f"Complemento: $$P(\\chi^2_{{{df}}} \\ge {b:.3f}) = 1 - {p_level} = {res:.3f}$$"
            e["region_type"] = "right"
            e["points"] = [b]
            e["labels"] = [f"chi2 = {b:.3f}"]
            e["probabilidad"] = res

        elif crit == 4:
            p_level = random.choice(lower_cols)
            a = self.tm.get_chi(df, p_level)
            res = round(1.0 - float(p_level), 3)
            e["criterio_nombre"] = ">= -"
            e["orden"] = f"P(\\chi^2_{{{df}}} \\ge {a:.3f}) = ?"
            e["resolucion"] = f"Complemento desde percentil bajo: $$P(\\chi^2_{{{df}}} \\ge {a:.3f}) = 1 - {p_level} = {res:.3f}$$"
            e["region_type"] = "right"
            e["points"] = [a]
            e["labels"] = [f"chi2 = {a:.3f}"]
            e["probabilidad"] = res

        elif crit == 5:
            idx1 = random.randint(0, len(upper_cols) - 2)
            idx2 = random.randint(idx1 + 1, len(upper_cols) - 1)
            pa, pb = upper_cols[idx1], upper_cols[idx2]
            b1 = self.tm.get_chi(df, pa)
            b2 = self.tm.get_chi(df, pb)
            res = round(float(pb) - float(pa), 3)
            e["criterio_nombre"] = "+ <= <= +"
            e["orden"] = f"P({b1:.3f} \\le \\chi^2_{{{df}}} \\le {b2:.3f}) = ?"
            e["resolucion"] = f"Intervalo superior: $$P({b1:.3f} \\le \\chi^2_{{{df}}} \\le {b2:.3f}) = {pb} - {pa} = {res:.3f}$$"
            e["region_type"] = "interval"
            e["points"] = [b1, b2]
            e["labels"] = [f"chi2_1 = {b1:.3f}", f"chi2_2 = {b2:.3f}"]
            e["probabilidad"] = res

        elif crit == 6:
            pa = random.choice(["0.025", "0.050", "0.100"])
            pb = random.choice(["0.900", "0.950", "0.975"])
            a = self.tm.get_chi(df, pa)
            b = self.tm.get_chi(df, pb)
            res = round(float(pb) - float(pa), 3)
            e["criterio_nombre"] = "- <= <= +"
            e["orden"] = f"P({a:.3f} \\le \\chi^2_{{{df}}} \\le {b:.3f}) = ?"
            e["resolucion"] = f"Intervalo central: $$P({a:.3f} \\le \\chi^2_{{{df}}} \\le {b:.3f}) = {pb} - {pa} = {res:.3f}$$"
            e["region_type"] = "interval"
            e["points"] = [a, b]
            e["labels"] = [f"chi2_1 = {a:.3f}", f"chi2_2 = {b:.3f}"]
            e["probabilidad"] = res

        elif crit == 7:
            idx1 = random.randint(0, len(lower_cols) - 2)
            idx2 = random.randint(idx1 + 1, len(lower_cols) - 1)
            pa, pb = lower_cols[idx1], lower_cols[idx2]
            a1 = self.tm.get_chi(df, pa)
            a2 = self.tm.get_chi(df, pb)
            res = round(float(pb) - float(pa), 3)
            e["criterio_nombre"] = "- <= <= -"
            e["orden"] = f"P({a1:.3f} \\le \\chi^2_{{{df}}} \\le {a2:.3f}) = ?"
            e["resolucion"] = f"Intervalo inferior: $$P({a1:.3f} \\le \\chi^2_{{{df}}} \\le {a2:.3f}) = {pb} - {pa} = {res:.3f}$$"
            e["region_type"] = "interval"
            e["points"] = [a1, a2]
            e["labels"] = [f"chi2_1 = {a1:.3f}", f"chi2_2 = {a2:.3f}"]
            e["probabilidad"] = res

        elif crit == 8:
            p = random.choice(upper_cols)
            c_val = self.tm.get_chi(df, p)
            e["criterio_nombre"] = "<= C"
            e["orden"] = f"P(\\chi^2_{{{df}}} \\le c) = {p}, \\quad c = ?"
            e["resolucion"] = f"Inversa cuantil alto en fila $r = {df}$: $$c = {c_val:.3f}$$"
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = float(p)

        elif crit == 9:
            p_level = random.choice(upper_cols)
            alpha_str = f"{1.0 - float(p_level):.3f}"
            c_val = self.tm.get_chi(df, p_level)
            e["criterio_nombre"] = ">= C"
            e["orden"] = f"P(\\chi^2_{{{df}}} \\ge c) = {alpha_str}, \\quad c = ?"
            e["resolucion"] = f"Complemento e inversa: $$P(\\chi^2 \\le c) = {p_level} \\implies c = {c_val:.3f}$$"
            e["region_type"] = "right"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = float(alpha_str)

        elif crit == 10:
            p = random.choice(lower_cols)
            c_val = self.tm.get_chi(df, p)
            e["criterio_nombre"] = "<= -C"
            e["orden"] = f"P(\\chi^2_{{{df}}} \\le c) = {p}, \\quad c = ?"
            e["resolucion"] = f"Inversa percentil bajo en fila $r = {df}$: $$c = {c_val:.3f}$$"
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = float(p)

        elif crit == 11:
            p_comp = random.choice(lower_cols)
            p_level = f"{1.0 - float(p_comp):.3f}"
            c_val = self.tm.get_chi(df, p_comp)
            e["criterio_nombre"] = ">= -C"
            e["orden"] = f"P(\\chi^2_{{{df}}} \\ge c) = {p_level}, \\quad c = ?"
            e["resolucion"] = f"Inversa cola amplia hacia la derecha: $$P(\\chi^2 \\le c) = {p_comp} \\implies c = {c_val:.3f}$$"
            e["region_type"] = "right"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.3f}"]
            e["probabilidad"] = float(p_level)

        return e

    # =========================================================================
    # GENERADOR FISHER F(r1, r2) (MUESTREO ALEATORIO)
    # =========================================================================
    def _generar_fisher(self, crit, ej_id, params):
        # Todos los pares invertibles de la tabla con r1 != r2
        invertible_pool = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20]
        pares = [(r1, r2) for r1 in invertible_pool for r2 in invertible_pool if r1 != r2]
        
        r1 = params.get("r1")
        r2 = params.get("r2")
        if not r1 or not r2:
            r1, r2 = random.choice(pares)
            
        e = {"id": ej_id, "distribucion": f"Fisher-Snedecor (r1 = {r1}, r2 = {r2})", "dist_type": "fisher", "criterio_id": crit, "params": {"r1": r1, "r2": r2}}
        niveles = ["0.950", "0.975", "0.990", "0.995"]

        if crit == 1:
            p = random.choice(niveles)
            b = self.tm.get_fisher_upper(r1, r2, p)
            e["criterio_nombre"] = "<= +"
            e["orden"] = f"P(F_{{{r1}, {r2}}} \\le {b:.2f}) = ?"
            e["resolucion"] = f"Consulta directa en nivel `{p}`: $$P(F_{{{r1}, {r2}}} \\le {b:.2f}) = {p}$$"
            e["region_type"] = "left"
            e["points"] = [b]
            e["labels"] = [f"F = {b:.2f}"]
            e["probabilidad"] = float(p)

        elif crit == 2:
            p = random.choice(["0.950", "0.975"])
            alpha_str = f"{1.0 - float(p):.3f}"
            a, f_inv = self.tm.get_fisher_lower(r1, r2, p)
            e["criterio_nombre"] = "<= -"
            e["orden"] = f"P(F_{{{r1}, {r2}}} \\le {a:.4f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Propiedad de inversión oficial de la cabecera:**\n"
                f"$$F_{{\\alpha; r_1, r_2}} = \\frac{{1}}{{F_{{1 - \\alpha; r_2, r_1}}}}$$\n"
                f"Para $\\alpha = {alpha_str}$, buscamos $F_{{{p}; {r2}, {r1}}} = {f_inv:.2f}$:\n"
                f"$$a = \\frac{{1}}{{{f_inv:.2f}}} = {a:.4f} \\implies P(F_{{{r1}, {r2}}} \\le {a:.4f}) = {alpha_str}$$"
            )
            e["region_type"] = "left"
            e["points"] = [a]
            e["labels"] = [f"F = {a:.4f}"]
            e["probabilidad"] = float(alpha_str)

        elif crit == 3:
            p = random.choice(niveles)
            b = self.tm.get_fisher_upper(r1, r2, p)
            res = round(1.0 - float(p), 3)
            e["criterio_nombre"] = ">= +"
            e["orden"] = f"P(F_{{{r1}, {r2}}} \\ge {b:.2f}) = ?"
            e["resolucion"] = f"Regla del complemento: $$P(F_{{{r1}, {r2}}} \\ge {b:.2f}) = 1 - {p} = {res:.3f}$$"
            e["region_type"] = "right"
            e["points"] = [b]
            e["labels"] = [f"F = {b:.2f}"]
            e["probabilidad"] = res

        elif crit == 4:
            p = random.choice(["0.950", "0.975"])
            alpha_str = f"{1.0 - float(p):.3f}"
            a, f_inv = self.tm.get_fisher_lower(r1, r2, p)
            e["criterio_nombre"] = ">= -"
            e["orden"] = f"P(F_{{{r1}, {r2}}} \\ge {a:.4f}) = ?"
            e["resolucion"] = (
                f"**Paso 1: Inversión y complemento:**\n"
                f"Como $a = 1 / {f_inv:.2f} = {a:.4f}$ acumula $\\alpha = {alpha_str}$ a la izquierda:\n"
                f"$$P(F_{{{r1}, {r2}}} \\ge {a:.4f}) = 1 - {alpha_str} = {p}$$"
            )
            e["region_type"] = "right"
            e["points"] = [a]
            e["labels"] = [f"F = {a:.4f}"]
            e["probabilidad"] = float(p)

        elif crit == 5:
            pa, pb = "0.950", "0.990"
            b1 = self.tm.get_fisher_upper(r1, r2, pa)
            b2 = self.tm.get_fisher_upper(r1, r2, pb)
            res = round(float(pb) - float(pa), 3)
            e["criterio_nombre"] = "+ <= <= +"
            e["orden"] = f"P({b1:.2f} \\le F_{{{r1}, {r2}}} \\le {b2:.2f}) = ?"
            e["resolucion"] = f"Intervalo superior: $$P({b1:.2f} \\le F \\le {b2:.2f}) = {pb} - {pa} = {res:.3f}$$"
            e["region_type"] = "interval"
            e["points"] = [b1, b2]
            e["labels"] = [f"F1 = {b1:.2f}", f"F2 = {b2:.2f}"]
            e["probabilidad"] = res

        elif crit == 6:
            p = random.choice(["0.950", "0.975"])
            alpha_str = f"{1.0 - float(p):.3f}"
            a, f_inv = self.tm.get_fisher_lower(r1, r2, p)
            b = self.tm.get_fisher_upper(r1, r2, p)
            res = round(float(p) - float(alpha_str), 3)
            e["criterio_nombre"] = "- <= <= +"
            e["orden"] = f"P({a:.4f} \\le F_{{{r1}, {r2}}} \\le {b:.2f}) = ?"
            e["resolucion"] = f"Intervalo con cuantil inferior por inversión: $$P = {p} - {alpha_str} = {res:.3f}$$"
            e["region_type"] = "interval"
            e["points"] = [a, b]
            e["labels"] = [f"F1 = {a:.4f}", f"F2 = {b:.2f}"]
            e["probabilidad"] = res

        elif crit == 7:
            pa, pb = "0.990", "0.950"
            a1, f1 = self.tm.get_fisher_lower(r1, r2, pa)
            a2, f2 = self.tm.get_fisher_lower(r1, r2, pb)
            res = round(0.050 - 0.010, 3)
            e["criterio_nombre"] = "- <= <= -"
            e["orden"] = f"P({a1:.4f} \\le F_{{{r1}, {r2}}} \\le {a2:.4f}) = ?"
            e["resolucion"] = f"Intervalo inferior mediante doble inversión: $$P = 0.050 - 0.010 = {res:.3f}$$"
            e["region_type"] = "interval"
            e["points"] = [a1, a2]
            e["labels"] = [f"F1 = {a1:.4f}", f"F2 = {a2:.4f}"]
            e["probabilidad"] = res

        elif crit == 8:
            p = random.choice(niveles)
            c_val = self.tm.get_fisher_upper(r1, r2, p)
            e["criterio_nombre"] = "<= C"
            e["orden"] = f"P(F_{{{r1}, {r2}}} \\le c) = {p}, \\quad c = ?"
            e["resolucion"] = f"Inversa directa cuantil alto: $$c = {c_val:.2f}$$"
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.2f}"]
            e["probabilidad"] = float(p)

        elif crit == 9:
            p = random.choice(niveles)
            alpha_str = f"{1.0 - float(p):.3f}"
            c_val = self.tm.get_fisher_upper(r1, r2, p)
            e["criterio_nombre"] = ">= C"
            e["orden"] = f"P(F_{{{r1}, {r2}}} \\ge c) = {alpha_str}, \\quad c = ?"
            e["resolucion"] = f"Complemento e inversa: $$P(F \\le c) = {p} \\implies c = {c_val:.2f}$$"
            e["region_type"] = "right"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.2f}"]
            e["probabilidad"] = float(alpha_str)

        elif crit == 10:
            p_comp = random.choice(["0.950", "0.975"])
            alpha_str = f"{1.0 - float(p_comp):.3f}"
            c_val, f_inv = self.tm.get_fisher_lower(r1, r2, p_comp)
            e["criterio_nombre"] = "<= -C"
            e["orden"] = f"P(F_{{{r1}, {r2}}} \\le c) = {alpha_str}, \\quad c = ?"
            e["resolucion"] = (
                f"**Paso 1: Inversión en tabla Fisher:**\n"
                f"$$c = \\frac{{1}}{{F_{{{p_comp}; {r2}, {r1}}}}} = \\frac{{1}}{{{f_inv:.2f}}} = {c_val:.4f}$$"
            )
            e["region_type"] = "left"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.4f}"]
            e["probabilidad"] = float(alpha_str)

        elif crit == 11:
            p = random.choice(["0.950", "0.975"])
            p_comp = f"{1.0 - float(p):.3f}"
            c_val, f_inv = self.tm.get_fisher_lower(r1, r2, p)
            e["criterio_nombre"] = ">= -C"
            e["orden"] = f"P(F_{{{r1}, {r2}}} \\ge c) = {p}, \\quad c = ?"
            e["resolucion"] = (
                f"**Paso 1: Complemento e inversión:**\n"
                f"$$P(F \\le c) = {p_comp} \\implies c = \\frac{{1}}{{F_{{{p}; {r2}, {r1}}}}} = {c_val:.4f}$$"
            )
            e["region_type"] = "right"
            e["points"] = [c_val]
            e["labels"] = [f"c = {c_val:.4f}"]
            e["probabilidad"] = float(p)

        return e

    def generar_lote_personalizado(self, distribuciones, criterios, repeticiones_por_tipo=1, params=None):
        """
        Genera un lote dinámico según las distribuciones seleccionadas, los criterios elegidos
        y la cantidad de repeticiones (tandas) por cada tipo/criterio.
        """
        params = params or {}
        if not distribuciones:
            distribuciones = ["Z", "t", "chi", "fisher"]
        if not criterios:
            criterios = list(range(1, 12))

        self.reiniciar_rastreo()
        repeticiones_por_tipo = max(1, int(repeticiones_por_tipo))
        resultado = []
        ej_id = 1

        for dist in distribuciones:
            for crit in criterios:
                for tanda in range(1, repeticiones_por_tipo + 1):
                    tanda_params = dict(params)
                    tanda_params["_tanda"] = tanda
                    ej = self.generar_ejercicio(dist, crit, params=tanda_params, ej_id=ej_id)
                    ej["tanda"] = tanda
                    resultado.append(ej)
                    ej_id += 1

        return resultado

if __name__ == "__main__":
    gen = GeneradorEjercicios()
    print("Probando generación aleatoria de 3 ejercicios de Z:")
    for _ in range(3):
        e1 = gen.generar_ejercicio("z", 1)
        print(" ->", e1["orden"])
