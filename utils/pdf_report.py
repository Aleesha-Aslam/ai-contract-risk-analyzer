from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io

def generate_pdf_report(
    filename,
    risk_score,
    risk_level,
    keywords,
    category_scores,
    ai_analysis,
    summary,
    entities
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Colors ──
    purple     = colors.HexColor("#6366f1")
    dark_bg    = colors.HexColor("#0f1117")
    red        = colors.HexColor("#f85149")
    yellow     = colors.HexColor("#d29922")
    green      = colors.HexColor("#3fb950")
    light_gray = colors.HexColor("#e6edf3")
    mid_gray   = colors.HexColor("#8b949e")

    risk_color = red if risk_level == "HIGH" else yellow if risk_level == "MEDIUM" else green

    # ── Custom Styles ──
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=24,
        fontName="Helvetica-Bold",
        textColor=purple,
        alignment=TA_CENTER,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica",
        textColor=mid_gray,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=14,
        fontName="Helvetica-Bold",
        textColor=purple,
        spaceBefore=16,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#1c2128"),
        spaceAfter=6,
        leading=16
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        textColor=mid_gray,
        spaceAfter=4
    )

    # ── Header ──
    elements.append(Paragraph("⚖️ AI Contract Risk Analyzer", title_style))
    elements.append(Paragraph("Automated Legal Contract Analysis Report", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=purple))
    elements.append(Spacer(1, 16))

    # ── Overall Risk Score ──
    elements.append(Paragraph("📊 Overall Risk Assessment", section_style))

    score_data = [
        ["Risk Score", "Risk Level", "Status"],
        [
            f"{risk_score}/100",
            risk_level,
            "⚠️ Review Required" if risk_level == "HIGH" else "⚡ Caution Advised" if risk_level == "MEDIUM" else "✅ Relatively Safe"
        ]
    ]
    score_table = Table(score_data, colWidths=[150, 150, 200])
    score_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  purple),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  11),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",   (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
        ("TEXTCOLOR",    (0, 1), (0, 1),   risk_color),
        ("TEXTCOLOR",    (1, 1), (1, 1),   risk_color),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 1), (0, 1),   20),
        ("FONTSIZE",     (1, 1), (1, 1),   14),
        ("ROWBACKGROUND",(0, 1), (-1, -1), [colors.HexColor("#f8f9fa")]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
        ("ROWHEIGHT",    (0, 0), (-1, -1), 35),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 12))

    # ── Category Scores ──
    if category_scores:
        elements.append(Paragraph("📋 Category Score Breakdown", section_style))

        cat_data = [["Category", "Score", "Risk Level"]]
        for cat, data in category_scores.items():
            cat_color = colors.HexColor("#f85149") if data["level"] == "HIGH" else \
                        colors.HexColor("#d29922") if data["level"] == "MEDIUM" else \
                        colors.HexColor("#3fb950")
            cat_data.append([cat, f"{data['score']}/100", f"{data['emoji']} {data['level']}"])

        cat_table = Table(cat_data, colWidths=[220, 100, 150])
        cat_style = [
            ("BACKGROUND",   (0, 0), (-1, 0),  purple),
            ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, 0),  11),
            ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
            ("ALIGN",        (0, 1), (0, -1),  "LEFT"),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
            ("ROWHEIGHT",    (0, 0), (-1, -1), 28),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ("LEFTPADDING",  (0, 0), (0, -1),  10),
        ]
        for i, (cat, data) in enumerate(category_scores.items(), start=1):
            bg = colors.HexColor("#fff8f8") if data["level"] == "HIGH" else \
                 colors.HexColor("#fffbf0") if data["level"] == "MEDIUM" else \
                 colors.HexColor("#f0fff4")
            cat_style.append(("BACKGROUND", (0, i), (-1, i), bg))
            text_color = colors.HexColor("#f85149") if data["level"] == "HIGH" else \
                         colors.HexColor("#d29922") if data["level"] == "MEDIUM" else \
                         colors.HexColor("#3fb950")
            cat_style.append(("TEXTCOLOR", (1, i), (2, i), text_color))
            cat_style.append(("FONTNAME",  (1, i), (2, i), "Helvetica-Bold"))

        cat_table.setStyle(TableStyle(cat_style))
        elements.append(cat_table)
        elements.append(Spacer(1, 12))

    # ── Keywords ──
    elements.append(Paragraph("🔍 Risk Keywords Detected", section_style))

    if keywords["high"]:
        elements.append(Paragraph("🔴 High Risk:", ParagraphStyle("Red", parent=body_style, textColor=red, fontName="Helvetica-Bold")))
        elements.append(Paragraph(", ".join(keywords["high"]), body_style))

    if keywords["medium"]:
        elements.append(Paragraph("🟡 Medium Risk:", ParagraphStyle("Yellow", parent=body_style, textColor=yellow, fontName="Helvetica-Bold")))
        elements.append(Paragraph(", ".join(keywords["medium"]), body_style))

    if keywords["low"]:
        elements.append(Paragraph("🟢 Low Risk:", ParagraphStyle("Green", parent=body_style, textColor=green, fontName="Helvetica-Bold")))
        elements.append(Paragraph(", ".join(keywords["low"]), body_style))

    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d7de")))

    # ── Summary ──
    if summary:
        elements.append(Paragraph("📄 Contract Summary", section_style))
        clean_summary = summary.replace("\n", "<br/>")
        elements.append(Paragraph(clean_summary, body_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d7de")))

    # ── AI Analysis ──
    if ai_analysis:
        elements.append(Paragraph("🤖 AI Risk Analysis", section_style))
        clean_analysis = ai_analysis.replace("\n", "<br/>")
        elements.append(Paragraph(clean_analysis, body_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d7de")))

    # ── Entities ──
    if entities and any(len(v) > 0 for v in entities.values()):
        elements.append(Paragraph("🏷️ Extracted Entities", section_style))
        for label, items in entities.items():
            if items:
                elements.append(Paragraph(f"<b>{label}:</b> {', '.join(items)}", body_style))

    # ── Footer ──
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=purple))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "Generated by ⚖️ AI Contract Risk Analyzer | For educational purposes only",
        ParagraphStyle("Footer", parent=small_style, alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer