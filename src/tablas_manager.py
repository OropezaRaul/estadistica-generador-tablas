"""
Módulo de Gestión y Consulta de Tablas Estadísticas Oficiales.
Permite realizar búsquedas directas e inversas exactas sobre las 4 distribuciones:
- Normal Estándar Z ~ N(0, 1)
- t-Student T ~ t(r)
- Chi-cuadrado X ~ Chi^2(r)
- Fisher F ~ F(r1, r2)
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

class TablasManager:
    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        self.tabla_z = self._cargar_json("tabla_z.json")
        self.tabla_t = self._cargar_json("tabla_t.json")
        self.tabla_chi = self._cargar_json("tabla_chi.json")
        self.tabla_fisher = self._cargar_json("tabla_fisher.json")
        
        # Índices inversos para optimizar búsquedas rápidas y exactas
        self._build_indices()

    def _cargar_json(self, nombre_archivo):
        # Primero intenta en data_dir, luego en raíz por retrocompatibilidad
        p1 = os.path.join(self.data_dir, nombre_archivo)
        p2 = os.path.join(BASE_DIR, nombre_archivo)
        ruta = p1 if os.path.exists(p1) else p2
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo de tabla: {ruta}")
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_indices(self):
        # Índice inverso para Z: prob -> (z, row_key, col_key)
        self.z_inv_map = {}
        for r_key, cols in self.tabla_z.items():
            for c_key, prob in cols.items():
                z_val = round(float(r_key) + float(c_key), 2)
                self.z_inv_map[round(prob, 4)] = (z_val, r_key, c_key)

    # ------------------ MÉTODOS NORMAL ESTÁNDAR Z ------------------
    def get_z(self, z_val):
        """
        Retorna (probabilidad, row_key, col_key) para un z >= 0 dado.
        """
        z_abs = round(abs(z_val), 2)
        if z_abs > 3.49:
            z_abs = 3.49
        row_val = int(z_abs * 10) / 10.0
        row_key = f"{row_val:.1f}"
        col_val = round(z_abs - row_val, 2)
        col_key = f"{col_val:.2f}"
        
        prob = self.tabla_z[row_key][col_key]
        return prob, row_key, col_key

    def find_z_inverse(self, target_prob):
        """
        Dada una probabilidad target_prob in (0.5, 1.0), busca el z más cercano en la tabla.
        Retorna (z_val, prob_encontrada, row_key, col_key).
        """
        target = round(target_prob, 4)
        if target in self.z_inv_map:
            z_val, r_k, c_k = self.z_inv_map[target]
            return z_val, target, r_k, c_k
        
        # Si no es exacto, buscamos el valor más próximo en la tabla
        best_diff = float("inf")
        best_match = None
        for prob, (z_val, r_k, c_k) in self.z_inv_map.items():
            diff = abs(prob - target)
            if diff < best_diff:
                best_diff = diff
                best_match = (z_val, prob, r_k, c_k)
        return best_match

    # ------------------ MÉTODOS t-STUDENT ------------------
    def get_t(self, df, p_str):
        """
        Retorna el valor crítico c = t_{p; df} tabulado para grados de libertad df y columna p_str.
        """
        df_key = str(df)
        if df_key not in self.tabla_t:
            raise KeyError(f"Grados de libertad {df} no encontrados en tabla t.")
        if p_str not in self.tabla_t[df_key]:
            raise KeyError(f"Nivel {p_str} no encontrado en tabla t para gl={df}.")
        return self.tabla_t[df_key][p_str]

    def get_t_available_dfs(self):
        return [int(k) if k != "inf" else "inf" for k in self.tabla_t.keys()]

    def get_t_available_probs(self):
        return ["0.750", "0.800", "0.900", "0.950", "0.975", "0.990", "0.995", "0.999", "0.9995", "0.9999"]

    # ------------------ MÉTODOS CHI-CUADRADO ------------------
    def get_chi(self, df, p_str):
        """
        Retorna el valor crítico c = chi^2_{p; df} tabulado.
        """
        df_key = str(df)
        if df_key not in self.tabla_chi:
            raise KeyError(f"Grados de libertad {df} no encontrados en tabla chi.")
        if p_str not in self.tabla_chi[df_key]:
            raise KeyError(f"Nivel {p_str} no encontrado en tabla chi para gl={df}.")
        return self.tabla_chi[df_key][p_str]

    def get_chi_available_dfs(self):
        return [int(k) for k in self.tabla_chi.keys()]

    def get_chi_lower_probs(self):
        return ["0.005", "0.010", "0.025", "0.050", "0.100"]

    def get_chi_upper_probs(self):
        return ["0.900", "0.950", "0.975", "0.990", "0.995"]

    # ------------------ MÉTODOS FISHER ------------------
    def get_fisher_upper(self, r1, r2, p_str):
        """
        Retorna el valor crítico directo de la tabla F_{p; r1, r2}.
        p_str in ['0.950', '0.975', '0.990', '0.995'].
        """
        if p_str not in self.tabla_fisher:
            raise KeyError(f"Nivel {p_str} no disponible en tabla Fisher.")
        r2_key = str(r2)
        r1_key = str(r1)
        if r2_key not in self.tabla_fisher[p_str]:
            raise KeyError(f"r2={r2} no disponible en nivel {p_str} de tabla Fisher.")
        if r1_key not in self.tabla_fisher[p_str][r2_key]:
            raise KeyError(f"r1={r1} no disponible en r2={r2}, nivel {p_str} de tabla Fisher.")
        return self.tabla_fisher[p_str][r2_key][r1_key]

    def get_fisher_lower(self, r1, r2, p_upper_str):
        """
        Calcula el percentil inferior por la propiedad de inversión:
        F_{alpha; r1, r2} = 1 / F_{1-alpha; r2, r1}
        donde p_upper_str es 1-alpha in ['0.950', '0.975', '0.990', '0.995'].
        Retorna (val_inferior, val_denominador_tabulado).
        """
        val_f_inv = self.get_fisher_upper(r1=r2, r2=r1, p_str=p_upper_str)
        val_lower = round(1.0 / val_f_inv, 4)
        return val_lower, val_f_inv

    def get_fisher_r1_list(self):
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 120]

    def get_fisher_r2_list(self):
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 60, 120, "inf"]

    def get_fisher_probs(self):
        return ["0.950", "0.975", "0.990", "0.995"]

if __name__ == "__main__":
    tm = TablasManager()
    print("TablasManager inicializado y probado con éxito desde data/.")
    print("Z(1.96):", tm.get_z(1.96))
    print("Z inv(0.9750):", tm.find_z_inverse(0.9750))
    print("t(df=10, 0.950):", tm.get_t(10, "0.950"))
    print("Chi(df=10, 0.950):", tm.get_chi(10, "0.950"))
    print("Fisher superior(r1=5, r2=10, 0.950):", tm.get_fisher_upper(5, 10, "0.950"))
    print("Fisher inferior(r1=5, r2=10, 0.950):", tm.get_fisher_lower(5, 10, "0.950"))
