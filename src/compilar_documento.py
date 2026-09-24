"""
Compilador Dinámico de Documentos PDF en ReportLab con Índice Interactivo y Marcadores.
Permite compilar guías de ejercicios personalizadas de cualquier tamaño y distribución:
- Portada institucional.
- Índice General Interactivo con enlaces clicables directos a cada tabla/distribución.
- Marcadores de navegación nativos del visor PDF (TOC / Outlines).
- Cada ejercicio incluye:
  1. Orden del ejercicio estructurada
  2. Resolución analítica detallada paso a paso citando las tablas oficiales
  3. Gráfico teórico sombreado incrustado
- Numeración correlativa 'Página X de Y' con NumberedCanvas.
- Exportación organizada a la carpeta 'Resultados/' con numeración secuencial.
"""
import os
import re
import pymupdf
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTADOS_DIR = os.path.join(BASE_DIR, "Resultados")
DEFAULT_GRAFICOS_DIR = os.path.join(BASE_DIR, "graficos")

try:
    from .generador_graficos import renderizar_grafico
except ImportError:
    from generador_graficos import renderizar_grafico

def generar_nombre_salida(es_completo, dist="VARIADO", cantidad=176, output_dir=RESULTADOS_DIR):
    """
    Genera un nombre de archivo correlativo y ordenado dentro de Resultados/:
    - 001_Completo_176_Ejercicios_Estadistica.pdf
    - 002_Parcial_FISHER_5_Ejercicios.pdf
    - 003_Parcial_Z_10_Ejercicios.pdf
    """
    os.makedirs(output_dir, exist_ok=True)
    existing = [f for f in os.listdir(output_dir) if f.endswith(".pdf")]
    next_num = 1
    for f in existing:
        m = re.match(r"^(\d+)_", f)
        if m:
            next_num = max(next_num, int(m.group(1)) + 1)
            
    prefix = f"{next_num:03d}"
    if es_completo or cantidad >= 176:
        filename = f"{prefix}_Completo_176_Ejercicios_Estadistica.pdf"
    else:
        dist_tag = str(dist).upper() if dist else "VARIADO"
        filename = f"{prefix}_Parcial_{dist_tag}_{cantidad}_Ejercicios.pdf"
    return os.path.join(output_dir, filename)

class NumberedCanvas(canvas.Canvas):
    """
    Canvas de doble pasada para calcular el número total de páginas (Página X de Y)
    e imprimir encabezados y pies de página profesionales.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#6c757d"))
            
            # Encabezado superior
            self.drawString(40, 755, "GUÍA DE PROBABILIDAD Y ESTADÍSTICA • TABLAS OFICIALES")
            self.setStrokeColor(colors.HexColor("#dee2e6"))
            self.setLineWidth(0.6)
            self.line(40, 748, 572, 748)
            
            # Pie de página inferior
            self.line(40, 42, 572, 42)
            self.drawString(40, 30, "Generado con el Sistema Automatizado de Tablas Oficiales")
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(572, 30, page_text)
            self.restoreState()

def convert_to_reportlab_html(text):
    """
    Convierte sintaxis matemática y markdown básico en etiquetas XML compatibles con ReportLab.
    """
    def repl_disp(m):
        eq = m.group(1)
        return f'<font color="#1d3557"><b>{eq}</b></font>'
    text = re.sub(r"\$\$(.*?)\$\$", repl_disp, text, flags=re.DOTALL)
    
    def repl_inline(m):
        eq = m.group(1)
        return f"<i>{eq}</i>"
    text = re.sub(r"\$(.*?)\$", repl_inline, text)

    text = text.replace(r"\le", "≤").replace(r"\ge", "≥")
    text = text.replace(r"\chi^2", "χ²").replace(r"\chi", "χ")
    text = text.replace(r"\alpha", "α").replace(r"\Phi", "Φ")
    text = text.replace(r"\sim", "~")
    text = text.replace(r"\mathcal{N}", "N").replace(r"\mathcal{F}", "F")
    text = text.replace(r"\quad", " &nbsp; ")
    text = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1 / \2)", text)
    text = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", text)
    text = re.sub(r"_([0-9a-zA-Z])", r"<sub>\1</sub>", text)
    text = re.sub(r"\^\{([^}]+)\}", r"<sup>\1</sup>", text)
    text = re.sub(r"\^([0-9a-zA-Z])", r"<sup>\1</sup>", text)
    text = text.replace("{", "").replace("}", "").replace("\\", "")

    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r'<font color="#0d6efd"><b>\1</b></font>', text)
    text = text.replace("\n", "<br/>")
    return text

def compilar_guia_pdf(ejercicios, nombre_archivo=None, titulo=None, subtitulo=None, dist_tag="VARIADO"):
    """
    Compila un documento PDF con cualquier lista de ejercicios y lo almacena por defecto
    en la carpeta Resultados/ con nombre correlativo y descriptivo, incorporando un
    Índice Interactivo clicable y marcadores nativos en el lector de PDF.
    """
    es_completo = len(ejercicios) >= 176
    if not nombre_archivo:
        nombre_archivo = generar_nombre_salida(es_completo, dist=dist_tag, cantidad=len(ejercicios))
        
    os.makedirs(os.path.dirname(os.path.abspath(nombre_archivo)), exist_ok=True)
    os.makedirs(DEFAULT_GRAFICOS_DIR, exist_ok=True)

    if not titulo:
        titulo = "GUÍA COMPLETA DE EJERCICIOS RESUELTOS" if es_completo else f"GUÍA PRÁCTICA DE EJERCICIOS RESUELTOS"
    if not subtitulo:
        subtitulo = "176 Problemas de Probabilidad y Estadística Inferencial" if es_completo else f"Lote Seleccionado de {len(ejercicios)} Ejercicios Analíticos"
    
    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=48,
        bottomMargin=48
    )
    
    styles = getSampleStyleSheet()
    
    style_cover_badge = ParagraphStyle(
        "CoverBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#457b9d"),
        alignment=1,
        spaceAfter=15
    )
    style_cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1d3557"),
        alignment=1,
        spaceAfter=12
    )
    style_cover_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2b2d42"),
        alignment=1,
        spaceAfter=25
    )
    style_body = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=12.2,
        textColor=colors.HexColor("#212529")
    )
    style_h2 = ParagraphStyle(
        "Header2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1d3557"),
        spaceBefore=8,
        spaceAfter=5
    )
    style_ej_header = ParagraphStyle(
        "EjHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=colors.white
    )
    style_orden = ParagraphStyle(
        "OrdenText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1d3557")
    )
    style_toc_title = ParagraphStyle(
        "TocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1d3557"),
        alignment=1,
        spaceAfter=10
    )
    style_toc_desc = ParagraphStyle(
        "TocDesc",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#4b5563"),
        alignment=1,
        spaceAfter=20
    )

    story = []

    # =========================================================================
    # 1. PORTADA
    # =========================================================================
    story.append(Spacer(1, 35))
    story.append(Paragraph("ESTADÍSTICA E INGENIERÍA • TABLAS OFICIALES", style_cover_badge))
    story.append(Paragraph(titulo, style_cover_title))
    story.append(Paragraph(subtitulo, style_cover_subtitle))
    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#e63946"), spaceAfter=25))
    
    meta_p = (
        f"<b>Resumen del Documento:</b><br/>"
        f"• Total de ejercicios incluidos: <b>{len(ejercicios)}</b><br/>"
        f"• Resolución analítica rigurosa citando coordenadas de la tabla oficial.<br/>"
        f"• Gráficas teóricas con áreas de probabilidad sombreadas y puntos críticos señalados.<br/>"
        f"• Incluye <b>Índice Interactivo</b> y marcadores para navegación rápida entre tablas.<br/>"
        f"• Documento exportado automáticamente a la carpeta <code>Resultados/</code>."
    )
    story.append(Paragraph(meta_p, style_body))
    story.append(PageBreak())

    # =========================================================================
    # 2. ÍNDICE GENERAL INTERACTIVO (PÁGINA 2)
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("ÍNDICE GENERAL INTERACTIVO", style_toc_title))
    story.append(Paragraph("Haz clic en cualquier sección para saltar directamente al inicio de sus ejercicios:", style_toc_desc))

    # Analizar qué distribuciones y rangos de ejercicios están presentes en el lote
    dist_nombres = {
        "z": ("NORMAL ESTÁNDAR", "Normal Estándar Z ~ N(0, 1)"),
        "t": ("t-STUDENT", "t-Student T ~ t(r)"),
        "chi": ("CHI-CUADRADO", "Chi-cuadrado X ~ χ²(r)"),
        "fisher": ("FISHER-SNEDECOR", "Fisher-Snedecor F ~ F(r₁, r₂)")
    }

    secciones_info = []
    current_dist = None
    start_id = None
    prev_ej = None

    for i, ej in enumerate(ejercicios):
        d_type = ej.get("dist_type", "").lower()
        if d_type != current_dist:
            if current_dist is not None and prev_ej is not None:
                short_name, full_name = dist_nombres.get(current_dist, (current_dist.upper(), current_dist.upper()))
                secciones_info.append({
                    "dist_type": current_dist,
                    "search_key": short_name,
                    "nombre": full_name,
                    "start_id": start_id,
                    "end_id": prev_ej.get("id", i),
                    "count": (prev_ej.get("id", i) - start_id + 1)
                })
            current_dist = d_type
            start_id = ej.get("id", i + 1)
        prev_ej = ej

    if current_dist is not None and prev_ej is not None:
        short_name, full_name = dist_nombres.get(current_dist, (current_dist.upper(), current_dist.upper()))
        secciones_info.append({
            "dist_type": current_dist,
            "search_key": short_name,
            "nombre": full_name,
            "start_id": start_id,
            "end_id": prev_ej.get("id", len(ejercicios)),
            "count": (prev_ej.get("id", len(ejercicios)) - start_id + 1)
        })

    # Construir filas de la tabla de índice
    toc_table_data = []
    for num_sec, s in enumerate(secciones_info, start=1):
        col_left = (
            f"<b>{num_sec}. SECCIÓN: {s['search_key']}</b><br/>"
            f"<font color='#6b7280'>{s['nombre']} &bull; Ejercicios {s['start_id']} al {s['end_id']} ({s['count']} problemas)</font>"
        )
        col_right = "<font color='#0d6efd'><b>[Ir a los ejercicios &rarr;]</b></font>"
        toc_table_data.append([
            Paragraph(col_left, style_body),
            Paragraph(col_right, style_body)
        ])

    t_toc = Table(toc_table_data, colWidths=[400, 132])
    t_toc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 25))
    
    nota_navegacion = (
        "<i>Nota de Navegación:</i> Además de los enlaces en este índice, el documento incluye "
        "<b>marcadores de esquema PDF nativos</b> (Bookmarks) disponibles en la barra lateral izquierda "
        "de tu lector de PDF (Chrome, Edge, Adobe Reader, etc.) para saltar entre tablas desde cualquier página."
    )
    story.append(Paragraph(nota_navegacion, style_body))
    story.append(PageBreak())

    # =========================================================================
    # 3. EJERCICIOS
    # =========================================================================
    dist_actual_ej = None

    for idx, ej in enumerate(ejercicios):
        ej_id = ej.get("id", idx + 1)
        crit_nom = ej.get("criterio_nombre", "")
        dist_nom = ej.get("distribucion", "")
        d_type = ej.get("dist_type", "").lower()

        # Banner de inicio de sección para el primer ejercicio de cada distribución
        if d_type != dist_actual_ej:
            dist_actual_ej = d_type
            short_name, full_name = dist_nombres.get(d_type, (d_type.upper(), d_type.upper()))
            banner_text = f"<b>INICIO DE SECCIÓN: {short_name}</b> &bull; {full_name}"
            t_banner = Table([[Paragraph(banner_text, style_ej_header)]], colWidths=[532])
            t_banner.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(t_banner)
            story.append(Spacer(1, 4))

        # Encabezado del ejercicio
        header_text = f"<b>EJERCICIO {ej_id}:</b> {dist_nom}" + (f" &nbsp;|&nbsp; <b>Caso:</b> {crit_nom}" if crit_nom else "")
        t_header = Table([[Paragraph(header_text, style_ej_header)]], colWidths=[532])
        t_header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1d3557")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t_header)
        story.append(Spacer(1, 6))

        # 1. Orden
        orden_html = convert_to_reportlab_html(f"<b>1. Orden del ejercicio:</b> &nbsp; {ej['orden']}")
        t_orden = Table([[Paragraph(orden_html, style_orden)]], colWidths=[532])
        t_orden.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#edf2f4")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#8d99ae")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(t_orden)
        story.append(Spacer(1, 8))

        # 2. Resolución
        story.append(Paragraph("<b>2. Resolución analítica del ejercicio:</b>", style_h2))
        res_html = convert_to_reportlab_html(ej["resolucion"])
        story.append(Paragraph(res_html, style_body))
        story.append(Spacer(1, 8))

        # 3. Gráfica
        story.append(Paragraph("<b>3. Gráfico de la distribución y región evaluada:</b>", style_h2))
        img_path = ej.get("grafico_path")
        if not img_path or not os.path.exists(img_path):
            img_path = renderizar_grafico(ej, output_dir=DEFAULT_GRAFICOS_DIR)
            ej["grafico_path"] = img_path
            
        if os.path.exists(img_path):
            img = RLImage(img_path, width=4.4 * inch, height=2.27 * inch)
            img.hAlign = "CENTER"
            story.append(img)

        story.append(PageBreak())

    # Compilación ReportLab
    doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # 4. POST-PROCESAMIENTO CON PyMuPDF (ENLACES CLICABLES Y MARCADORES)
    # =========================================================================
    try:
        pdf = pymupdf.open(nombre_archivo)
        
        # Detectar la página exacta donde inicia cada sección
        section_start_pages = {}
        for p_idx, page in enumerate(pdf):
            txt = page.get_text()
            for s in secciones_info:
                key = s["search_key"]
                if key not in section_start_pages and f"INICIO DE SECCIÓN: {key}" in txt:
                    section_start_pages[key] = p_idx  # 0-indexed

        # Página 2 (Índice): p_idx = 1
        if len(pdf) >= 2:
            page_indice = pdf[1]
            for s in secciones_info:
                key = s["search_key"]
                if key in section_start_pages:
                    target_page_idx = section_start_pages[key]
                    rects = page_indice.search_for(key)
                    if rects:
                        r = rects[0]
                        # Rectángulo clicable que cubre toda la fila de la tabla
                        click_rect = pymupdf.Rect(40, r.y0 - 6, 572, r.y1 + 18)
                        page_indice.insert_link({
                            "kind": pymupdf.LINK_GOTO,
                            "from": click_rect,
                            "page": target_page_idx
                        })

        # Construir Outline / Marcadores laterales del PDF
        toc_outline = [
            [1, "Portada", 1],
            [1, "Índice General Interactivo", 2]
        ]
        for s in secciones_info:
            key = s["search_key"]
            if key in section_start_pages:
                pg_num = section_start_pages[key] + 1  # 1-indexed para PyMuPDF TOC
                toc_outline.append([1, f"Sección: {s['nombre']} (Ej. {s['start_id']} al {s['end_id']})", pg_num])

        pdf.set_toc(toc_outline)
        
        # Guardar en archivo temporal e intercambiar para escritura segura
        temp_out = nombre_archivo + ".tmp"
        pdf.save(temp_out)
        pdf.close()
        os.replace(temp_out, nombre_archivo)
        print(f" -> Enlaces interactivos y marcadores agregados exitosamente en '{nombre_archivo}'.")

    except Exception as ex:
        print(f"Aviso durante post-procesamiento de enlaces: {ex}")

    return nombre_archivo

if __name__ == "__main__":
    from generador_ejercicios import GeneradorEjercicios
    gen = GeneradorEjercicios()
    print("Probando compilación con Índice Interactivo...")
    ej_list = gen.generar_lote_personalizado(["z", "t"], [1, 2], repeticiones_por_tipo=2)
    out = compilar_guia_pdf(ej_list, titulo="GUÍA DE PRUEBA CON ÍNDICE")
    print("PDF generado con éxito en:", out)
