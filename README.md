# 📊 Sistema Estadístico Interactivo: Generador, Resolvedor & Tablas Oficiales

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plataforma abierta y universal para estudiantes y profesores de **Probabilidad y Estadística**. Permite generar lotes personalizados de ejercicios con sus desarrollos paso a paso y gráficas teóricas, resolver ejercicios propios con datos de clase y generar únicamente las curvas de densidad sombreadas a partir de las tablas estadísticas oficiales:
- **Normal Estándar:** $Z \sim \mathcal{N}(0, 1)$
- **t-Student:** $T \sim t(r)$
- **Chi-cuadrado:** $X \sim \chi^2(r)$
- **Fisher-Snedecor:** $F \sim F(r_1, r_2)$

**100% ejecutable desde la Interfaz Web:** Todas las funciones del sistema (generación personalizada, resolución puntual, exportación de gráficas, visor de tablas y compilación de la guía completa de 176 ejercicios) están integradas en la aplicación web.

---

## ⚡ Inicio Rápido con 1 Clic (Sin Comandos)

### 🪟 En Windows (Doble Clic):
Simplemente haz **doble clic en el archivo `iniciar_windows.bat`**:
1. Detecta automáticamente tu instalación de Python.
2. Si es la primera vez, configura automáticamente el entorno virtual local `.venv` e instala las librerías necesarias.
3. Inicia el servidor local y **abre automáticamente tu navegador web predeterminado** (Chrome, Edge, Firefox, Brave, Opera, etc.).

### 🐧 En Linux / macOS (Doble Clic o Terminal):
Haz doble clic en `iniciar_linux.sh` o ejecuta en tu terminal:
```bash
./iniciar_linux.sh
```
*(O directamente con el entorno virtual: `.venv/bin/python app.py`)*. Se abrirá automáticamente en tu navegador predeterminado en `http://127.0.0.1:5000`.

---

## 🌟 Todas las Funciones desde la Interfaz Web

Al abrir la aplicación, dispones de 3 pestañas principales:

### 1. 🎲 Pestaña "Generador de Ejercicios"
- **Generación Personalizada:**
  - Elige la distribución ($Z$, $t$, $\chi^2$ o $F$).
  - Selecciona qué criterios analíticos de los 11 deseas incluir (o usa atajos rápidos: *Colas directas*, *Intervalos*, *Inversas* o *Todos*).
  - Define la cantidad exacta a generar (ej. 3, 5, 10, etc.).
  - Muestra tarjetas interactivas con la **orden matemática**, la **resolución paso a paso citando la tabla** y la **gráfica teórica sombreada** con botón de descarga PNG.
  - **Botón "Descargar Guía en PDF":** Compila y descarga al instante un PDF con ReportLab solo con los ejercicios generados.
- **⚡ Botón "Generar Guía Completa (176 Ejercicios)":**
  - Con un solo clic compila y descarga el catálogo oficial completo (4 tandas × 11 criterios × 4 distribuciones) con portada y gráficos incrustados.

### 2. ⚡ Pestaña "Resolvedor & Gráficos" (Para tus Propios Ejercicios)
- Introduce cualquier ejercicio que ya tengas propuesto.
- **Tres modalidades según tu necesidad:**
  - **Completo:** Obtén la orden estructurada, la resolución analítica paso a paso y la gráfica sombreada.
  - **Solo Gráfico:** Ideal si ya tienes el cálculo hecho en papel y solo necesitas la curva de densidad sombreada con los puntos críticos señalados para pegarla en tu informe.
  - **Solo Resolución:** Comprueba tu procedimiento analítico citando la fila y columna exacta de la tabla.

### 3. 📖 Pestaña "Tablas Oficiales"
- Explora interactivamente las matrices numéricas oficiales de Normal Estándar, t-Student, Chi-cuadrado y los 4 niveles de significancia de Fisher ($0.950$, $0.975$, $0.990$, $0.995$) con cabeceras fijas.

---

## 📂 Organización de Salidas en `Resultados/` y Protección Git

Todos los documentos PDF generados se exportan de forma ordenada y secuencial a la carpeta `Resultados/`:
- `001_Completo_176_Ejercicios_Estadistica.pdf` (guías completas).
- `002_Parcial_FISHER_3_Ejercicios.pdf` (lotes parciales).
- `003_Parcial_Z_5_Ejercicios.pdf`

> **Nota para Git:** Las carpetas `Resultados/` y `graficos/` están incluidas en `.gitignore`. Puedes generar todos los ejercicios, imágenes y PDFs que quieras; **tus resultados personales se mantendrán seguros en tu disco local** y nunca interferirán al hacer `git pull` o `git push`.

---

## 📁 Estructura del Repositorio

```text
.
├── iniciar_windows.bat            # Lanzador con doble clic para Windows
├── iniciar_linux.sh               # Lanzador con doble clic/terminal para Linux y macOS
├── app.py                         # Servidor local Flask (auto-abre navegador predeterminado)
├── resolver.py                    # Resolvedor de ejercicios por consola (CLI alternativo)
├── main.py                        # Lanzador general multi-modo
├── requirements.txt               # Dependencias del proyecto
├── .gitignore                     # Protege .venv, Resultados/ y graficos/
├── README.md                      # Documentación completa
│
├── Resultados/                    # Carpeta de exportación de PDFs (.gitkeep)
├── graficos/                      # Carpeta de salida para imágenes PNG (.gitkeep)
│
├── data/                          # Tablas numéricas puras en JSON
│   ├── tabla_z.json
│   ├── tabla_t.json
│   ├── tabla_chi.json
│   └── tabla_fisher.json
│
├── docs/                          # Tablas PDF oficiales originales
│   ├── TablasEstadisticasZTStudentChicuadrado.pdf
│   └── TablaFisher.pdf
│
├── src/                           # Código fuente del sistema
│   ├── compilar_documento.py      # Compilador dinámico de PDF ReportLab
│   ├── extraer_tablas.py          # Extractor e inspector de tablas
│   ├── generador_ejercicios.py    # Motor generador dinámico de ejercicios
│   ├── generador_graficos.py      # Motor gráfico Matplotlib (PNG y Base64)
│   ├── resolver_personalizado.py  # Reconocedor de patrones analíticos
│   └── tablas_manager.py          # Gestor de consultas e indexación
│
├── static/                        # Frontend web (Vanilla CSS y JS)
│   ├── css/style.css
│   └── js/app.js
│
└── templates/
    └── index.html                 # Interfaz gráfica de usuario
```

---

## 📐 Los 11 Criterios Analíticos Soportados

| # | Criterio | Descripción | Distribuciones Simétricas ($Z$ y $t$) | Chi-cuadrado y Fisher (Soporte $\ge 0$) |
|---|---|---|---|---|
| **1** | `<= +` | Cola izquierda positiva | $P(X \le a) = \text{Tabla}(a)$ | Percentil superior directo |
| **2** | `<= -` | Cola izquierda negativa | $P(X \le -a) = 1 - P(X \le a)$ | Percentil bajo tabulado o inversión |
| **3** | `>= +` | Cola derecha positiva | $P(X \ge a) = 1 - P(X \le a)$ | Complemento en cuantil alto |
| **4** | `>= -` | Cola derecha negativa | $P(X \ge -a) = P(X \le a)$ | Complemento en cuantil bajo |
| **5** | `+ <= <= +` | Intervalo positivo | $P(Z \le b) - P(Z \le a)$ | Resta de cuantiles superiores |
| **6** | `- <= <= +` | Intervalo asimétrico | $P(Z \le b) - [1 - P(Z \le a)]$ | Intervalo entre cuantil inferior y superior |
| **7** | `- <= <= -` | Intervalo negativo | $P(Z \le a) - P(Z \le b)$ | Resta de cuantiles inferiores |
| **8** | `<= C` | Inversa cola izquierda | Dado $P(X \le c) = p \to c > 0$ | Búsqueda directa en cuantil superior |
| **9** | `>= C` | Inversa cola derecha | Dado $P(X \ge c) = p \to c > 0$ | Complemento $P(X \le c) = 1 - p$ |
| **10** | `<= -C` | Inversa cuantil bajo | $P(X \le k) = 1 - p \to c = -k$ | Búsqueda en cuantil bajo o por inversión |
| **11** | `>= -C` | Inversa cuantil bajo | $P(X \le k) = p \to c = -k$ | Complemento + cuantil bajo o inversión |

### 📌 Notas Técnicas
- **Propiedad de Inversión de Fisher:** Para calcular percentiles inferiores en Fisher se utiliza la propiedad oficial de la tabla:
  $$F_{\alpha; r_1, r_2} = \frac{1}{F_{1-\alpha; r_2, r_1}}$$
- **Notación Homogénea:** Se utiliza la notación estándar directa $P(X \le x)$ en todo el sistema para garantizar la máxima comprensión en el estudio compartido.

---

## 📤 Cómo Subir el Repositorio a GitHub

1. En tu cuenta de [GitHub](https://github.com/new), crea un nuevo repositorio (por ejemplo `estadistica-generador-tablas`).
2. En tu terminal ejecuta:
```bash
git add .
git commit -m "feat: plataforma estadistica interactiva web con lanzador 1-clic y exportador ordenado"
git branch -M main
git remote add origin https://github.com/OropezaRaul/estadistica-generador-tablas.git
git push -u origin main
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Libre para compartir, extender y usar con fines académicos.
