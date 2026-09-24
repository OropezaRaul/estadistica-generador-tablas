"""
Compilador Dinámico de Documentos PDF en ReportLab.
Permite compilar guías de ejercicios personalizadas de cualquier tamaño y distribución:
- Portada institucional.
- Secciones analíticas con formato riguroso.
- Cada ejercicio incluye:
  1. Orden del ejercicio estructurada
  2. Resolución analítica detallada paso a paso citando las tablas oficiales
  3. Gráfico teórico sombreado incrustado
- Numeración correlativa 'Página X de Y' con NumberedCanvas.
- Exportación organizada a la carpeta 'Resultados/' con numeración secuencial
  distinguiendo entre 'Completo' y 'Parcial'.
"""
import os
import re
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
    en la carpeta Resultados/ con nombre correlativo y descriptivo.
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

    story = []

    # Portada
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
        f"• Documento exportado automáticamente a la carpeta <code>Resultados/</code>."
    )
    story.append(Paragraph(meta_p, style_body))
    story.append(PageBreak())

    # Ejercicios
    for idx, ej in enumerate(ejercicios):
        ej_id = ej.get("id", idx + 1)
        crit_nom = ej.get("criterio_nombre", "")
        dist_nom = ej.get("distribucion", "")
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

    doc.build(story, canvasmaker=NumberedCanvas)
    return nombre_archivo
